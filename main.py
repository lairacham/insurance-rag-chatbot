from langgraph.graph import StateGraph, START, END
from state import ChatState
from nodes import *
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()

builder = StateGraph(ChatState)

builder.add_node("greet", greet_node)
builder.add_node("question_or_quote", question_or_quote_node)
builder.add_node("rag", rag_node)
builder.add_node("quote", identify_node)
builder.add_node("collect", collect_node)
builder.add_node("is_valid_identify", is_valid_identify_node)
builder.add_node("generate_quote", generate_quote_node)
builder.add_node("confirm", confirm_node)
builder.add_node("is_valid_confirm", is_valid_confirm_node)

builder.add_edge(START, "greet")
builder.add_edge("greet", "question_or_quote")
builder.add_edge("quote", "is_valid_identify")
builder.add_edge("generate_quote", "confirm")

builder.add_conditional_edges("question_or_quote", lambda state: state.get("mode", "idle"), {
    "rag": "rag",
    "quote": "quote",
    "confirm": "is_valid_confirm",
    "idle": END,
})
builder.add_conditional_edges("is_valid_identify", route_after_identify, {
    "ask_again": END, # already asked clarification — wait for user's reply
    "question_in_middle_of_quote": "rag",
    "valid": "collect",
})
builder.add_conditional_edges("collect", route_after_collect, {
    "rag": "rag", # user asked a question mid-quote → answer it immediately
    "done": "generate_quote",
    "collecting": END,
})
builder.add_conditional_edges("is_valid_confirm", route_after_confirm, {
    "rag": "rag", # user asked a question mid-quote → answer it immediately
    "adjust": "collect",
    "done": END,
})

builder.add_edge("rag", END)
builder.add_edge("confirm", END)

app = builder.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    print("ShieldBase Insurance Assistant (type 'quit' to exit)\n")

    config = {"configurable": {"thread_id": "session-1"}}
    result = app.invoke({
        "messages": [],
    }, config=config)
    
    for message in result["messages"]:
        print(f"{message['role'].upper()}: {message['content']}")

    while True:
        user_input = input("USER: ").strip()

        if user_input.lower() in ("quit", "exit", "bye"):
            print("ASSISTANT: Goodbye!")
            break
        
        if not user_input:
            continue

        message_count_before = len(result["messages"])

        result["messages"].append({"role": "user", "content": user_input})
        result = app.invoke(result, config=config)
        
        # Print all new assistant messages since before invoke
        new_messages = result["messages"][message_count_before + 1:]  # +1 to skip the user message we added
        for message in new_messages:
            if message["role"] == "assistant":
                print(f"\nASSISTANT: {message['content']}\n")


    # Uncomment to save graph as png
    # from IPython.display import Image
    # image = Image(app.get_graph().draw_mermaid_png())
    # with open("graph.png", "wb") as f:
    #     f.write(image.data)
