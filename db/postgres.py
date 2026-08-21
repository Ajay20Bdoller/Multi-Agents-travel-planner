import os

from dotenv import load_dotenv
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver


# =========================================================
# Load environment variables
# =========================================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set in the .env file."
    )


# =========================================================
# LangGraph PostgreSQL Checkpointer
# =========================================================

_checkpointer_context = PostgresSaver.from_conn_string(
    DATABASE_URL
)

checkpointer = _checkpointer_context.__enter__()

# Creates LangGraph checkpoint tables automatically
checkpointer.setup()


# =========================================================
# Application Database Connection Pool
# =========================================================

db_pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=5
)


# =========================================================
# Create TripMate application tables
# =========================================================

def create_tables():

    with db_pool.connection() as conn:

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trips (

                id UUID PRIMARY KEY,

                thread_id TEXT NOT NULL,

                user_query TEXT NOT NULL,

                answer TEXT,

                flight_results TEXT,

                hotel_results TEXT,

                itinerary TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            );
            """
        )

        conn.commit()




# =========================================================
# Initialize application tables
# =========================================================

create_tables()