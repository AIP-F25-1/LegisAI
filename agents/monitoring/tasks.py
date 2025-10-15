from crewai import Task

def monitoring_task():
    return Task(
        description=(
            "Call crawl_sources to collect current regulatory texts. "
            "Summarize novel or changed items (assume comparison to last run heuristically). "
            "Return STRICT JSON object only:\n"
            "{ \"changes\": [ {\"id\": str, \"title\": str, \"source\": str, "
            "\"summary\": str, \"affected_domain\": str, \"update_suggestion\": str } ] }"
        ),
        expected_output="Valid JSON with 'changes' array.",
        agent=None
    )
