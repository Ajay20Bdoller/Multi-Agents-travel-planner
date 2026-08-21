# # this agent use aviationStacktool/


# from langchain_core.messages import AIMessage

# from graph.state import TravelState
# from tools.flight import search_flights


# def flight_agent(state: TravelState):
#     """
#     Flight Agent

#     Responsibility:
#     ----------------
#     Find flight information for the user's trip.

#     This agent does NOT need Gemini to search flights.

#     Instead:
#         User Query
#              ↓
#         AviationStack
#              ↓
#         Flight Results

#     Gemini can be used later to interpret the results,
#     but the actual flight data comes from AviationStack.
#     """

#     # Get the original request from shared state.
#     query = state["user_query"]

#     # Call our AviationStack tool.
#     #
#     # search_flights() is the function from:
#     # tools/flight.py
#     #
#     # Example:
#     # "Plan a trip from Delhi to Tokyo"
#     #
#     # The tool will try to resolve:
#     # Delhi → DEL
#     # Tokyo → NRT
#     #
#     # and then query AviationStack.
#     flight_data = search_flights(query)

#     # Return only the information that this agent
#     # wants to add/update in the shared state.
#     return {
#         "flight_results": flight_data,

#         # Add a message so we know that the Flight Agent
#         # completed its work.
#         "messages": [
#             AIMessage(
#                 content="Flight information fetched successfully."
#             )
#         ],

#         # This agent itself does NOT call Gemini.
#         # Therefore we don't increment llm_calls here.
#         "llm_calls": state.get("llm_calls", 0)
#     }






# ---------------with decision-making ability---------


import os

from dotenv import load_dotenv

# from langchain_google_genai import ChatGoogleGenerativeAI

# from langchain_xai import ChatXAI
from langchain_groq import ChatGroq


from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    AIMessage
)

from graph.state import TravelState
from tools.flight import search_flights

load_dotenv()


# llm = ChatGoogleGenerativeAI(
#     model="gemini-3.1-flash-lite",
#     google_api_key=os.getenv("GEMINI_API_KEY"),
#     temperature=0
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


# Give Gemini access to the AviationStack tool.
#
# Gemini can now decide:
#
# "I need flight information"
#       ↓
# call search_flights()
#
# rather than our Python code blindly calling it.
llm_with_tools = llm.bind_tools([search_flights])


def flight_agent(state: TravelState):

    query = state["user_query"]

    response = llm_with_tools.invoke([
        SystemMessage(
            content="""
You are the Flight Agent.

Your job is to obtain flight information when required.

You have access to the search_flights tool.

Decide whether the tool is necessary.

If flight information is required:
    → call search_flights.

If flight information is not required:
    → do not call the tool.

Do not invent live flight information.
"""
        ),
        HumanMessage(content=query)
    ])

    # If Gemini decided to call AviationStack,
    # execute the requested tool call.
    if response.tool_calls:

        tool_call = response.tool_calls[0]

        tool_result = search_flights(
            **tool_call["args"]
        )

        return {
            "flight_results": str(tool_result),
            "messages": [
                response,
                AIMessage(
                    content="Flight information fetched."
                )
            ]
        }

    # Gemini decided that flight information wasn't needed.
    return {
        "flight_results": "",
        "messages": [
            AIMessage(
                content="Flight information was not required."
            )
        ]
    }