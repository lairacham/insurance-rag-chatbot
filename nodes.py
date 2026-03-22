import os
import json
from state import ChatState
from helpers import _get_last_user_message, _chat, _ask_next_question, _chat_with_history
from rag import retrieve
from validators import validate_quote_data

def greet_node(state: ChatState) -> ChatState:
    """
    Greets the user and asks what they need.
    """
    if state.get("messages"): # already greeted, skip
        return state

    state["messages"] = state.get("messages", [])
    state["mode"] = "idle"
    state["quote_product"] = None
    state["quote_data"] = {}
    state["quote_step"] = None
    state["ask_again_flag"] = False
    state["question_in_middle_of_quote_flag"] = False
    state["quote_accepted"] = None

    greeting = (
        "Hi! I'm the ShieldBase Insurance assistant. I can help you with two things:\n"
        "1. Answer questions about our auto, home, and life insurance products.\n"
        "2. Generate a personalized insurance quote.\n\n"
        "What can I help you with today?"
    )
    
    state["messages"].append({ "role": "assistant", "content": greeting })


    return state

def question_or_quote_node(state: ChatState) -> ChatState:
    """
    Decides whether the user's message is a question or a quote request.
    """
    last_user_message = _get_last_user_message(state)

    if state.get("question_in_middle_of_quote_flag"):
        state["mode"] = "rag"
        return state

    if state.get("quote_step") == "confirm":
        state["mode"] = "confirm"
        return state
    
    if state.get("quote_accepted"):
        state["mode"] = "idle"
        state["quote_product"] = None
        state["quote_data"] = {}
        state["quote_step"] = None
        state["quote_result"] = None
        state["ask_again_flag"] = False
        state["question_in_middle_of_quote_flag"] = False
        state["quote_accepted"] = None

    
    if state.get("quote_accepted") == False:
        state["mode"] = "idle"
        state["quote_data"] = {}
        state["quote_step"] = "collect"
        state["quote_result"] = None
        state["ask_again_flag"] = False
        state["question_in_middle_of_quote_flag"] = False
        state["quote_accepted"] = None

        return state

    ACTIVE_COLLECTION_STEPS = ("collect", "generate")
    if state.get("quote_step") == "confirm":
        state["mode"] = "confirm"
        return state
    if state.get("quote_step") and state.get("quote_step") in ACTIVE_COLLECTION_STEPS:
        system_check = (
            "The user is mid-quote. Is their message a question about insurance, "
            "or an answer to a quote question?\n"
            "Return ONLY 'rag' or 'answer'.\n"
            "Examples:\n"
            "User: 28 -> answer\n"
            "User: what are included in home insurance? -> rag\n"
        )
        response = _chat(system_check, last_user_message).strip().lower()
        if response == "rag":
            state["question_in_middle_of_quote_flag"] = True
            state["mode"] = "rag"
        else:
            state["mode"] = "quote"

        return state
        
    if not last_user_message:
        state["mode"] = "idle"
        return state

    system = (
        "You are a helpful assistant that helps users with two things:\n"
        "1. Answer questions about insurance products.\n"
        "2. Generate insurance quotes (auto, home, or life insurance).\n\n"
        "Analyze the user's message and decide if it is a question or a quote request.\n"
        "Return 'rag' if it is a question, and 'quote' if it is a quote request.\n\n"
        "Examples:\n"
        "User: What is the difference between auto and home insurance? -> rag\n"
        "User: I want to get a quote for auto insurance. -> quote\n"
        "User: How much does auto insurance cost? -> quote\n"
        "User: What is the difference between auto and home insurance? -> rag\n"
    )

    mode = _chat(system, last_user_message).strip().lower()

    # If the model is not sure, default to rag
    state["mode"] = mode if mode in ("rag", "quote") else "rag"



    return state

def rag_node(state: ChatState) -> ChatState:
    """
    Retrieves relevant information from the knowledge base and generates a response.
    """
    last_user_message = _get_last_user_message(state)

    context = retrieve(last_user_message)

    history = [
        m for m in state["messages"]
        if m["role"] in ("user", "assistant")
    ]

    system = f"""You are a helpful assistant for ShieldBase Insurance.
Use ONLY the context below to answer the user's question.
If the answer is not in the context, say: "I don't have that information — please call us at 1-800-743-5527."
Be concise and friendly.

Context:
{"\n".join(context)}"""
    messages = [
        *history,
        {"role": "user", "content": last_user_message}
    ]
    answer = _chat_with_history(system, messages)
    state["messages"].append({ "role": "assistant", "content": answer })
    state["mode"] = "idle"

    # If we interrupted a quote flow, clear the flag and re-ask the pending question
    if state.get("question_in_middle_of_quote_flag"):
        state["question_in_middle_of_quote_flag"] = False
        state["ask_again_flag"] = False
        product = state.get("quote_product")
        data = state.get("quote_data", {})
        required = REQUIRED_FIELDS.get(product, [])
        missing = [f for f in required if f not in data]
        if missing:
            reprompt = f"Now, back to your quote — {_ask_next_question(missing[0])}"
            state["messages"].append({"role": "assistant", "content": reprompt})

    if state.get("ask_again_flag"):
        state["mode"] = "quote"
        state["question_in_middle_of_quote_flag"] = False
        state["ask_again_flag"] = False
        message = f"Now, back to your quote. Could you please specify which product you're interested in?"
        state["messages"].append({ "role": "assistant", "content": message })

    if state.get("quote_step") == "confirm":
        state["mode"] = "confirm"
        state["messages"].append({"role": "assistant", "content": "Do you want to use this quote?"})

    return state
    
