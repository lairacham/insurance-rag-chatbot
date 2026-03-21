import os
import json
from state import ChatState
from helpers import _get_last_user_message, _chat
from rag import retrieve

def greet_node(state: ChatState) -> ChatState:
    """
    Greets the user and asks what they need.
    """
    state["messages"] = state.get("messages", [])
    state["mode"] = "idle"
    state["quote_product"] = None
    state["quote_data"] = {}
    state["quote_step"] = None
    state["validation_errors"] = []

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
    if mode == "rag" or mode == "quote":
        state["mode"] = mode
    else:
        state["mode"] = "rag"

    return state

def rag_node(state: ChatState) -> ChatState:
    """
    Retrieves relevant information from the knowledge base and generates a response.
    """
    last_user_message = _get_last_user_message(state)

    context = retrieve(last_user_message)

    system = f"""You are a helpful assistant for ShieldBase Insurance.
Use ONLY the context below to answer the user's question.
If the answer is not in the context, say: "I don't have that information — please call us at 1-800-743-5527."
Be concise and friendly.

Context:
{context}"""

    answer = _chat(system, last_user_message)
    state["messages"].append({ "role": "assistant", "content": answer })
    state["mode"] = "idle"

    return state
    
def identify_node(state: ChatState) -> ChatState:
    """
    Identifies the type of insurance the user is interested in.
    """
    return state