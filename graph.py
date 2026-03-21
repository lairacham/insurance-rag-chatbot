from langgraph.graph import StateGraph, START, END
from state import ChatState
from nodes import *

builder = StateGraph(ChatState)

builder.add_node("greet", greet_node)
builder.add_node("question_or_quote", question_or_quote_node)
builder.add_node("rag", rag_node)
builder.add_node("quote", identify_node)

builder.add_edge(START, "greet")
builder.add_edge("greet", "question_or_quote")
builder.add_conditional_edges("question_or_quote", lambda state: state["mode"], {
    "rag": "rag",
    "quote": "quote",
})
builder.add_edge("rag", END)
builder.add_edge("quote", END)

app = builder.compile()

if __name__ == "__main__":
    print("ShieldBase Insurance Assistant (type 'quit' to exit)\n")

    result = app.invoke({
        "messages": [],
    })
    
    for msg in result["messages"]:
        print(f"{msg['role'].upper()}: {msg['content']}")

    while True:
        user_input = input("USER: ").strip()

        if user_input.lower() in ("quit", "exit", "bye"):
            print("ASSISTANT: Goodbye!")
            break
        
        if not user_input:
            continue

        result["messages"].append({"role": "user", "content": user_input})
        result = app.invoke(result)
        
        # Print only the latest assistant message
        last_assistant = None
        for msg in reversed(result["messages"]):
            if msg["role"] == "assistant":
                last_assistant = msg["content"]
                break
        
        if last_assistant:
            print(f"\nASSISTANT: {last_assistant}\n")