def identify_node(state: ChatState) -> ChatState:
    """
    Identifies the type of insurance the user is interested in.
    """
    last_user_message = _get_last_user_message(state)
    system = """You are an insurance quote assistant.
The user wants a quote. Determine which product they want from their message.
Products: auto, home, life.

If the product is clear from their message, return ONLY: "auto", "home", or "life".
If it is a question regarding insurance, return: "rag".
If unclear, return: "unknown".

No explanation, no markdown, just "auto", "home", "life", "rag", or "unknown".
"""

    # Skip only if we've already moved past identification (quote_step is set to something else)
    # quote_step=None means first time — must run. quote_step="identify" means retry — must run.
    if state.get("quote_step") and state.get("quote_step") != "identify":
        return state

    response = _chat(system, last_user_message)
    message_type = response.strip().lower()
    if message_type in ["auto", "home", "life"]:
        state["quote_product"] = message_type
        state["quote_step"] = "collect"
        state["quote_data"] = {}
        state["ask_again_flag"] = False       # clear stale flag from any previous failed attempt
        state["question_in_middle_of_quote_flag"] = False
        message = f"Great! Let's get you a {state['quote_product']} insurance quote. I'll ask you a few questions."
        state["messages"].append({ "role": "assistant", "content": message })
    else:
        # Return invalid message and go back to question_or_quote node
        state["messages"].append({ "role": "assistant", "content": "I'm sorry, I didn't understand which product you're interested in. Could you please specify?" })
        state["mode"] = "idle"
        state["question_in_middle_of_quote_flag"] = message_type == "rag"
        state["ask_again_flag"] = message_type == "unknown"


    return state

def is_valid_identify_node(state: ChatState) -> ChatState:
    """
    Node: sets mode to 'rag' if the user asked a question mid-quote,
    otherwise leaves state unchanged. Always returns the state dict
    """

    if state.get("ask_again_flag"):
        state["quote_step"] = "identify"
    elif state.get("question_in_middle_of_quote_flag"):
        state["mode"] = "rag"
    elif state.get("quote_step") == "confirm":
        state["mode"] = "idle"
        state["quote_data"] = {}
        state["ask_again_flag"] = False
        state["question_in_middle_of_quote_flag"] = False
    return state

def route_after_identify(state: ChatState) -> str:
    """
    Router: decides which edge to take after is_valid_identify_node
    Must return a string
    """
    if state.get("ask_again_flag"):
        return "ask_again"
    elif state.get("question_in_middle_of_quote_flag"):
        return "question_in_middle_of_quote"
    return "valid"

def route_after_collect(state: ChatState) -> str:
    """
    Router: after collect_node, go to rag immediately if user asked a question,
    otherwise end the turn and wait for the next user message.
    """
    if state.get("question_in_middle_of_quote_flag"):
        return "rag"
    if state.get("quote_step") == "generate":
        return "done" # all fields collected, generate quote
    return "collecting"

