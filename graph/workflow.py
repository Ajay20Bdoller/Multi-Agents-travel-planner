from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from graph.state import TravelState

from agents.coordinator_agent import coordinator_agent
from agents.flight_agent import flight_agent
from agents.hotel_agent import hotel_agent
from agents.itinerary_agent import itinerary_agent
from agents.final_agent import final_agent
from db.postgres import checkpointer


# =========================================================
# Decide which agents should run
# =========================================================

def route_agents(state: TravelState):
    """
    Coordinator has decided which agents are relevant.

    We dynamically send the state to only those agents.

    Example:

        flight_needed = True
        hotel_needed = False
        itinerary_needed = True

    Then:

        Coordinator
             ├──> Flight Agent
             └──> Itinerary Agent
    """

    routes = []

    if state["flight_needed"]:
        routes.append(
            Send("flight_agent", state)
        )

    if state["hotel_needed"]:
        routes.append(
            Send("hotel_agent", state)
        )

    if state["itinerary_needed"]:
        routes.append(
            Send("itinerary_agent", state)
        )

    # If no specialized agent is required,
    # go directly to the final agent.
    if not routes:
        return "final_agent"

    return routes


# =========================================================
# Build graph
# =========================================================

graph = StateGraph(TravelState)


# Add nodes
graph.add_node(
    "coordinator_agent",
    coordinator_agent
)

graph.add_node(
    "flight_agent",
    flight_agent
)

graph.add_node(
    "hotel_agent",
    hotel_agent
)

graph.add_node(
    "itinerary_agent",
    itinerary_agent
)

graph.add_node(
    "final_agent",
    final_agent
)


# =========================================================
# START → Coordinator
# =========================================================

graph.add_edge(
    START,
    "coordinator_agent"
)


# =========================================================
# Coordinator → Relevant Agents
# =========================================================

graph.add_conditional_edges(
    "coordinator_agent",
    route_agents,
    {
        "final_agent": "final_agent"
    }
)


# =========================================================
# Specialized Agents → Final Agent
# =========================================================

graph.add_edge(
    "flight_agent",
    "final_agent"
)

graph.add_edge(
    "hotel_agent",
    "final_agent"
)

graph.add_edge(
    "itinerary_agent",
    "final_agent"
)


# =========================================================
# Final → END
# =========================================================

graph.add_edge(
    "final_agent",
    END
)


# =========================================================
# Compile
# =========================================================

travel_graph = graph.compile(
    checkpointer=checkpointer
)


