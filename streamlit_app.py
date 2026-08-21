import os
import tempfile
import streamlit as st
from app.parser import ResumeParser
from app.analyzer import ResumeAnalyzer

# ---------- Page setup ----------
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="centered")

st.title("📄 AI Resume Analyzer")
st.caption("Upload a resume for AI analysis, and optionally match it against a job description.")

# ---------- Inputs ----------
uploaded_file = st.file_uploader(
    "Drag & drop the resume here, or click to browse",
    type=["pdf", "docx", "txt"],
    help="We accept PDF, DOCX, and TXT files."
)

st.subheader("🎯 Job Description (optional)")
job_description = st.text_area(
    "Paste a job description to get a match score",
    height=150,
    placeholder="e.g. Looking for a Python developer with FastAPI, SQL, and React experience..."
)

if uploaded_file is not None:
    st.success(f"Loaded: **{uploaded_file.name}**")

    if st.button("🚀 Analyze Resume", type="primary"):
        with st.spinner("AI is reading the resume..."):
            # Save uploaded file temporarily so the parser can read it
            temp_path = os.path.join(tempfile.gettempdir(), uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                parser = ResumeParser()
                parsed = parser.extract(temp_path)
                analyzer = ResumeAnalyzer()

                # 1. Resume analysis
                result = analyzer.analyze(parsed["text"])

                # 2. Job match (only if a job description was provided)
                match_result = None
                if job_description.strip():
                    match_result = analyzer.match_job(parsed["text"], job_description)

            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.stop()
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        # ================= RESULTS =================
        st.divider()

        # ----- Job Match -----
        if match_result:
            st.header("🎯 Job Match")
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("Match Score", f"{match_result.get('match_score', 0)}/100")
            with c2:
                st.write(f"**Verdict:** {match_result.get('verdict', 'N/A')}")

            mc1, mc2 = st.columns(2)
            with mc1:
                st.success("✅ Matched Skills")
                matched = match_result.get("matched_skills", [])
                st.markdown("  ".join([f"`{s}`" for s in matched]) or "_None detected_")
            with mc2:
                st.warning("❌ Missing Skills")
                missing = match_result.get("missing_skills", [])
                st.markdown("  ".join([f"`{s}`" for s in missing]) or "_None — great fit!_")

            suggestions = match_result.get("keyword_suggestions", [])
            if suggestions:
                st.subheader("💡 Keywords to Add")
                st.markdown("  ".join([f"`{s}`" for s in suggestions]))

            st.divider()

        # ----- Resume Analysis -----
        st.header("📄 Resume Analysis")
        col_score, col_info = st.columns([1, 2])
        with col_score:
            st.metric("Resume Score", f"{result.get('score', 0)}/100")
        with col_info:
            st.write(f"**Name:** {result.get('name', 'N/A')}")
            st.write(f"**Email:** {result.get('email', 'N/A')}")
            st.write(f"**Phone:** {result.get('phone', 'N/A')}")
            st.write(f"**Experience:** ~{result.get('experience_years', 0)} years")

        st.subheader("🛠️ Detected Skills")
        skills = result.get("skills", [])
        st.markdown("  ".join([f"`{s}`" for s in skills]) or "_No skills detected_")

        st.subheader("📝 AI Summary")
        st.info(result.get("summary", "No summary available."))

        with st.expander("🔍 View raw JSON"):
            st.json({"resume_analysis": result, "job_match": match_result})