
import json
import os
import re
from datetime import date, datetime
from typing import TypedDict

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import StructuredTool
from matching import classify_job_match
from probe import run_web_probe


class State(TypedDict, total=False):
    inputs: dict
    actions: list
    action: str
    action_inputs: dict
    result: object


def parse_deadline(value: str):
    """Parse an explicit application deadline using common date formats."""
    if not isinstance(value, str) or not value.strip():
        return None

    text = value.strip()

    formats = (
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
    )

    for fmt in formats:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    # Accept a date embedded in a longer phrase, but only if
    # the phrase contains a recognizable full date.
    patterns = (
        r"\b[A-Za-z]+ \d{1,2},? \d{4}\b",
        r"\b\d{1,2} [A-Za-z]+ \d{4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b",
    )

    for pattern in patterns:
        match = re.search(pattern, text)
        if not match:
            continue

        candidate = match.group(0)
        for fmt in formats:
            try:
                return datetime.strptime(candidate, fmt).date()
            except ValueError:
                continue

    return None


def as_text(value) -> str:
    """Convert extracted values to clean display strings."""
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if item)
    return str(value).strip()


async def graph():
    token = os.environ["GRAVITY_RUN_TOKEN"]

    model = ChatOpenAI(
        model="openai/gpt-6-luna",
        base_url=os.environ["GRAVITY_LLM_URL"],
        api_key=token,
    )

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

    # react = create_react_agent()
    original_tools = await client.get_tools()

    # Enforce per-run limits on web-tool calls.
    usage = {"search": 0, "fetch": 0}
    tools = []

    for original_tool in original_tools:
        tool_name = original_tool.name.lower().replace(".", "_")

        if tool_name in {"web_search", "search"}:
            limit_type = "search"
            limit = 2
        elif tool_name in {"web_fetch", "web_fetch_proxied"}:
            limit_type = "fetch"
            limit = 3
        else:
            tools.append(original_tool)
            continue

        async def limited_call(
            _tool=original_tool,
            _kind=limit_type,
            _limit=limit,
            **kwargs,
        ):
            if usage[_kind] >= _limit:
                return (
                    f": Maximum {_limit} calls for "
                    f"{_kind}. Do not retry; continue using the "
                    "information already collected."
                )

            usage[_kind] += 1
            return await _tool.ainvoke(kwargs)

        tools.append(
            StructuredTool.from_function(
                coroutine=limited_call,
                name=original_tool.name,
                description=original_tool.description or original_tool.name,
                args_schema=original_tool.args_schema,
            )
        )

    react = create_react_agent(
        model,
        tools,
        prompt=(
            "You are OpportunityFinder, a careful personalized job-search assistant. "
            "Search across relevant industries when the applicant is open to different "
            "fields, including technology, business, marketing, HR, recruitment, "
            "operations, content writing, and customer support. "
            "Use at most 2 web searches and fetch at most 3 job listing pages total. "
            "Do not repeat a search or fetch the same URL more than once. "
            "Return useful opportunities found within these search limits; do not claim "
            "to have searched the entire internet. "
            "Report role, employer, location, arrangement, opportunity type, pay, "
            "requirements, application deadline, and source URL when supported. "
            "Write 'Not stated in the source' for missing details. "
            "Distinguish application deadlines from posting dates, interview dates, "
            "and other dates. "
            "The supplied current date is authoritative for deciding whether a deadline "
            "has passed. Do not rely on your own assumed current date. "
            "Verify application deadlines from the fetched listing page, not just "
            "search-result snippets. Extract only the actual application deadline. "
            "If the deadline has passed, exclude the job. "
            "If the deadline cannot be verified or dates conflict, disclose that fact "
            "and do not present the job as verified and active. "
            "Never invent job details, salary, deadlines, application links, or "
            "verification claims. Include source links and explain each role's fit."
        ),
    )
    async def run_agent(state: State):
        inputs = state.get("inputs", {})

        job_goal = inputs.get(
            "job_goal", "Open to suitable opportunities"
        )
        background = inputs.get("background", "")
        location = inputs.get("location", "")
        work_arrangement = inputs.get("work_arrangement", "any")
        opportunity_type = inputs.get("opportunity_type", ["any"])
        minimum_income = inputs.get("minimum_monthly_income", 0)
        extra_preferences = inputs.get("query", "")

        if isinstance(opportunity_type, str):
            opportunity_types = [
                item.strip()
                for item in opportunity_type.split(",")
                if item.strip()
            ]
        elif isinstance(opportunity_type, list):
            opportunity_types = opportunity_type
        else:
            opportunity_types = ["any"]

        today = date.today()

        query = (
            f"Today's date is {today.isoformat()}.\n"
            "Use this exact date when checking application deadlines. "
            "Do not recommend jobs whose application deadline is before today.\n"
            f"Job goal or preferred fields: {job_goal}\n"
            f"Applicant skills, education, experience, and projects: {background}\n"
            f"Preferred location: {location}\n"
            f"Preferred work arrangement: {work_arrangement}\n"
            f"Opportunity types: {', '.join(opportunity_types)}\n"
            f"Minimum monthly income: {minimum_income}. "
            "Zero means flexible. Do not assume a currency unsupported by the inputs.\n"
            f"Additional preferences: {extra_preferences}\n"
            "Find suitable opportunities from public web sources. "
            "Search relevant industries if the applicant is open to any field. "
            "Verify deadlines from listing pages and distinguish deadlines from "
            "posting dates. Disclose missing or conflicting facts. "
            "Never invent details or claim verification without evidence. "
            "Return suitable results within the search limits."
        )

        actions = state.get("actions") or ["answer"]
        action = state.get("action") or actions[0]

        if action == "web_probe":
            probe_tools = {
                tool.name.replace(".", "_"): tool
                for tool in tools
            }
            return {
                "result": await run_web_probe(query, probe_tools)
            }

        result = await react.ainvoke(
            {"messages": [{"role": "user", "content": query}]},
            config={"recursion_limit": 15},
        )

        messages = result.get("messages", [])
        answer = (
            messages[-1].content
            if messages
            else "The job search did not return an answer."
        )

        extraction_prompt = (
            "Extract structured facts about jobs mentioned in the answer below. "
            "Return valid JSON only: a list of objects. "
            "Each object must contain: title, employer, required_skills, "
            "experience_level, location, work_arrangement, opportunity_type, "
            "stipend_or_salary, deadline, source_url, requirements. "
            "required_skills and requirements must be lists of strings. "
            "All other fields must be strings. "
            "For deadline, extract only an explicitly stated application deadline, "
            "not a posting date, interview date, or date range for the role. "
            "If no application deadline is explicitly stated, use an empty string. "
            "If a date is uncertain or conflicting, do not guess. "
            "Use only facts in the answer. Do not add jobs or invent details. "
            "Copy source URLs exactly. "
            f"\nCurrent date: {today.isoformat()}"
            f"\n\nJob-search answer:\n{answer}"
        )

        try:
            extracted = await model.ainvoke(extraction_prompt)
            raw_content = extracted.content

            if isinstance(raw_content, list):
                raw_content = "".join(
                    item.get("text", "")
                    for item in raw_content
                    if isinstance(item, dict)
                )

            raw_content = str(raw_content).strip()

            if raw_content.startswith("```"):
                raw_content = raw_content.split("\n", 1)[-1]
                if raw_content.endswith("```"):
                    raw_content = raw_content[:-3].strip()

            jobs = json.loads(raw_content)

            if not isinstance(jobs, list):
                raise ValueError("Expected a JSON list of jobs")

        except (json.JSONDecodeError, TypeError, ValueError, AttributeError):
            return {
                "result": (
                    "The search completed, but job details could not be "
                    "structured reliably. No categorized recommendations "
                    "are being presented. Review the original listing pages "
                    "and verify their application deadlines manually."
                )
            }

        background_lower = background.casefold()
        candidate_level = ""

        if any(
            word in background_lower
            for word in (
                "beginner",
                "fresher",
                "no experience",
                "no professional experience",
                "student",
                "entry-level",
            )
        ):
            candidate_level = "beginner"

        candidate = {
            "background": background,
            "skills": [],
            "experience_level": candidate_level,
            "preferred_location": location,
            "work_arrangement": work_arrangement,
            "opportunity_type": opportunity_types,
            "minimum_monthly_income": minimum_income,
            "job_goal": job_goal,
        }

        categorized_jobs = []
        expired_jobs = []
        unverified_deadlines = []

        for job in jobs:
            if not isinstance(job, dict):
                continue

            title = as_text(job.get("title")) or "Title not stated"
            employer = as_text(job.get("employer")) or "Employer not stated"
            deadline_text = as_text(job.get("deadline"))
            source_url = as_text(job.get("source_url"))

            parsed_deadline = parse_deadline(deadline_text)

            # Do not show confirmed expired jobs in the recommendation sections.
            if parsed_deadline and parsed_deadline < today:
                expired_jobs.append(f"{title} — {employer}")
                continue

            # Unknown or unparsable deadlines must be flagged for review.
            if parsed_deadline is None:
                unverified_deadlines.append(f"{title} — {employer}")

            # Do not let the classifier claim a verified active listing
            # when there is no usable source URL.
            match = classify_job_match(candidate, job)

            concerns = list(match.get("concerns", []))
            reasons = list(match.get("reasons", []))
            category = match.get("category", "Needs review")

            if parsed_deadline is None:
                category = "Needs review"
                concerns.append(
                    "Application deadline is missing or could not be parsed; "
                    "active status is not confirmed"
                )

            if not source_url.startswith(("https://", "http://")):
                category = "Needs review"
                concerns.append("A valid direct source URL is missing")

            categorized_jobs.append(
                {
                    "title": title,
                    "employer": employer,
                    "category": category,
                    "reasons": reasons,
                    "concerns": list(dict.fromkeys(concerns)),
                    "required_skills": job.get("required_skills", []),
                    "requirements": job.get("requirements", []),
                    "location": as_text(job.get("location")) or "Not stated",
                    "work_arrangement": (
                        as_text(job.get("work_arrangement")) or "Not stated"
                    ),
                    "opportunity_type": (
                        as_text(job.get("opportunity_type")) or "Not stated"
                    ),
                    "stipend_or_salary": (
                        as_text(job.get("stipend_or_salary")) or "Not stated"
                    ),
                    "deadline": deadline_text or "Not stated",
                    "source_url": source_url or "Not stated",
                    "deadline_verified_by_parser": parsed_deadline is not None,
                }
            )

        category_order = {
            "Strong match": 0,
            "Possible match": 1,
            "Needs review": 2,
        }

        categorized_jobs.sort(
            key=lambda job: category_order.get(job["category"], 2)
        )

        sections = []

        for category in (
            "Strong match",
            "Possible match",
            "Needs review",
        ):
            category_jobs = [
                job for job in categorized_jobs
                if job["category"] == category
            ]

            if not category_jobs:
                continue

            sections.append(f"## {category}")

            for index, job in enumerate(category_jobs, start=1):
                lines = [
                    f"{index}. **{job['title']} — {job['employer']}**",
                    f"   Location: {job['location']}",
                    f"   Work arrangement: {job['work_arrangement']}",
                    f"   Opportunity type: {job['opportunity_type']}",
                    f"   Salary/stipend: {job['stipend_or_salary']}",
                    f"   Application deadline: {job['deadline']}",
                    "   Why it may fit: "
                    + (
                        "; ".join(job["reasons"])
                        if job["reasons"]
                        else "A clear match could not yet be established."
                    ),
                ]

                if job["concerns"]:
                    lines.append(
                        "   Needs checking: " + "; ".join(job["concerns"])
                    )

                lines.append(f"   Source: {job['source_url']}")
                sections.append("\n".join(lines))

        if not categorized_jobs:
            sections.append(
                "No current recommendations could be produced from the "
                "structured results. Expired jobs, if any, were excluded. "
                "Try another search or verify listings directly."
            )

        if expired_jobs:
            sections.append(
                "## Excluded expired listings\n"
                + "\n".join(f"- {item}" for item in expired_jobs)
            )

        if unverified_deadlines:
            sections.append(
                "## Deadline verification note\n"
                "These listings were not confirmed as active because their "
                "application deadlines were missing or could not be parsed:\n"
                + "\n".join(f"- {item}" for item in unverified_deadlines)
            )

        return {
            "result": (
                f"## OpportunityFinder results\n"
                f"Date checked: {today.isoformat()}\n\n"
                + "\n\n".join(sections)
                + "\n\nOnly dates explicitly extracted as application deadlines "
                "are checked against today's date. Parsing a future date does "
                "not independently prove that a listing is still accepting "
                "applications. Confirm status on the original source before "
                "applying. Results are limited to the searches and pages checked; "
                "they are not exhaustive across the entire internet. Match "
                "categories are guidance, not a guarantee of recruiter selection."
            )
        }

    workflow = StateGraph(State)
    workflow.add_node("agent", run_agent)
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", END)

    return workflow.compile()
