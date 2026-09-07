import io
import json
import os
import re
from typing import Any, Dict

from dotenv import load_dotenv
from docx import Document
from pypdf import PdfReader
from groq import Groq

from checker_parser import parse_analysis
from prompts import build_analysis_prompt

load_dotenv()


def extract_document_text(uploaded_file) -> str:
    """Extract text from a Streamlit UploadedFile."""
    name = uploaded_file.name.lower()
    data = uploaded_file.getvalue()

    if name.endswith(".txt"):
        return data.decode("utf-8", errors="replace").strip()

    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        return "\n\n".join((page.extract_text() or "") for page in reader.pages).strip()

    if name.endswith(".docx"):
        document = Document(io.BytesIO(data))
        paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
        return "\n".join(paragraphs).strip()

    raise ValueError("Unsupported file type. Use PDF, DOCX, or TXT.")


def _basic_web_search(query: str, max_results: int = 5):
    """
    Optional public web search using DuckDuckGo HTML.

    This is deliberately isolated from the AI layer. If it is unavailable,
    the app still performs AI-based similarity analysis.
    """
    try:
        import requests
        from bs4 import BeautifulSoup

        response = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        for item in soup.select(".result"):
            link = item.select_one(".result__a")
            snippet = item.select_one(".result__snippet")
            if not link:
                continue
            results.append({
                "title": link.get_text(" ", strip=True),
                "url": link.get("href", ""),
                "snippet": snippet.get_text(" ", strip=True) if snippet else "",
            })
            if len(results) >= max_results:
                break
        return results
    except Exception:
        return []


def _search_queries(content: str, max_sources: int):
    sentences = [
        s.strip()
        for s in re.split(r"(?<=[.!?])\s+", content)
        if len(s.split()) >= 8
    ]
    queries = []
    for sentence in sentences[:max_sources]:
        words = sentence.split()
        query = " ".join(words[:18])
        if query:
            queries.append(query)
    return queries


def _call_groq(prompt: str, model: str) -> Dict[str, Any]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Copy .env.example to .env and add your Groq API key."
        )

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful text-analysis assistant. Return only valid JSON "
                    "matching the requested schema. Do not invent sources or factual claims."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )
    return json.loads(response.choices[0].message.content)


def analyze_document(content: str, job_description: str = "", model: str = "llama-3.3-70b-versatile", max_sources: int = 5):
    if len(content.strip()) < 20:
        raise ValueError("Please provide at least 20 characters of content.")

    web_sources = []
    for query in _search_queries(content, max_sources):
        web_sources.extend(_basic_web_search(query, 1))

    prompt = build_analysis_prompt(
        content=content,
        job_description=job_description,
        web_sources=web_sources[:max_sources],
    )

    raw = _call_groq(prompt, model)
    return parse_analysis(raw, original_content=content)
