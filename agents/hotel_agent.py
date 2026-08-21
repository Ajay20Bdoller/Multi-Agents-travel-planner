import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    AIMessage
)

from graph.state import TravelState
from tools.tavily import tavily_search


load_dotenv()


# ============================================================
# LLM
# ============================================================
# Groq LLM is used as the decision maker.
#
# Its job is NOT to directly search the web.
# It decides:
#   - Is hotel information needed?
#   - Should Tavily be called?
#   - What search query should be sent?
# ============================================================

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)


# ============================================================
# Give the LLM access to Tavily
# ============================================================
# This allows the LLM to decide whether to call Tavily.
#
# If hotel information is unnecessary:
#       no tool call
#
# If hotel information is necessary:
#       LLM creates a query and calls Tavily
# ============================================================

llm_with_tools = llm.bind_tools([tavily_search])


# ============================================================
# HOTEL AGENT
# ============================================================

def hotel_agent(state: TravelState):

    # Get the original user request
    query = state["user_query"]


    # ========================================================
    # Ask the LLM to decide whether Tavily is required
    # ========================================================

    response = llm_with_tools.invoke([

        SystemMessage(
            content="""
You are the Hotel Agent of a travel planning system.

Your responsibility is to provide hotel/accommodation
information when it is relevant to the user's request.

You have access to the tavily_search tool.

DECISION MAKING:

1. First understand the user's request.

2. If hotel/accommodation information is required:
   - Call tavily_search.
   - Create a useful and specific search query.

3. If hotel information is NOT required:
   - Do NOT call tavily_search.

When searching, try to find:
- Recommended hotels
- Hotel location
- Approximate price
- Rating
- Important features
- Useful accommodation information

Never invent hotel information.

Use Tavily when current web information is useful.
"""
        ),

        HumanMessage(content=query)
    ])


    # ========================================================
    # CHECK WHETHER THE LLM DECIDED TO USE TAVILY
    # ========================================================

    if response.tool_calls:

        # We only expect one Tavily call here.
        tool_call = response.tool_calls[0]


        # ====================================================
        # IMPORTANT:
        #
        # tool_call["args"] looks like:
        #
        # {
        #     "query": "best hotels in Thailand"
        # }
        #
        # Therefore we must use ** to unpack the dictionary.
        #
        # WRONG:
        # tavily_search(tool_call["args"])
        #
        # CORRECT:
        # tavily_search(**tool_call["args"])
        # ====================================================

        tool_result = tavily_search(
            **tool_call["args"]
        )


        # ====================================================
        # Return hotel information to the shared state
        # ====================================================

        return {
            "hotel_results": str(tool_result),

            "messages": [
                response,
                AIMessage(
                    content="Hotel information fetched using Tavily."
                )
            ],

            "llm_calls": state.get("llm_calls", 0) + 1
        }


    # ========================================================
    # LLM DECIDED THAT TAVILY IS NOT REQUIRED
    # ========================================================

    return {
        "hotel_results": "",

        "messages": [
            response,
            AIMessage(
                content="Hotel information was not required."
            )
        ],

        "llm_calls": state.get("llm_calls", 0) + 1
    }