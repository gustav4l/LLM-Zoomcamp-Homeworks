"""Query agent traces from DuckDB to find input token usage per run."""

import duckdb

DB_PATH = ".dlt/data/dev/logfire_to_duckdb.duckdb"

conn = duckdb.connect(DB_PATH, read_only=True)

# Q2: How many tables in agent_traces schema?
print("=== Q2: Table count in agent_traces schema ===")
conn.sql("""
    SELECT COUNT(*) as table_count
    FROM information_schema.tables 
    WHERE table_schema = 'agent_traces'
""").show()

# Q3: Input token usage per agent run (trace)
print("=== Q3: Input token usage per trace ===")
conn.sql("""
    SELECT 
        trace_id,
        SUM(attributes__gen_ai_usage_input_tokens) as total_input_tokens,
        SUM(attributes__gen_ai_usage_output_tokens) as total_output_tokens,
        MIN(start_timestamp) as run_start
    FROM agent_traces.traces
    WHERE attributes__gen_ai_usage_input_tokens IS NOT NULL
    GROUP BY trace_id
    ORDER BY run_start
""").show()

conn.close()
