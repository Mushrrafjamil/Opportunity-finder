import asyncio

from src.probe import extract_urls, run_web_probe, select_argument


class FakeTool:
    def __init__(self, schema=None, response=None):
        self.name = "fake_tool"
        self.args_schema = schema
        self.response = response
        self.calls = []

    async def ainvoke(self, args):
        self.calls.append(args)
        return self.response


def test_argument_selection_uses_one_matching_field():
    schema = {
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    }
    assert select_argument(schema, "query", "software jobs Toronto") == {
        "query": "software jobs Toronto"
    }


def test_argument_selection_rejects_ambiguous_schema():
    schema = {
        "properties": {
            "query": {"type": "string"},
            "search_query": {"type": "string"},
        },
        "required": ["query"],
    }
    try:
        select_argument(schema, "query", "jobs")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ambiguous schema to be refused")


def test_extract_urls_uses_recognized_fields():
    response = {"results": [
        {"title": "Role", "url": "https://jobs.example/1"},
        {"title": "Another role", "link": "https://jobs.example/2"},
    ]}
    assert extract_urls(response) == [
        "https://jobs.example/1",
        "https://jobs.example/2",
    ]


def test_extract_urls_rejects_malformed_or_non_http_urls():
    response = {"results": [
        {"url": "https://jobs.example/valid"},
        {"url": "ftp://jobs.example/not-http"},
        {"url": "https:///missing-host"},
        {"url": "https://[::1"},
    ]}
    assert extract_urls(response) == ["https://jobs.example/valid"]


def test_missing_tool_is_reported():
    report = asyncio.run(run_web_probe("entry-level developer jobs", {}))
    assert report["failures"][0]["source"] == "web_search"


def test_schema_failure_is_reported():
    report = asyncio.run(run_web_probe(
        "entry-level developer jobs",
        {"web_search": FakeTool(schema=None)},
    ))
    assert report["failures"][0]["source"] == "web_search"
    assert report["failures"][0]["reason"].startswith("schema:")


def test_probe_fetches_at_most_two_search_urls():
    query_schema = {
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    }
    url_schema = {
        "properties": {"url": {"type": "string"}},
        "required": ["url"],
    }
    search = FakeTool(query_schema, {"results": [
        {"url": "https://jobs.example/1"},
        {"url": "https://jobs.example/2"},
        {"url": "https://jobs.example/3"},
    ]})
    fetch = FakeTool(url_schema, {"content": "sample page"})
    proxied = FakeTool(url_schema)
    report = asyncio.run(run_web_probe(
        "entry-level developer jobs",
        {
            "web_search": search,
            "web_fetch": fetch,
            "web_fetch_proxied": proxied,
        },
    ))
    assert len(fetch.calls) == 2
    assert len(report["pages"]) == 2
    assert proxied.calls == []
