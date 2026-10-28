
from src.matching import classify_job_match


def test_strong_match_for_relevant_candidate_and_job():
    candidate = {
        "background": "Python programming, beginner, student",
        "skills": ["Python"],
        "experience_level": "beginner",
        "work_arrangement": "remote",
        "opportunity_type": ["internship"],
        "minimum_monthly_income": 0,
    }

    job = {
        "title": "Python Intern",
        "required_skills": ["Python"],
        "experience_level": "beginner",
        "work_arrangement": "remote",
        "opportunity_type": "internship",
        "source_url": "https://example.com/python-intern",
    }

    result = classify_job_match(candidate, job)

    assert result["category"] == "Strong match"
    assert result["reasons"]


def test_unconfirmed_requirements_do_not_become_strong_match():
    candidate = {
        "background": "Beginner with basic Python knowledge",
        "skills": ["Python"],
        "experience_level": "beginner",
        "work_arrangement": "remote",
    }

    job = {
        "title": "Python Developer Intern",
        "required_skills": ["Python", "Django", "REST APIs"],
        "experience_level": "beginner",
        "work_arrangement": "remote",
        "source_url": "https://example.com/python-role",
    }

    result = classify_job_match(candidate, job)

    assert result["category"] != "Strong match"
    assert result["concerns"]


def test_missing_source_requires_review():
    candidate = {
        "background": "Beginner Python student",
        "skills": ["Python"],
        "experience_level": "beginner",
        "work_arrangement": "remote",
    }

    job = {
        "title": "Python Intern",
        "required_skills": ["Python"],
        "experience_level": "beginner",
        "work_arrangement": "remote",
    }

    result = classify_job_match(candidate, job)

    assert result["category"] != "Strong match"
    assert any("source link" in item.casefold() for item in result["concerns"])


def test_work_arrangement_conflict_needs_review():
    candidate = {
        "background": "Beginner Python student",
        "skills": ["Python"],
        "experience_level": "beginner",
        "work_arrangement": "remote",
    }

    job = {
        "title": "Python Intern",
        "required_skills": ["Python"],
        "experience_level": "beginner",
        "work_arrangement": "on-site",
        "source_url": "https://example.com/onsite-role",
    }

    result = classify_job_match(candidate, job)

    assert result["category"] == "Needs review"
