# # This is Final Response Agent.

# # Its job is NOT to search.

# # Its job is to take everything produced by the other agents and create one clean answer for the user.



# import os

# from dotenv import load_dotenv

# from langchain_google_genai import ChatGoogleGenerativeAI

# from langchain_core.messages import (
#     HumanMessage,
#     SystemMessage
# )

# from graph.state import TravelState


# # Load environment variables.
# load_dotenv()


# # Get Gemini API key.
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# if not GEMINI_API_KEY:
#     raise ValueError(
#         "GEMINI_API_KEY is missing. "
#         "Please add it to your .env file."
#     )


# # Gemini will be used to generate the final answer.
# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     google_api_key=GEMINI_API_KEY,
#     temperature=0.3
# )


# def final_agent(state: TravelState):
#     """
#     Final Response Agent

#     Responsibility:
#     ----------------
#     Combine everything produced by the other agents.

#     Input:

#         User Query
#         Flight Results
#         Hotel Results
#         Itinerary

#     Output:

#         One final response for the user.
#     """

#     user_query = state["user_query"]
#     flight_results = state["flight_results"]
#     hotel_results = state["hotel_results"]
#     itinerary = state["itinerary"]

#     # Give Gemini all information collected by
#     # the previous agents.
#     final_prompt = f"""
# Generate the final travel planning response.

# USER REQUEST:
# {user_query}

# FLIGHT INFORMATION:
# {flight_results}

# HOTEL INFORMATION:
# {hotel_results}

# ITINERARY:
# {itinerary}

# Structure the final response using:

# 1. Trip Summary
# 2. Flight Information
# 3. Hotel Suggestions
# 4. Day-by-Day Itinerary
# 5. Estimated Budget
# 6. Final Recommendations

# Important rules:

# - Use the information provided by the agents.
# - Do not invent flight information.
# - Clearly mention when flight pricing is unavailable.
# - Keep the response practical and easy to understand.
# - Make the final answer useful for real travel planning.
# """

#     # Gemini combines everything into one response.
#     response = llm.invoke(
#         [
#             SystemMessage(
#                 content=(
#                     "You are a professional AI travel planning "
#                     "assistant. Combine information from multiple "
#                     "specialized travel agents into one accurate "
#                     "and useful response."
#                 )
#             ),
#             HumanMessage(content=final_prompt)
#         ]
#     )

#     return {
#         # The final Gemini response is added as the last message.
#         "messages": [response],

#         # Another Gemini call happened.
#         "llm_calls": state.get("llm_calls", 0) + 1
#     }




# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


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

def final_agent(state: TravelState):

    prompt = f"""
Generate the final response to the user's travel request.

USER REQUEST:
{state["user_query"]}

FLIGHT INFORMATION:
{state.get("flight_results", "")}

HOTEL INFORMATION:
{state.get("hotel_results", "")}

ITINERARY:
{state.get("itinerary", "")}

Only include sections that have relevant information.

Possible sections:

1. Trip Summary
2. Flight Information
3. Hotel Suggestions
4. Day-by-Day Itinerary
5. Estimated Budget
6. Final Recommendations

Be clear and practical.

Do not invent live flight information or prices.
"""

    response = llm.invoke([
        SystemMessage(
            content=(
                "You are the final travel planning assistant. "
                "Combine the results from specialized agents "
                "into one useful answer."
            )
        ),
        HumanMessage(content=prompt)
    ])

    return {
        "messages": [response]
    }