REQUIRED_FIELDS = {
    "auto": ["driver_age", "vehicle_year", "vehicle_make", "vehicle_model", "driving_history", "coverage_level"],
    "home": ["property_type", "location", "home_value", "coverage_level"],
    "life": ["applicant_age", "smoker", "health_status", "coverage_amount", "term_length"],
}
def collect_node(state: ChatState) -> ChatState:
    """
    Collects quote data from the user step by step.
    """

    if state.get("quote_step") != "collect":
        return state

    product = state.get("quote_product")
    data = state.get("quote_data", {})
    required = REQUIRED_FIELDS.get(product, [])
    missing = [f for f in required if f not in data]
    last_user_message = _get_last_user_message(state)

    # Skip rag-vs-answer check on the very first collect call (quote_data is empty
    # meaning we just came from identify_node — the last user message is the quote
    # request, not an answer to a data question)
    if data:
        system_check = (
            "The user is mid-quote. Is their message a question about insurance, "
            "or an answer to a quote question?\n"
            "Return ONLY 'rag' or 'answer'.\n"
            "Examples:\n"
            "User: 28 -> answer\n"
            "User: clean record -> answer\n"
            "User: yes -> answer\n"
            "User: comprehensive -> answer\n"
            "User: liability -> answer\n"
            "User: full coverage -> answer\n"
            "User: What does comprehensive cover? -> rag\n"
        )
        msg_type = _chat(system_check, last_user_message).strip().lower()
        if msg_type == "rag":
            state["question_in_middle_of_quote_flag"] = True
            return state

    if missing:
        next_field = missing[0]

        if data:
            system = f"""The user is answering a question about their {product} insurance quote.
The question was about: {next_field.replace("_", " ")}
"""
            raw = _chat(system, last_user_message)
            try:
                extracted = json.loads(raw)
                for k, v in extracted.items():
                    if v is not None:
                        data[k] = v
            except Exception:
                data[next_field] = last_user_message.strip()

            errors = validate_quote_data(product, {next_field: data.get(next_field)})
            if errors:
                data.pop(next_field, None)
                state["quote_data"] = data
                state["messages"].append({"role": "assistant", "content": f"{errors[0]} Please try again."})
                return state

        system = f"""The user is answering a question about their {product} insurance quote.
The question was about: {next_field.replace("_", " ")}
Extract the value from their message and return ONLY JSON.

Field to extract: "{next_field}"
Example output: {{"{next_field}": "value"}}

For yes/no fields (smoker), return true or false.
For number fields (age, year, amount), return a number.
For text fields, return the cleaned string.
Return ONLY the JSON, no explanation."""

        raw = _chat(system, last_user_message)

        try:
            extracted = json.loads(raw)
            for k, v in extracted.items():
                if v is not None:
                    data[k] = v
        except Exception:
            # LLM didn't return clean JSON — store raw answer for the current field
            data[next_field] = last_user_message.strip()

        errors = validate_quote_data(product, {next_field: data.get(next_field)})

        if errors:
            # Field is invalid — remove it and re-ask
            data.pop(next_field, None)
            state["quote_data"] = data
            error_msg = errors[0]  # show first error only
            state["messages"].append({"role": "assistant", "content": f"{error_msg} Please try again."})
            return state


    state["quote_data"] = data

    # Recalculate missing after extraction
    missing = [f for f in required if f not in data]

    if missing:
        # Ask next question
        next_question = _ask_next_question(missing[0])
        state["messages"].append({"role": "assistant", "content": next_question})
        state["quote_step"] = "collect"
    else:
        # All fields collected
        state["messages"].append({"role": "assistant", "content": "Great, I have all the details! Let me generate your quote..."})
        state["quote_step"] = "generate"


    return state

def generate_quote_node(state: ChatState) -> ChatState:
    """
    Generates a quote based on the collected data.
    """
    if state.get("quote_step") != "generate":
        return state
    
    product = state.get("quote_product")
    data = state.get("quote_data", {})

    system = f"""You are an insurance quote assistant.
Generate a quote based on the following data:
{data}
Return ONLY the quote in JSON format.
"""
    raw = _chat(system, "Generate quote")
    try:
        clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        quote = json.loads(clean)
    except Exception:
        quote = {"error": "Failed to generate quote"}
    state["quote_result"] = quote
    state["quote_step"] = "confirm"
    state["messages"].append({"role": "assistant", "content": f"Here is your {product} insurance quote: {quote}"})
    

    return state

def confirm_node(state: ChatState) -> ChatState:
    """
    Ask the user if the quote is accepted.
    """
    if state.get("quote_step") != "confirm":
        return state
    
    last_user_message = _get_last_user_message(state)
    state["quote_step"] = "confirm"
    state["messages"].append({"role": "assistant", "content": "Do you want to use this quote?"})


    return state

def is_valid_confirm_node(state: ChatState) -> bool:
    """
    Check if the confirm_node is valid.
    """
    if state["quote_step"] != "confirm":
        return state

    last_user_message = _get_last_user_message(state)
    system = """
The user just received an insurance quote.
If the user accepts the quote, return 'yes'.
If the user wants to change something or restart, return 'no'.
If the user asks a question about insurance, return 'rag'.
Return ONLY one word: 'yes', 'no', or 'rag'.
"""
    response = _chat(system, last_user_message).strip().lower()

    if response == "rag":
        state["question_in_middle_of_quote_flag"] = True
    elif response == "yes":
        state["mode"] = "idle"
        state["quote_product"] = None
        state["quote_data"] = {}
        state["quote_step"] = None
        state["ask_again_flag"] = False
        state["question_in_middle_of_quote_flag"] = False
        state["quote_accepted"] = True
        state["messages"].append({"role": "assistant", "content": "Great! Your quote has been accepted. We'll be in touch soon!"})
    elif response == "no":
        state["quote_step"] = "collect"
        state["quote_data"] = {}
        state["quote_accepted"] = False
        state["messages"].append({"role": "assistant", "content": "No problem! Let's start over with a new quote."})


    return state

def route_after_confirm(state: ChatState) -> str:
    """
    Router: decides which edge to take after confirm_node.
    Must ONLY return a string matching one of the graph edges, never a dict.
    """
    if state["question_in_middle_of_quote_flag"]:
        return "rag"
    elif state["mode"] == "idle":
        return "done"
    return "adjust"
