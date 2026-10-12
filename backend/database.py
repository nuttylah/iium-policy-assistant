
import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client


# Load environment variables from the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
    raise ValueError(
        "SUPABASE_URL or SUPABASE_SECRET_KEY is missing."
    )

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY,
)


def save_search_history(question: str, answer: str) -> None:
    """Save a question and its generated answer."""

    supabase.table("search_history").insert(
        {
            "question": question,
            "answer": answer,
        }
    ).execute()


def get_search_history(limit: int = 20) -> list[dict]:
    """Retrieve the most recent search history entries."""

    response = (
        supabase.table("search_history")
        .select("id, question, answer, created_at")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return response.data


def get_search_history_by_id(history_id: int) -> dict | None:
    """Retrieve one search history record by its ID."""

    response = (
        supabase.table("search_history")
        .select("id, question, answer, created_at")
        .eq("id", history_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]
