import json


def build_analysis_prompt(content: str, job_description: str, web_sources: list) -> str:
    schema = {
        "plagiarism": {
            "score": 0,
            "originality_score": 100,
            "summary": "",
            "matches": [
                {"text": "", "similarity": 0, "source": ""}
            ],
            "sources": [
                {"title": "", "url": ""}
            ]
        },
        "grammar": {
            "summary": "",
            "issues": [
                {
                    "type": "grammar|spelling|punctuation|style",
                    "original": "",
                    "correction": "",
                    "explanation": ""
                }
            ]
        },
        "humanized_content": "",
        "ats": {
            "score": 0,
            "detected_keywords": [],
            "recommended_keywords": [],
            "notes": ""
        },
        "final_content": ""
    }

    sources_context = json.dumps(web_sources, ensure_ascii=False)
    return f"""
Analyze the user's content carefully.

IMPORTANT PLAGIARISM RULE:
- Treat web search results only as leads/evidence for possible similarity.
- Never claim that a source matches unless the supplied search-result snippet actually supports the claim.
- Do not invent URLs, titles, quotations, or sources.
- The plagiarism score is an indicator, not legal proof of plagiarism.
- If evidence is weak or absent, keep the score conservative and explain the limitation.
- Do not label common phrases as plagiarism.

GRAMMAR:
Identify meaningful grammar, spelling, punctuation, and style problems. Do not invent errors.

HUMANIZATION:
Rewrite the content naturally while preserving meaning, facts, numbers, names, and technical terminology. Do not optimize for evading plagiarism detectors.

ATS:
If a job description is supplied, compare the content against it. Recommend only relevant keywords. Never claim the user has a skill that is not supported by their content.

FINAL CONTENT:
Create a polished version based on the original content, grammar corrections, humanized wording, and relevant ATS suggestions. Do not add unsupported qualifications or facts.

Return ONLY JSON using exactly this structure:
{json.dumps(schema, indent=2)}

WEB SEARCH LEADS:
{sources_context}

JOB DESCRIPTION:
{job_description or "(none supplied)"}

USER CONTENT:
{content}
""".strip()
