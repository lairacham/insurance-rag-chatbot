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

MODEL = "google/gemini-2.0-flash-001"

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
        temperature=0
    )
    return response.choices[0].message.content.strip()

def _chat_with_history(system: str, messages: list[dict]) -> str:
    response = llm.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            *messages
        ]
    )
    return response.choices[0].message.content

def _first_question(product: str) -> str:
    questions = {
        "auto": "What is the year, make, and model of your vehicle? (e.g. 2019 Toyota Camry)",
        "home": "What type of property is it? (single-family, townhouse, condo, or manufactured home)",
        "life": "What is your age?",
    }
    return questions.get(product, "Let's get started. Can you tell me more about what you need?")

def _ask_next_question(field: str) -> str:
    questions = {
        "driver_age":      "How old is the primary driver?",
        "vehicle_year":    "What year is the vehicle?",
        "vehicle_make":    "What is the make of the vehicle? (e.g. Toyota, Ford, Honda)",
        "vehicle_model":   "What is the model? (e.g. Camry, F-150, Civic)",
        "driving_history": "How is your driving history? (clean / minor violation / at-fault accident / multiple violations / DUI)",
        "coverage_level":  "What coverage level would you like? (basic / standard / comprehensive)",
        "property_type":   "What type of property? (single-family / townhouse / condo / manufactured)",
        "location":        "What city and state is the property located in?",
        "home_value":      "What is the estimated rebuild value of the home? (e.g. 350000)",
        "applicant_age":   "How old are you?",
        "smoker":          "Are you a current smoker? (yes or no)",
        "health_status":   "How would you describe your overall health? (excellent / good / fair / poor)",
        "coverage_amount": "How much life insurance coverage do you need? (e.g. 500000)",
        "term_length":     "What term length would you like? (10 / 15 / 20 / 30 years)",
    }
    return questions.get(field, f"Could you provide your {field.replace('_', ' ')}?")
