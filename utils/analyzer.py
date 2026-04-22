"""
AI-powered resume analysis using Google Gemini API.
Handles prompt construction, response parsing, and local ATS keyword scoring.
"""

import json
import re
import google.generativeai as genai


# ---------------------------------------------------------------------------
# Role-specific keyword bank for local ATS scoring
# ---------------------------------------------------------------------------
ROLE_KEYWORDS = {
    "software engineer": [
        "python", "java", "javascript", "c++", "sql", "git", "github",
        "api", "rest", "agile", "scrum", "data structures", "algorithms",
        "docker", "kubernetes", "aws", "cloud", "ci/cd", "testing",
        "microservices", "linux", "html", "css", "react", "node",
        "database", "mongodb", "postgresql", "oop", "design patterns",
    ],
    "data analyst": [
        "sql", "python", "excel", "tableau", "power bi", "statistics",
        "data visualization", "pandas", "numpy", "r", "etl", "dashboard",
        "reporting", "analytics", "machine learning", "data cleaning",
        "a/b testing", "hypothesis testing", "regression", "kpi",
        "data warehouse", "bigquery", "looker", "jupyter", "matplotlib",
    ],
    "data scientist": [
        "python", "machine learning", "deep learning", "tensorflow",
        "pytorch", "scikit-learn", "pandas", "numpy", "sql", "statistics",
        "nlp", "computer vision", "feature engineering", "model deployment",
        "a/b testing", "jupyter", "spark", "aws", "docker", "git",
        "regression", "classification", "clustering", "neural network",
    ],
    "web developer": [
        "html", "css", "javascript", "react", "angular", "vue", "node",
        "typescript", "responsive design", "bootstrap", "tailwind",
        "api", "rest", "graphql", "git", "webpack", "npm", "sass",
        "mongodb", "postgresql", "firebase", "aws", "deployment", "seo",
    ],
    "product manager": [
        "product strategy", "roadmap", "agile", "scrum", "user research",
        "stakeholder", "analytics", "kpi", "a/b testing", "jira",
        "wireframe", "prototype", "market research", "go-to-market",
        "prioritization", "cross-functional", "user stories", "mvp",
        "competitive analysis", "customer feedback", "data-driven",
    ],
    "devops engineer": [
        "docker", "kubernetes", "aws", "azure", "gcp", "terraform",
        "ansible", "jenkins", "ci/cd", "linux", "bash", "python",
        "monitoring", "grafana", "prometheus", "git", "helm",
        "infrastructure as code", "microservices", "networking", "security",
    ],
}

# Generic keywords used when the role doesn't match any specific bank
GENERIC_KEYWORDS = [
    "communication", "teamwork", "leadership", "problem solving",
    "project management", "analytical", "detail-oriented", "collaboration",
    "time management", "critical thinking", "adaptability", "presentation",
    "microsoft office", "excel", "python", "sql", "agile",
]


def _get_keywords_for_role(job_role: str) -> list[str]:
    """Return a keyword list for the given job role.

    Tries exact match first, then partial match, then falls back to generic
    keywords combined with the role words themselves.
    """
    role_lower = job_role.lower().strip()

    # Exact match
    if role_lower in ROLE_KEYWORDS:
        return ROLE_KEYWORDS[role_lower]

    # Partial match — e.g. "senior software engineer" matches "software engineer"
    for key, keywords in ROLE_KEYWORDS.items():
        if key in role_lower or role_lower in key:
            return keywords

    # Fallback — generic keywords + words from the role itself
    role_words = [w for w in role_lower.split() if len(w) > 2]
    return GENERIC_KEYWORDS + role_words


