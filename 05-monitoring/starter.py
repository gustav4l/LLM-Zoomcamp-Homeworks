"""Starter code for the monitoring homework.

Sets up the text-search RAG from homework 1 and a shared OpenAI client.
"""

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
import os
from gitsource import GithubRepositoryDataReader
from minsearch import Index

from rag_tracer import RAGTraced

COMMIT = "8c1834d"

# --- Load the course lessons (same as HW1, HW2, HW4) ---
reader = GithubRepositoryDataReader(
    repo_owner="DataTalksClub",
    repo_name="llm-zoomcamp",
    commit_id=COMMIT,
    allowed_extensions={"md"},
    filename_filter=lambda path: "/lessons/" in path,
)
documents = [file.parse() for file in reader.read()]

index = Index(text_fields=["content"], keyword_fields=["filename"])
index.fit(documents)

client = OpenAI(base_url="https://ai.sumopod.com/v1",api_key=os.getenv("SUMOPOD_API_KEY"))
assistant = RAGTraced(index, client)

if __name__ == "__main__":
    query = "How does the agentic loop keep calling the model until it stops?"
    answer = assistant.rag(query)
    print(answer)