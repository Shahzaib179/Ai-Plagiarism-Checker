# AI Plagiarism Checker

A modular Streamlit application that accepts PDF, DOCX, TXT, or pasted text and produces structured analysis using the Groq API.

## Features

- PDF, DOCX, and TXT text extraction
- AI-assisted plagiarism/similarity assessment
- Optional public web search leads for similarity checking
- Grammar and writing issue detection
- Natural humanized rewrite
- ATS keyword analysis with an optional job description
- Final improved content
- Structured JSON output
- Download final content as TXT

## Important limitation

This project does **not** provide a certified internet-wide plagiarism score. The web-search component retrieves public search-result leads and the AI evaluates the evidence available to it. Search coverage, indexing, snippets, and query selection can miss sources. A production plagiarism product should integrate a dedicated plagiarism database/API and preserve source evidence.

The "humanized" feature is intended to improve clarity and natural writing. It is not designed to bypass plagiarism or AI-detection systems.

## Requirements

- Python 3.10+
- A Groq API key
- Internet access for the Groq API and optional web search

## Setup

### 1. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the API key

Copy `.env.example` to `.env`:

Windows:

```powershell
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder with your Groq API key:

```text
GROQ_API_KEY=your_actual_key
```

Never commit `.env` to GitHub.

### 4. Run

```bash
streamlit run app.py
```

The terminal will show the local Streamlit URL.

## How the application works

```text
Upload/Paste
    ↓
Text Extraction
    ↓
Web Search Leads
    ↓
Groq Structured JSON Analysis
    ↓
Parser / Validation
    ↓
Streamlit Results
```

The main responsibilities are separated:

- `app.py` — UI and user interaction
- `analyzer.py` — extraction, web-search integration, and Groq orchestration
- `checker_parser.py` — validation/normalization of AI JSON
- `prompts.py` — AI prompt and output schema
- `requirements.txt` — dependencies
- `.env.example` — environment variable template
- `.gitignore` — files that should not be committed

## GitHub

Create a new GitHub repository, then from the project directory:

```bash
git init
git add .
git commit -m "Initial AI plagiarism checker"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Do not upload `.env`.

## Streamlit deployment

1. Push the project to GitHub.
2. Open Streamlit Community Cloud.
3. Create a new app.
4. Select your GitHub repository and `app.py`.
5. Deploy.
6. Open the app's Secrets settings.
7. Add:

```toml
GROQ_API_KEY = "your_actual_groq_api_key"
```

The application uses `os.getenv("GROQ_API_KEY")`, so the Streamlit secret is exposed to the app as an environment variable.

## Recommended production improvements

For a serious plagiarism-checking service, replace the lightweight public web-search component with a licensed plagiarism/similarity API or database. Add rate limiting, authentication, document-size limits, caching, privacy controls, logging without storing document contents, and stronger source-level evidence handling.
