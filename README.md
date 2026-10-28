# OpportunityFinder — AI-Powered Job Search Agent

OpportunityFinder is a personalized job-search agent built with Python and LangGraph. It helps job seekers discover relevant opportunities based on their skills, background, location, preferred work arrangement, opportunity type, and minimum monthly income.

## Features

- Searches public web sources for relevant job opportunities.
- Supports different fields, including technology, business, marketing, HR, recruitment, operations, content writing, and customer support.
- Compares job requirements with the applicant's background using rules-based matching.
- Categorizes opportunities as **Strong match**, **Possible match**, or **Needs review**.
- Extracts application deadlines and filters out jobs with explicitly identified expired deadlines.
- Reports source links and highlights details that need further verification.
- Includes automated tests for deadline parsing, job matching, and web-probe behavior.

## Technology Stack

- Python 3.12
- LangGraph
- LangChain
- Gravity tools and MCP integration
- Pytest

## Project Structure

```text
opportunity-finder/
├── src/
│   ├── agent.py
│   ├── matching.py
│   └── probe.py
├── tests/
│   ├── test_deadlines.py
│   ├── test_matching.py
│   └── test_probe.py
├── manifest.yaml
├── requirements.txt
├── requirements.lock
├── Gravity.agent.md
├── Gravity.getting-started.md
└── problem-to-agent.md
```

## Run Locally

### Prerequisites

- Windows
- Python 3.12
- Gravity CLI configured and authenticated
- Access to the required Gravity model and web tools

### 1. Clone the repository

```powershell
git clone -b master https://github.com/Mushrrafjamil/Opportunity-finder.git
cd Opportunity-finder
```

### 2. Create and activate a virtual environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this in the same terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Validate the Gravity project

```powershell
gravity validate
```

### 5. Run the agent

```powershell
gravity run --input job_goal="Find entry-level AI internships" --input background="Beginner with Python basics" --input location="India" --input work_arrangement="remote" --input opportunity_type="internship" --input minimum_monthly_income=15000
```

The agent requires a working Gravity configuration and access to its declared tools and model. A successful validation alone does not guarantee that every live run will succeed.

## Run Tests

```powershell
python -m pytest
```

The current test suite contains 16 automated tests covering deadline parsing, job-match classification, and web-probe behavior.

## Matching Categories

- **Strong match:** The available evidence indicates a strong fit with the supplied preferences.
- **Possible match:** The opportunity appears relevant, but some requirements or details may need checking.
- **Needs review:** Important information is missing, unclear, or requires manual verification.

These categories are preliminary guidance, not a guarantee of eligibility, job availability, or recruiter selection.

## Limitations

- Search results depend on the public sources and pages accessible during a run.
- Some listings may omit salary, requirements, or application deadlines.
- Extracted details and application status should be checked on the original source before applying.
- The agent does not guarantee exhaustive search results or successful job applications.

## Project Status

This is an evaluation-stage project. Automated tests and Gravity manifest validation have passed, but live runs can still encounter model or network timeouts. Tool-call limits and live-run reliability require further verification.

## Repository

[GitHub — OpportunityFinder](https://github.com/Mushrrafjamil/Opportunity-finder/tree/master)
