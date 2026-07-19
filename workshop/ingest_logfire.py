"""Pull trace data from Pydantic Logfire and load into DuckDB using dlt."""

import os
from datetime import datetime, timedelta, timezone

import dlt
import requests
from dotenv import load_dotenv

load_dotenv()

# Logfire config
LOGFIRE_READ_TOKEN = os.getenv("LOGFIRE_READ_TOKEN")
QUERY_URL = "https://logfire-us.pydantic.dev/v2/query"


def query_logfire(sql: str, hours_back: int = 24) -> list[dict]:
    """Execute a SQL query against the Logfire API and return rows as dicts."""
    now = datetime.now(timezone.utc)
    headers = {
        "Authorization": f"Bearer {LOGFIRE_READ_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "sql": sql,
        "min_timestamp": (now - timedelta(hours=hours_back)).isoformat(),
        "max_timestamp": now.isoformat(),
    }
    response = requests.post(QUERY_URL, json=payload, headers=headers)
    response.raise_for_status()

    result = response.json()
    return result.get("data", [])


@dlt.resource(name="traces", write_disposition="replace")
def logfire_traces():
    """Fetch all trace/span records from Logfire."""
    rows = query_logfire(
        "SELECT * FROM records ORDER BY start_timestamp DESC LIMIT 1000"
    )
    yield rows


def main():
    pipeline = dlt.pipeline(
        pipeline_name="logfire_to_duckdb",
        destination="duckdb",
        dataset_name="agent_traces",
    )

    load_info = pipeline.run(logfire_traces())
    print(load_info)

    # Quick check: print row count
    with pipeline.sql_client() as client:
        result = client.execute_sql("SELECT COUNT(*) FROM traces")
        print(f"\nTotal rows loaded: {result[0][0]}")


if __name__ == "__main__":
    main()
