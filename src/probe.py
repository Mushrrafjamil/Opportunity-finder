"""Temporary, read-only probe for Gravity's public web tools."""

from urllib.parse import urlparse


MAX_PROBE_PAGES = 2
URL_FIELDS = {"url", "link", "href", "source_url"}
REFUSALS = (
    "TOOL_NOT_DECLARED",
    "TOOL_UNAVAILABLE",
    "NEEDS_RECONNECT",
    "URL_REFUSED",
    "FETCH_FAILED",
    "PROXY_LIMIT",
)


def inspect_schema(tool):
    schema = getattr(tool, "args_schema", None)
    if isinstance(schema, dict):
        return schema
    if hasattr(schema, "model_json_schema"):
        return schema.model_json_schema()
    if hasattr(schema, "schema"):
        return schema.schema()
    raise ValueError(f"No inspectable input schema for {tool.name}")


def select_argument(schema, purpose, value):
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    names = {"query", "search_query", "q"} if purpose == "query" else {"url"}
    description_term = "search query" if purpose == "query" else "url"
    matches = [
        name for name, field in properties.items()
        if field.get("type") in ("string", None)
        and (
            name.casefold() in names
            or description_term in str(field.get("description", "")).casefold()
        )
    ]
    if len(matches) != 1:
        raise ValueError(f"No unambiguous {purpose} field in the live tool schema")
    name = matches[0]
    if required - {name}:
        raise ValueError("Other required fields exist; refusing to guess their values")
    return {name: value}


def extract_urls(response):
    """Extract validated URLs only from recognized fields in the response."""
    found = []

    def visit(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key.casefold() in URL_FIELDS and isinstance(item, str):
                    try:
                        parsed = urlparse(item)
                    except ValueError:
                        parsed = None
                    if (
                        parsed is not None
                        and parsed.scheme in {"http", "https"}
                        and parsed.hostname
                        and item not in found
                    ):
                        found.append(item)
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(response)
    return found


def first_probe_urls(response):
    return extract_urls(response)[:MAX_PROBE_PAGES]


def checked_response(response):
    text = str(response).upper()
    if any(marker in text for marker in REFUSALS):
        raise RuntimeError(str(response)[:300])
    if isinstance(response, dict) and response.get("successful") is False:
        raise RuntimeError(str(response.get("error", "successful=false"))[:300])
    return response


async def run_web_probe(query, tools):
    report = {
        "query": query,
        "schemas": {},
        "search": None,
        "pages": [],
        "failures": [],
        "web_fetch_proxied": "schema inspected only; tool not called",
    }
    names = ("web_search", "web_fetch", "web_fetch_proxied")
    schemas = {}
    for name in names:
        tool = tools.get(name)
        if tool is None:
            report["failures"].append({"source": name, "reason": "tool missing"})
            return report
        try:
            schemas[name] = inspect_schema(tool)
            report["schemas"][name] = schemas[name]
        except Exception as exc:
            report["failures"].append({"source": name, "reason": f"schema: {exc}"})
            return report

    try:
        search_input = select_argument(schemas["web_search"], "query", query)
        search_response = checked_response(
            await tools["web_search"].ainvoke(search_input)
        )
        report["search"] = {"input": search_input, "response": search_response}
    except Exception as exc:
        report["failures"].append({"source": "web.search", "reason": str(exc)})
        return report

    urls = first_probe_urls(search_response)
    if not urls:
        report["failures"].append({
            "source": "web.search",
            "reason": "No URLs found in recognized result fields",
        })
    for url in urls:
        try:
            fetch_input = select_argument(schemas["web_fetch"], "url", url)
            response = checked_response(
                await tools["web_fetch"].ainvoke(fetch_input)
            )
            report["pages"].append({"input": fetch_input, "response": response})
        except Exception as exc:
            report["failures"].append({
                "source": "web.fetch",
                "url": url,
                "reason": str(exc),
            })
    return report
