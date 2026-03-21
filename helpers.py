import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from state import ChatState

load_dotenv()

llm = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# TODO: Update to paid model after testing
MODEL = "nvidia/nemotron-3-super-120b-a12b:free"

def _get_last_user_message(state: ChatState) -> str:
    for msg in reversed(state.get("messages", [])):
        if msg.get("role") == "user":
            return msg["content"]
    return ""

def _chat(system: str, user: str) -> str:
    response = llm.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    )
    return response.choices[0].message.content.strip()
