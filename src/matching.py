
import re


BEGINNER_LEVELS = {
    "beginner",
    "entry-level",
    "entry level",
    "intern",
    "internship",
    "fresher",
    "junior",
    "student",
}

SKILL_ALIASES = {
    "python programming": ["python"],
    "communication skills": ["communication", "communicate"],
    "written communication": ["written english", "writing"],
    "customer support": ["customer service", "user support"],
    "content writing": ["writing", "content creation"],
    "social media": ["social media management", "instagram", "facebook"],
    "microsoft excel": ["excel", "spreadsheets"],
    "data analysis": ["data analytics", "pandas", "data analysis"],
    "html": ["html"],
    "css": ["css"],
    "javascript": ["javascript", "js"],
    "git": ["git", "github"],
}


def _normalize(value) -> str:
    """Normalize text for simple, case-insensitive comparisons."""
    return re.sub(r"\s+", " ", str(value or "").casefold()).strip()


def _contains_term(text: str, term: str) -> bool:
    """Match a phrase without accidentally matching inside another word."""
    term = _normalize(term)
    if not term:
        return False

    pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
    return re.search(pattern, text) is not None


def _as_list(value) -> list:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _skill_matches(candidate_text: str, required_skill: str) -> bool:
    """Check a requirement against explicit candidate information."""
    skill = _normalize(required_skill)

    if not skill:
        return False

    if _contains_term(candidate_text, skill):
        return True

    aliases = SKILL_ALIASES.get(skill, [])
    return any(_contains_term(candidate_text, alias) for alias in aliases)


def classify_job_match(candidate: dict, job: dict) -> dict:
    """
    Return Strong match, Possible match, or Needs review.

    This is a preliminary rules-based classification, not a guarantee
    of eligibility, job availability, or recruiter selection.
    """

    reasons = []
    concerns = []
    blockers = []

    background = _normalize(candidate.get("background", ""))
    candidate_skills = _as_list(candidate.get("skills", []))
    candidate_text = _normalize(
        " ".join(candidate_skills) + " " + background
    )

    job_goal = _normalize(candidate.get("job_goal", ""))
    job_title = _normalize(job.get("title", ""))
    job_description = _normalize(job.get("description", ""))

    # 1. Compare stated job requirements with candidate information.
    required_skills = _as_list(job.get("required_skills", []))

    generic_requirements = {
        "relevant skills and interests",
        "good attitude",
        "willingness to learn",
        "ability to learn",
        "problem solving",
        "problem-solving",
    }

    required_skills = [
        skill for skill in required_skills
        if _normalize(skill) not in generic_requirements
    ]

    matched_skills = [
        skill for skill in required_skills
        if _skill_matches(candidate_text, skill)
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill not in matched_skills
    ]

    if required_skills:
        if matched_skills:
            reasons.append(
                "Relevant skills found: " + ", ".join(matched_skills)
            )

        if missing_skills:
            concerns.append(
                "Requirements not confirmed: " + ", ".join(missing_skills)
            )
    else:
        concerns.append("Specific required skills are not clearly stated")

    # 2. Check experience compatibility without assuming unknown facts.
    candidate_level = _normalize(candidate.get("experience_level", ""))
    job_level = _normalize(job.get("experience_level", ""))

    if not job_level:
        concerns.append("Required experience level is unclear")
    elif candidate_level and (
        candidate_level == job_level
        or candidate_level in job_level
        or job_level in candidate_level
    ):
        reasons.append("Experience level appears compatible")
    elif candidate_level in BEGINNER_LEVELS and job_level in BEGINNER_LEVELS:
        reasons.append("Role appears suitable for an entry-level applicant")
    else:
        concerns.append("Experience-level compatibility needs checking")

    # 3. Check work arrangement; do not award points for location.
    preferred_arrangement = _normalize(
        candidate.get("work_arrangement", "any")
    )
    job_arrangement = _normalize(job.get("work_arrangement", ""))

    arrangement_aliases = {
        "on-site": {"on-site", "onsite", "office-based", "in-person"},
        "hybrid": {"hybrid"},
        "remote": {"remote", "work from home", "work-from-home", "wfh"},
    }

    if preferred_arrangement in {"", "any"}:
        reasons.append("Candidate is flexible about work arrangement")
    elif not job_arrangement:
        concerns.append("Work arrangement is not confirmed")
    elif (
        job_arrangement == preferred_arrangement
        or any(
            alias in job_arrangement
            for alias in arrangement_aliases.get(preferred_arrangement, set())
        )
    ):
        reasons.append("Work arrangement matches the preference")
    else:
        blockers.append("Work arrangement does not match the preference")
        
    # 4. Check the requested opportunity type when listing data is available.
    preferred_types = _as_list(candidate.get("opportunity_type", []))
    job_type = _normalize(job.get("opportunity_type", ""))

    if preferred_types and "any" not in {
        _normalize(item) for item in preferred_types
    }:
        if not job_type:
            concerns.append("Opportunity type is not confirmed")
        elif not any(
            _normalize(item) in job_type
            or job_type in _normalize(item)
            for item in preferred_types
        ):
            blockers.append("Opportunity type may not match the preference")
        else:
            reasons.append("Opportunity type matches the preference")

    # 5. Check salary only when a minimum is explicitly provided.
    try:
        minimum_income = float(
            candidate.get("minimum_monthly_income", 0) or 0
        )
    except (TypeError, ValueError):
        minimum_income = 0
        concerns.append("Minimum income preference could not be interpreted")

    salary_text = _normalize(job.get("stipend_or_salary", ""))

    if minimum_income > 0:
        if not salary_text or any(
            marker in salary_text
            for marker in ("not stated", "unpaid", "unavailable")
        ):
            concerns.append("Income compatibility is not confirmed")
        else:
            amounts = [
                int(value.replace(",", ""))
                for value in re.findall(
                    r"(?<!\w)(\d[\d,]*)(?!\w)", salary_text
                )
            ]

            if not amounts:
                concerns.append("Salary could not be reliably compared")
            elif max(amounts) < minimum_income:
                blockers.append(
                    "Advertised income appears below the minimum preference"
                )
            elif min(amounts) < minimum_income:
                concerns.append(
                    "Advertised salary range may fall below the minimum preference"
                )
            else:
                reasons.append(
                    "Advertised income appears to meet the minimum preference"
                )

    # 6. Source link is required for a recommendation.
    source_url = str(job.get("source_url", "")).strip()

    if not source_url.startswith(("https://", "http://")):
        concerns.append("A valid direct source link is not available")

    # 7. Category decision.
    # A conflict with a stated preference prevents Strong match.
    if blockers:
        category = "Needs review"
        concerns.extend(blockers)
    elif concerns:
        category = "Possible match" if reasons else "Needs review"
    elif (
        required_skills
        and len(matched_skills) == len(required_skills)
        and job_level
        and candidate_level
        and reasons
    ):
        category = "Strong match"
    else:
        category = "Possible match"

    return {
        "category": category,
        "reasons": reasons,
        "concerns": concerns,
    }
