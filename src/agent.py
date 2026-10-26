# src/agent.py — the minimal template. No Gravity import: only three env vars.
import os
from typing import TypedDict

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import create_react_agent
from probe import run_web_probe


# Inputs arrive in state["inputs"]; the final `result` is what the consumer gets.
# No `messages` key: that would make it a chat agent.
class State(TypedDict, total=False):
    inputs: dict
    actions: list
    action: str
    action_inputs: dict
    result: object


# ← manifest.runtime.entrypoint. An async factory the runner calls per run; building the
# graph at import breaks inside the runner's event loop.
async def graph():
    token = os.environ["GRAVITY_RUN_TOKEN"]

    # models -> gravity's llm gateway: just a base_url. The run token is the
    # api key; the gateway swaps it for the real one.
    model = ChatOpenAI(
        model="openai/gpt-6-luna",
        base_url=os.environ["GRAVITY_LLM_URL"],
        api_key=token,
    )

    # tools -> gravity's gateway over mcp. It only serves what the manifest
    # declared, so this list is exactly permissions.tools.
    client = MultiServerMCPClient(
        {
            "gravity": {
                "transport": "streamable_http",
                "url": os.environ["GRAVITY_GATEWAY_URL"],
                "headers": {"Authorization": f"Bearer {token}"},
            }
        }
    )
    tools = await client.get_tools()
    react = create_react_agent(
        model,
        tools,
        
prompt=(
    "Help with the user's query using the available tools. "
    "For job searches, use source pages to verify each job's title, "
    "employer, location, salary, application deadline, and application URL. "
    "Never infer or invent missing job details. "
    "Distinguish application deadlines from posting dates, interview dates, "
    "and other dates. Report a deadline only when the source explicitly "
    "identifies it as the application deadline. Preserve the date as stated "
    "by the source. If the deadline is absent or cannot be verified, write "
    "'Not stated in the source' or clearly explain the verification failure. "
    "If sources conflict, disclose the conflict rather than guessing. "
    "Include the source page for each listing and do not claim a fact was "
    "verified unless the source supports it."
),

    )

    async def run_agent(state: State):
        query = state["inputs"].get("query", "")
        actions = state.get("actions") or ["answer"]
        action = state.get("action") or actions[0]
        if action == "web_probe":
            probe_tools = {
                tool.name.replace(".", "_"): tool
                for tool in tools
            }
            return {"result": await run_web_probe(query, probe_tools)}
        result = await react.ainvoke({"messages": [{"role": "user", "content": query}]})
        return {"result": result["messages"][-1].content}

    workflow = StateGraph(State)
    workflow.add_node("agent", run_agent)
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", END)
    return workflow.compile()
