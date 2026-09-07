from typing import Any, Dict, List


def _number(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _text(value):
    return "" if value is None else str(value)


def parse_analysis(data: Dict[str, Any], original_content: str) -> Dict[str, Any]:
    """Validate and normalize the structured response returned by the AI layer."""
    plagiarism = data.get("plagiarism", {})
    grammar = data.get("grammar", {})
    ats = data.get("ats", {})

    matches: List[Dict[str, Any]] = []
    for item in plagiarism.get("matches", []) or []:
        matches.append({
            "text": _text(item.get("text")),
            "similarity": round(max(0, min(100, _number(item.get("similarity")))), 1),
            "source": _text(item.get("source")),
        })

    issues = []
    for item in grammar.get("issues", []) or []:
        issues.append({
            "type": _text(item.get("type")),
            "original": _text(item.get("original")),
            "correction": _text(item.get("correction")),
            "explanation": _text(item.get("explanation")),
        })

    sources = []
    for item in plagiarism.get("sources", []) or []:
        if isinstance(item, dict):
            sources.append({
                "title": _text(item.get("title")),
                "url": _text(item.get("url")),
            })

    plagiarism_score = round(max(0, min(100, _number(plagiarism.get("score")))), 1)
    originality = round(max(0, min(100, _number(plagiarism.get("originality_score", 100 - plagiarism_score)))), 1)

    ats_score = round(max(0, min(100, _number(ats.get("score")))), 1)

    return {
        "plagiarism": {
            "score": plagiarism_score,
            "originality_score": originality,
            "summary": _text(plagiarism.get("summary")),
            "matches": matches,
            "sources": sources,
        },
        "grammar": {
            "issues": issues,
            "summary": _text(grammar.get("summary")),
        },
        "humanized_content": _text(data.get("humanized_content")),
        "ats": {
            "score": ats_score,
            "detected_keywords": [
                _text(x) for x in (ats.get("detected_keywords", []) or []) if _text(x)
            ],
            "recommended_keywords": [
                _text(x) for x in (ats.get("recommended_keywords", []) or []) if _text(x)
            ],
            "notes": _text(ats.get("notes")),
        },
        "final_content": _text(data.get("final_content")),
    }
