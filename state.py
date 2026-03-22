from typing import TypedDict, Optional, Literal, List

class ChatState(TypedDict):
    messages: List[dict] # full conversation history
    mode: Optional[Literal["rag", "quote", "idle"]]
    quote_product: Optional[Literal["auto", "home", "life"]]
    quote_step: Optional[Literal["identify", "collect", "generate", "confirm"]]
    quote_data: Optional[dict] # collected fields (age, vehicle, etc.)
    quote_result: Optional[dict] # final computed quote
    ask_again_flag: Optional[bool]
    question_in_middle_of_quote_flag: Optional[bool]
    quote_accepted: Optional[bool]