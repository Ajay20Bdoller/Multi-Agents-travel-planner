from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage


class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

    user_query: str

    # Coordinator decisions
    flight_needed: bool
    hotel_needed: bool
    itinerary_needed: bool

    # Agent outputs
    flight_results: str
    hotel_results: str
    itinerary: str

    llm_calls: int