# OpportunityFinder 🎯

**An AI-powered job search agent for freshers.**

OpportunityFinder helps users discover entry-level job opportunities using web search and page-fetching tools. It aims to provide useful job information while being transparent about missing details and conflicting source information.

## Features

- 🔎 Search for relevant job opportunities.
- 💼 Gather job titles, employers, and locations.
- 💰 Report salary information when available.
- 📅 Distinguish application deadlines from posting dates.
- 🔗 Include source pages and application links when available.
- ⚠️ Identify missing details and disclose conflicting information.
- 🧪 Include automated tests for the web-probing component.

## Technology Stack

- Python 3.12
- LangGraph
- LangChain
- Gravity AI Agent Platform
- Pytest

## Example Query

```text
Find entry-level Python developer jobs in India for freshers.
Include the job title, employer, location, salary, application
deadline, source page, and application link. Do not invent
missing details.
```

## Project Structure

```text
opportunity-finder/
├── src/
│   ├── agent.py
│   └── probe.py
├── tests/
├── manifest.yaml
├── requirements.txt
├── requirements.lock
├── Gravity.agent.md
├── problem-to-agent.md
├── README.md
└── .gitignore
```

## Validation and Tests

Validate the agent with:

```powershell
gravity validate
```

Run the existing web-probe tests with:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_probe.py -v
```

The current web-probe test suite contains seven tests. These tests cover argument selection, URL extraction, failure reporting, and limiting the number of fetched pages.

## Running Locally

Start the local development dashboard from the project folder:

```powershell
gravity dev
```

Follow the URL and instructions displayed by Gravity.

## Limitations

Job listings and deadlines may change. Always check the original job page before applying. Missing or conflicting information should be reported rather than guessed. Automated tests currently cover the web-probe component, not every part of the job-search workflow.

## Author

Created as an AI agent project using the Gravity platform.

## Disclaimer

OpportunityFinder is an assistive job-discovery tool. Users should independently verify job details, eligibility, deadlines, and application links before applying.
