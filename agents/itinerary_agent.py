# # This is where Gemini becomes important.

# # It receives the flight + hotel results and generates an itinerary.



# import os

# from dotenv import load_dotenv

# from langchain_google_genai import ChatGoogleGenerativeAI

# from langchain_core.messages import (
#     HumanMessage,
#     SystemMessage
# )

# from graph.state import TravelState


# # Load variables from .env
# load_dotenv()


# # Get Gemini API key.
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# if not GEMINI_API_KEY:
#     raise ValueError(
#         "GEMINI_API_KEY is missing. "
#         "Please add it to your .env file."
#     )


# # Create Gemini LLM.
# #
# # This is the model that will generate our itinerary.
# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     google_api_key=GEMINI_API_KEY,
#     temperature=0.3
# )


# def itinerary_agent(state: TravelState):
#     """
#     Itinerary Agent

#     Responsibility:
#     ----------------
#     Create a day-by-day travel itinerary.

#     It receives:

#         User Query
#         +
#         Flight Results
#         +
#         Hotel Results

#     and asks Gemini to combine this information
#     into a practical itinerary.
#     """

#     # Get information from shared state.
#     user_query = state["user_query"]
#     flight_results = state["flight_results"]
#     hotel_results = state["hotel_results"]

#     # Create the prompt for Gemini.
#     prompt = f"""
# Create a complete travel itinerary based on the information below.

# USER REQUEST:
# {user_query}

# FLIGHT INFORMATION:
# {flight_results}

# HOTEL INFORMATION:
# {hotel_results}

# Create a practical day-by-day itinerary.

# Include:
# - Arrival/departure considerations
# - Major attractions
# - Activities
# - Food suggestions
# - Approximate timing
# - Travel between locations
# - Budget-conscious suggestions

# Do not invent flight details that are not present
# in the flight information.

# If some information is unavailable, clearly mention that.
# """

#     # Send the prompt to Gemini.
#     response = llm.invoke(
#         [
#             SystemMessage(
#                 content=(
#                     "You are an expert travel itinerary planner. "
#                     "Create realistic and practical travel plans."
#                 )
#             ),
#             HumanMessage(content=prompt)
#         ]
#     )

#     # Return Gemini's itinerary into shared state.
#     return {
#         "itinerary": response.content,

#         # Store Gemini's response in messages as well.
#         "messages": [response],

#         # One Gemini call happened.
#         "llm_calls": state.get("llm_calls", 0) + 1
#     }




# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# This one doesn't need AviationStack/Tavily directly.

# It uses the information already collected.


import os

from dotenv import load_dotenv

# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_xai import ChatXAI
from langchain_groq import ChatGroq


from langchain_core.messages import (
    HumanMessage,
    SystemMessage
)

from graph.state import TravelState

load_dotenv()


# llm = ChatGoogleGenerativeAI(
#     model="gemini-3.1-flash-lite",
#     google_api_key=os.getenv("GEMINI_API_KEY"),
#     temperature=0.3
# )



# llm = ChatXAI(
#     model="grok-4.3",
#     api_key=os.getenv("XAI_API_KEY"),
# )

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)
def itinerary_agent(state: TravelState):

    prompt = f"""
Create a practical travel itinerary.

USER REQUEST:
{state["user_query"]}

FLIGHT INFORMATION:
{state.get("flight_results", "")}

HOTEL INFORMATION:
{state.get("hotel_results", "")}

Create a day-by-day itinerary.

Include:
- sightseeing
- activities
- approximate timing
- local travel
- food suggestions
- budget-conscious suggestions

Do not invent flight or hotel information.
If information is unavailable, clearly say so.
"""

    response = llm.invoke([
        SystemMessage(
            content=(
                "You are an expert travel itinerary planner."
            )
        ),
        HumanMessage(content=prompt)
    ])

    return {
        "itinerary": response.content,
        "messages": [response]
    }