def compute_ats_score(resume_text: str, job_role: str) -> dict:
    """Compute a local ATS compatibility score based on keyword matching.

    Args:
        resume_text: Extracted text content from the resume.
        job_role: Target job role the candidate is applying for.

    Returns:
        Dictionary with:
        - score (int): ATS score out of 100.
        - matched (list[str]): Keywords found in resume.
        - missing (list[str]): Keywords NOT found in resume.
    """
    keywords = _get_keywords_for_role(job_role)
    resume_lower = resume_text.lower()

    matched = []
    missing = []

    for kw in keywords:
        if kw.lower() in resume_lower:
            matched.append(kw)
        else:
            missing.append(kw)

    total = len(keywords)
    score = round((len(matched) / total) * 100) if total > 0 else 0

    return {
        "score": min(score, 100),
        "matched": matched,
        "missing": missing,
    }


# ---------------------------------------------------------------------------
# Gemini AI Analysis
# ---------------------------------------------------------------------------

def configure_gemini(api_key: str) -> None:
    """Configure the Gemini API with the provided key.

    Args:
        api_key: Google Gemini API key.
    """
    genai.configure(api_key=api_key)


def build_analysis_prompt(resume_text: str, job_role: str) -> str:
    """Build a structured prompt for the LLM to analyze the resume.

    Args:
        resume_text: Extracted text content from the resume.
        job_role: Target job role the candidate is applying for.

    Returns:
        Formatted prompt string.
    """
    return f"""Analyze the following resume for the role of {job_role}.

Give:
1. ATS Score (out of 100)
2. Key strengths
3. Missing skills
4. Specific suggestions to improve the resume

Provide your response in the following JSON format ONLY (no extra text):
{{
    "ats_score": <integer from 0 to 100>,
    "score_breakdown": {{
        "keyword_relevance": <integer 0-25>,
        "experience_match": <integer 0-25>,
        "skills_alignment": <integer 0-25>,
        "formatting_clarity": <integer 0-25>
    }},
    "key_strengths": [
        "strength 1",
        "strength 2",
        "strength 3"
    ],
    "missing_skills": [
        "skill 1",
        "skill 2",
        "skill 3"
    ],
    "improvement_suggestions": [
        "suggestion 1",
        "suggestion 2",
        "suggestion 3"
    ],
    "summary": "A 2-3 sentence overall assessment of the resume."
}}

RESUME TEXT:
---
{resume_text}
---

Important:
- Be specific and actionable in your suggestions.
- Base the ATS score on how well the resume matches the target role.
- Consider industry-standard keywords for the role.
- Return ONLY valid JSON, no markdown formatting or code fences.
"""


def parse_llm_response(response_text: str) -> dict:
    """Parse the LLM response text into a structured dictionary.

    Args:
        response_text: Raw text response from the LLM.

    Returns:
        Parsed dictionary with analysis results.

    Raises:
        ValueError: If the response cannot be parsed as valid JSON.
    """
    cleaned = response_text.strip()

    # Remove markdown code fences if present
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group(1)

    # If still wrapped in other text, try to find the JSON object
    if not cleaned.startswith("{"):
        json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if json_match:
            cleaned = json_match.group(0)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse AI response as JSON. Error: {e}"
        )


def analyze_resume(resume_text: str, job_role: str) -> dict:
    """Send the resume to Gemini API for analysis and return parsed results.

    Assumes `configure_gemini()` has already been called with a valid key.

    Args:
        resume_text: Extracted text content from the resume.
        job_role: Target job role the candidate is applying for.

    Returns:
        Dictionary containing analysis results with keys:
        - ats_score, score_breakdown, key_strengths,
        - missing_skills, improvement_suggestions, summary

    Raises:
        RuntimeError: If the API call fails or response cannot be parsed.
    """
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = build_analysis_prompt(resume_text, job_role)
        response = model.generate_content(prompt)
        return parse_llm_response(response.text)
    except ValueError:
        # Re-raise parse errors as-is
        raise
    except Exception as e:
        raise RuntimeError(
            f"AI analysis failed. Please check your API key or try again.\nDetails: {e}"
        )
