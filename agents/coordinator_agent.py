import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_xai import ChatXAI
from langchain_groq import ChatGroq



from langchain_core.messages import HumanMessage, SystemMessage

from graph.state import TravelState

load_dotenv()


# Gemini is used here as the "router".
# Its job is NOT to answer the user.
# Its job is to decide which specialized agents are needed.
# llm = ChatGoogleGenerativeAI(
#     model="gemini-3.1-flash-lite",
#     google_api_key=os.getenv("GEMINI_API_KEY"),
#     temperature=0
# )


# llm = ChatXAI(
#     model="grok-4.3",
#     api_key=os.getenv("XAI_API_KEY"),
# )


# llm = ChatGroq(
#     model="llama-3.3-70b-versatile",
#     api_key=os.getenv("GROQ_API_KEY"),
#     temperature=0,
# )


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)

# Structured output makes Gemini return predictable
# True/False values instead of random text.
class AgentDecision(BaseModel):

    flight_needed: bool = Field(
        description="True if flight information is required."
    )

    hotel_needed: bool = Field(
        description="True if hotel information is required."
    )

    itinerary_needed: bool = Field(
        description="True if a travel itinerary is required."
    )


# Tell Gemini to return the above structure.
decision_llm = llm.with_structured_output(AgentDecision)


def coordinator_agent(state: TravelState):

    query = state["user_query"]

    response = decision_llm.invoke([
        SystemMessage(
            content="""
You are the coordinator of a multi-agent travel planner.

Analyze the user's request and decide which specialized
agents are actually required.

Flight Agent:
Use when the user asks about flights, airfare,
departure/arrival, airlines, or flight-related planning.

Hotel Agent:
Use when the user asks about hotels, accommodation,
stays, resorts, or lodging.

Itinerary Agent:
Use when the user asks to plan a trip, activities,
day-by-day schedule, sightseeing, or travel itinerary.

Do NOT activate an agent if it is irrelevant.
"""
        ),
        HumanMessage(content=query)
    ])

    return {
        "flight_needed": response.flight_needed,
        "hotel_needed": response.hotel_needed,
        "itinerary_needed": response.itinerary_needed,
    }