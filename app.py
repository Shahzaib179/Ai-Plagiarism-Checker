import streamlit as st
from analyzer import analyze_document, extract_document_text

st.set_page_config(page_title="AI Plagiarism Checker", page_icon="🔎", layout="wide")

st.title("🔎 AI Plagiarism Checker")
st.caption("Analyze text for plagiarism indicators, grammar issues, humanization, and ATS keywords.")

with st.sidebar:
    st.header("Settings")
    model = st.text_input("Groq model", value="openai/gpt-oss-120b")
    max_sources = st.slider("Maximum web sources", 1, 8, 5)
    st.info("Set GROQ_API_KEY in .env before running the app.")

uploaded = st.file_uploader("Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])
text_input = st.text_area("Or paste your content", height=220, placeholder="Paste English content here...")
job_description = st.text_area(
    "Optional job description for ATS analysis",
    height=160,
    placeholder="Paste a job description here if this is a resume/CV..."
)

if uploaded:
    try:
        content = extract_document_text(uploaded)
        st.success(f"Extracted {len(content.split())} words from {uploaded.name}.")
    except Exception as exc:
        st.error(f"Could not extract the file: {exc}")
        content = ""
else:
    content = text_input.strip()

if st.button("Analyze Content", type="primary", use_container_width=True):
    if not content.strip():
        st.warning("Please upload a document or paste some text.")
        st.stop()

    with st.spinner("Analyzing content..."):
        try:
            result = analyze_document(
                content=content,
                job_description=job_description,
                model=model,
                max_sources=max_sources,
            )
        except Exception as exc:
            st.error(str(exc))
            st.stop()

    st.subheader("Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Plagiarism indicator", f"{result['plagiarism']['score']}%")
    c2.metric("Original indicator", f"{result['plagiarism']['originality_score']}%")
    c3.metric("Grammar issues", str(len(result["grammar"]["issues"])))

    tabs = st.tabs([
        "🔍 Plagiarism",
        "✍️ Grammar",
        "🧑 Humanized",
        "📊 ATS",
        "✨ Final Content",
        "🧾 Raw JSON",
    ])

    with tabs[0]:
        st.write(result["plagiarism"]["summary"])
        if result["plagiarism"]["matches"]:
            for match in result["plagiarism"]["matches"]:
                st.markdown(f"**Match:** {match['text']}")
                st.write(f"Similarity: {match['similarity']}%")
                if match.get("source"):
                    st.write(f"Source: {match['source']}")
        else:
            st.info("No strong matching passages were identified by the configured checker.")

        if result["plagiarism"]["sources"]:
            st.markdown("**Sources**")
            for source in result["plagiarism"]["sources"]:
                title = source.get("title") or source.get("url")
                url = source.get("url")
                if url:
                    st.markdown(f"- [{title}]({url})")
                else:
                    st.markdown(f"- {title}")

    with tabs[1]:
        if not result["grammar"]["issues"]:
            st.success("No significant grammar issues were identified.")
        for issue in result["grammar"]["issues"]:
            st.markdown(
                f"**{issue['type']}** — `{issue['original']}` → `{issue['correction']}`"
            )
            if issue.get("explanation"):
                st.caption(issue["explanation"])

    with tabs[2]:
        st.text_area("Humanized content", result["humanized_content"], height=450)

    with tabs[3]:
        st.metric("ATS keyword match", f"{result['ats']['score']}%")
        st.write("**Detected keywords:**", ", ".join(result["ats"]["detected_keywords"]) or "None")
        st.write("**Recommended keywords:**", ", ".join(result["ats"]["recommended_keywords"]) or "None")
        if result["ats"].get("notes"):
            st.write(result["ats"]["notes"])

    with tabs[4]:
        st.text_area("Final improved content", result["final_content"], height=550)
        st.download_button(
            "Download final content",
            result["final_content"],
            file_name="final_content.txt",
            mime="text/plain",
        )

    with tabs[5]:
        st.json(result)
