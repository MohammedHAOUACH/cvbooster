"""
LLM service for CV optimization using OpenRouter.
Generates ATS-optimized CV content in JSON Resume format.
"""
import json
import os
from typing import Any, Dict


SYSTEM_PROMPT = """You are an expert resume writer and ATS optimization specialist.
Your task is to rewrite a candidate's resume to maximize its match
with a specific job description, while maintaining complete honesty.

RULES:
1. Use EXACT keywords from the job description (verbatim match)
2. Never fabricate experience, skills, or achievements
3. Rephrase existing experience to highlight relevant aspects
4. Use standard section headers in the target language (e.g. Expérience, Formation, Compétences for French; Experience, Education, Skills for English)
5. Keep it to 1-2 pages maximum
6. Use quantifiable achievements where possible
7. Output must be valid JSON matching the JSON Resume schema
8. Do NOT include any markdown or code blocks - return ONLY the JSON object
9. Make the CV sound natural and professional, not keyword-stuffed
10. Preserve the original CV section order and format intent where possible
11. CRITICAL: Write ALL content (summary, experience descriptions, education, skills) in {output_language_full}. If the job is in French, write the entire CV in French. If in English, write in English. Do NOT mix languages.
12. Do NOT include images, photos, avatars, or any non-text content. This is a text-only CV.

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

CRITICAL: The entire CV must be written in {output_language_full}. Write the summary, all experience descriptions, education, skills, and section headers in {output_language_full}. Do NOT mix languages.

Please rewrite the resume to maximize ATS compatibility with this job.
Return ONLY valid JSON in the JSON Resume format - no markdown, no explanation."""


async def optimize_cv_for_job(
    original_cv_data: Dict[str, Any],
    job_posting_data: Dict[str, Any],
    output_language: str = "en",
) -> Dict[str, Any]:
    """
    Use LLM to optimize the CV content for a specific job posting.
    
    Args:
        original_cv_data: Extracted CV data from LiteParse.
        job_posting_data: Job posting data (raw_content, parsed_data).
        output_language: Target output language for generated CV content.
    
    Returns:
        Optimized CV as JSON Resume format dict.
    """
    from litellm import acompletion
    
    # Convert language code to full name for clearer instructions
    language_map = {"fr": "French", "en": "English", "es": "Spanish", "de": "German", "it": "Italian", "pt": "Portuguese", "ar": "Arabic"}
    output_language_full = language_map.get(output_language, output_language)
    
    # Build prompts
    user_prompt = USER_PROMPT_TEMPLATE.format(
        original_cv_data=json.dumps(original_cv_data, indent=2),
        job_posting_data=json.dumps(job_posting_data, indent=2),
        output_language_full=output_language_full,
    )
    
    system_prompt = SYSTEM_PROMPT.format(output_language_full=output_language_full)
    
    # Get OpenRouter config
    use_openrouter = os.environ.get("USE_OPENROUTER", "false").lower() == "true"
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY", "")
    openrouter_model = os.environ.get("OPENROUTER_MODEL", "qwen/qwen-2.5-coder-32b-instruct:free")
    
    if use_openrouter and openrouter_api_key:
        # Use OpenRouter with configured model
        model = openrouter_model
        print(f"[LLM] Using OpenRouter model: {model}")
        
        try:
            response = await acompletion(
                model=f"openrouter/{model}",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                api_key=openrouter_api_key,
                temperature=0.3,
                timeout=300,  # Free models can be slow
            )
            
            result_text = response.choices[0].message.content
            print("[LLM] Response received, parsing JSON...")
            
            # Parse JSON from response
            cv_data = _parse_llm_json(result_text)
            
            return cv_data
            
        except Exception as e:
            print(f"[LLM] OpenRouter error: {str(e)}")
            raise RuntimeError(f"OpenRouter API call failed: {str(e)}")
    else:
        # Fallback to local LLM (llama.cpp)
        local_url = os.environ.get("LOCAL_LLM_URL", "http://localhost:1234")
        local_model = os.environ.get("LOCAL_LLM_MODEL", "Qwen3.6-27B-UD-Q5_K_XL.gguf")
        
        try:
            print(f"[LLM] Using local model: {local_model} at {local_url}")
            response = await acompletion(
                model=f"openai/{local_model}",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                api_base=f"{local_url}/v1",
                api_key="sk-xxx",
                temperature=0.3,
                timeout=600,
                extra_body={"thinking": {"enabled": False}},
            )
            
            result_text = response.choices[0].message.content
            print("[LLM] Response received, parsing JSON...")
            
            cv_data = _parse_llm_json(result_text)
            
            return cv_data
            
        except Exception as e:
            print(f"[LLM] Local LLM error: {str(e)}")
            raise RuntimeError(f"Local LLM API call failed: {str(e)}")


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
