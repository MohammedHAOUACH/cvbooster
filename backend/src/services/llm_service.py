"""
LLM service for CV optimization using litellm (multi-provider abstraction).
Generates ATS-optimized CV content in JSON Resume format.
"""
import json
from typing import Any, Dict


SYSTEM_PROMPT = """You are an expert resume writer and ATS optimization specialist.
Your task is to rewrite a candidate's resume to maximize its match
with a specific job description, while maintaining complete honesty.

RULES:
1. Use EXACT keywords from the job description (verbatim match)
2. Never fabricate experience, skills, or achievements
3. Rephrase existing experience to highlight relevant aspects
4. Use standard section headers: Experience, Education, Skills, Summary
5. Keep it to 1-2 pages maximum
6. Use quantifiable achievements where possible
7. Output must be valid JSON matching the JSON Resume schema
8. Do NOT include any markdown or code blocks - return ONLY the JSON object
9. Make the CV sound natural and professional, not keyword-stuffed

JSON Resume Schema fields to use:
- basics: name, label, email, phone, url, summary, location
- work: array of positions (company, position, startDate, endDate, summary, highlights)
- education: array (institution, area, studyType, startDate, endDate)
- skills: array (name, level, keywords)
- projects: array (name, description, keywords)
- certificates: array (name, issuer, date)
"""

USER_PROMPT_TEMPLATE = """Original Resume (extracted):
{original_cv_data}

Job Description:
{job_posting_data}

Please rewrite the resume to maximize ATS compatibility with this job.
Return ONLY valid JSON in the JSON Resume format - no markdown, no explanation."""


async def optimize_cv_for_job(
    original_cv_data: Dict[str, Any],
    job_posting_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Use LLM to optimize the CV content for a specific job posting.

    Args:
        original_cv_data: Extracted CV data from LiteParse.
        job_posting_data: Job posting data (raw_content, parsed_data).

    Returns:
        Optimized CV as JSON Resume format dict.
    """
    from litellm import acompletion
    import os

    # Build prompts
    user_prompt = USER_PROMPT_TEMPLATE.format(
        original_cv_data=json.dumps(original_cv_data, indent=2),
        job_posting_data=json.dumps(job_posting_data, indent=2),
    )

    # Use local llama.cpp server (OpenAI-compatible)
    local_url = os.environ.get("LOCAL_LLM_URL", "http://localhost:1234")
    local_model = os.environ.get("LOCAL_LLM_MODEL", "Qwen3.6-27B-UD-Q5_K_XL.gguf")

    try:
        print(f"[LLM] Starting CV optimization with local model: {local_model}")
        response = await acompletion(
            model=f"openai/{local_model}",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            api_base=f"{local_url}/v1",
            api_key="sk-no-key-required",
            temperature=0.3,
            timeout=600,
        )

        result_text = response.choices[0].message.content
        print("[LLM] Response received, parsing JSON...")

        # Parse JSON from response
        cv_data = _parse_llm_json(result_text)

        return cv_data

    except Exception as e:
        print(f"[LLM] Error: {str(e)}")
        raise RuntimeError(f"LLM API call failed: {str(e)}")


def _parse_llm_json(text: str) -> Dict[str, Any]:
    """Extract valid JSON from LLM response (handles markdown code blocks)."""
    import re

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from markdown code block
    json_match = re.search(r'```(?:json)?\s*\n([\s\S]*?)\n```', text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find JSON object in text
    start = text.find('{')
    end = text.rfind('}') + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse JSON from LLM response: {text[:200]}...")
