"""Streaming wrapper around the existing agent pipeline.

This intentionally does NOT modify agents.py. It imports the same building
blocks (build_search_agent, build_reader_agent, writer_chain, critic_chain)
and re-runs the same four steps, but fires a callback after each step so the
Flask app can push live progress to the browser over Server-Sent Events.
"""

from agents import build_search_agent, build_reader_agent, critic_chain, writer_chain


def _to_text(value) -> str:
    """Best-effort stringification for LangChain message / chain outputs."""
    if isinstance(value, str):
        return value
    content = getattr(value, "content", None)
    if isinstance(content, str):
        return content
    return str(value)


def run_research_pipeline_stream(topic: str, callback=None) -> dict:
    """Same 4-step pipeline as run_research_pipeline, with progress events.

    callback(event: dict) is called with:
        {"step": "search" | "reader" | "writer" | "critic",
         "status": "started" | "done",
         "content": str | None}
    """
    state = {}

    def emit(step, status, content=None):
        if callback:
            callback({
                "step": step,
                "status": status,
                "content": _to_text(content) if content is not None else None,
            })

    # ---- 1. Search -------------------------------------------------------
    emit("search", "started")
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state["search_results"] = _to_text(search_result["messages"][-1].content)
    emit("search", "done", state["search_results"])

    # ---- 2. Read / scrape --------------------------------------------------
    emit("reader", "started")
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"""Based on the following results about the {topic},
            Pick the most relevant URL and scrape them for deeper content.

            Search Results:
            {state['search_results'][:300]}""")]
    })
    state["scraped_results"] = _to_text(reader_result["messages"][-1].content)
    emit("reader", "done", state["scraped_results"])

    # ---- 3. Write ----------------------------------------------------------
    emit("writer", "started")
    research_combined = (
        f"Search Results : {state['search_results']}",
        f"Detailed Scraped Results : {state['scraped_results']}",
    )
    state["report"] = _to_text(writer_chain.invoke({
        "topic": topic,
        "research": research_combined,
    }))
    emit("writer", "done", state["report"])

    # ---- 4. Critique ---------------------------------------------------
    emit("critic", "started")
    state["feedback"] = _to_text(critic_chain.invoke({f"Report : {state['report']}"}))
    emit("critic", "done", state["feedback"])

    return state
