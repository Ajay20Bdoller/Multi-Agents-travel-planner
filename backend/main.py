import uuid
import traceback

from fastapi import FastAPI
from pydantic import BaseModel

from graph.workflow import travel_graph
from db.postgres import db_pool
from fastapi.middleware.cors import CORSMiddleware



# =========================================================
# FastAPI application
# =========================================================

app = FastAPI(
    title="Trip planner",
    description="Multi-Agent AI Travel Planner",
    version="1.0.0"
)


# =========================================================
# Frontend and backend connection
# =========================================================


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# Request model
# =========================================================

class TravelRequest(BaseModel):
    message: str
    thread_id: str | None = None


# =========================================================
# Travel API
# =========================================================

@app.post("/api/travel")
async def travel_planner(request_data: TravelRequest):

    try:
        # -------------------------------------------------
        # Get user message
        # -------------------------------------------------

        user_message = request_data.message.strip()

        if not user_message:
            return {
                "success": False,
                "error": "Message cannot be empty."
            }


        # -------------------------------------------------
        # Create thread ID if frontend didn't provide one
        # -------------------------------------------------

        thread_id = request_data.thread_id

        if not thread_id:
            thread_id = f"user_{uuid.uuid4().hex}"


        # -------------------------------------------------
        # LangGraph configuration
        # -------------------------------------------------

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }


        # -------------------------------------------------
        # Run multi-agent LangGraph workflow
        # -------------------------------------------------

        result = travel_graph.invoke(
            {
                "messages": [],
                "user_query": user_message,

                # Coordinator will decide these
                "flight_needed": False,
                "hotel_needed": False,
                "itinerary_needed": False,

                # Initially empty
                "flight_results": "",
                "hotel_results": "",
                "itinerary": "",

                "llm_calls": 0
            },
            config=config
        )


        # -------------------------------------------------
        # Get final message from workflow
        # -------------------------------------------------

        final_message = result["messages"][-1]


        # -------------------------------------------------
        # Save trip to PostgreSQL
        # -------------------------------------------------

        trip_id = uuid.uuid4()

        with db_pool.connection() as conn:

            conn.execute(
                """
                INSERT INTO trips (
                    id,
                    thread_id,
                    user_query,
                    answer,
                    flight_results,
                    hotel_results,
                    itinerary
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    trip_id,
                    thread_id,
                    user_message,
                    final_message.content,
                    result.get("flight_results", ""),
                    result.get("hotel_results", ""),
                    result.get("itinerary", "")
                )
            )

            conn.commit()


        # -------------------------------------------------
        # Final response
        # -------------------------------------------------

        return {
            "success": True,

            "trip_id": str(trip_id),

            "thread_id": thread_id,

            "answer": final_message.content,

            "flight_results": result.get(
                "flight_results",
                ""
            ),

            "hotel_results": result.get(
                "hotel_results",
                ""
            ),

            "itinerary": result.get(
                "itinerary",
                ""
            ),

            "llm_calls": result.get(
                "llm_calls",
                0
            )
        }


    except Exception as e:

        print("ERROR:", e)
        traceback.print_exc()

        return {
            "success": False,
            "error": str(e)
        }


# =========================================================
# Get all saved trips
# =========================================================

@app.get("/api/trips")
async def get_trips():

    try:

        with db_pool.connection() as conn:

            rows = conn.execute(
                """
                SELECT
                    id,
                    thread_id,
                    user_query,
                    created_at
                FROM trips
                ORDER BY created_at DESC
                """
            ).fetchall()

        trips = []

        for row in rows:

            trips.append({
                "trip_id": str(row[0]),
                "thread_id": row[1],
                "user_query": row[2],
                "created_at": row[3].isoformat()
                    if row[3] else None
            })

        return {
            "success": True,
            "trips": trips
        }

    except Exception as e:

        print("ERROR:", e)
        traceback.print_exc()

        return {
            "success": False,
            "error": str(e)
        }




# =========================================================
# Get one saved trip
# =========================================================

@app.get("/api/trips/{trip_id}")
async def get_trip(trip_id: str):

    try:

        with db_pool.connection() as conn:

            row = conn.execute(
                """
                SELECT
                    id,
                    thread_id,
                    user_query,
                    answer,
                    flight_results,
                    hotel_results,
                    itinerary,
                    created_at
                FROM trips
                WHERE id = %s
                """,
                (trip_id,)
            ).fetchone()

        if not row:

            return {
                "success": False,
                "error": "Trip not found."
            }

        return {
            "success": True,
            "trip": {
                "trip_id": str(row[0]),
                "thread_id": row[1],
                "user_query": row[2],
                "answer": row[3],
                "flight_results": row[4],
                "hotel_results": row[5],
                "itinerary": row[6],
                "created_at": row[7].isoformat()
                    if row[7] else None
            }
        }

    except Exception as e:

        print("ERROR:", e)
        traceback.print_exc()

        return {
            "success": False,
            "error": str(e)
        }




# =========================================================
# Health check
# =========================================================

@app.get("/health")
async def health_check():

    return {
        "status": "ok",
        "message": "Trip planner API is running"
    }


# =========================================================
# Run server
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )