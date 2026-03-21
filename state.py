from typing import TypedDict, Optional, Literal, List

class ChatState(TypedDict):
    messages: List[dict] # full conversation history
    mode: Optional[Literal["rag", "quote", "idle"]]
    quote_product: Optional[Literal["auto", "home", "life"]]
    quote_step: Optional[Literal["identify", "collect", "validate", "generate", "confirm"]]
    quote_data: Optional[dict] # collected fields (age, vehicle, etc.)
    quote_result: Optional[dict] # final computed quote
    validation_errors: Optional[list] # error messages to re-prompt with
