import os
from pathlib import Path
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from auth import (
    render_auth_page,
    check_authentication
)

from file_utils import (
    extract_resume_text,
    validate_file_size
)

from usage_tracker import (
    get_remaining_usage,
    has_remaining_usage,
    increment_user_usage
)

from history_manager import (
    save_generation_history,
    load_user_history,
    get_total_generations,
    get_total_users
)

from feedback_manager import (
    save_feedback,
    load_feedback_data,
    get_total_feedback
)

from ats_engine import (
    run_resume_pipeline,
    clean_ats_score
)

from generate_documents import (
    generate_resume_docx,
    generate_cover_letter_docx
)

# =========================
# LOAD ENV
# =========================

load_dotenv()

# =========================
# CREATE DATA FOLDERS
# =========================

folders = [

    "data/usage",

    "data/feedback",

    "data/history",

    "outputs",

    "analysis"
]

for folder in folders:

    Path(folder).mkdir(
        parents=True,
        exist_ok=True
    )

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(

    page_title="AI Resume Automation",

    page_icon="📄",

    layout="wide"
)

# =========================
# AUTH
# =========================

authenticator, config = render_auth_page()

auth_data = check_authentication()

username = auth_data["username"]

name = auth_data["name"]

authentication_status = auth_data["authentication_status"]

# =========================
# SESSION STATE
# =========================

if "generated" not in st.session_state:

    st.session_state.generated = False

# =========================
# HEADER
# =========================

st.title(
    "📄 AI Resume Automation System"
)

st.markdown(
    f"Welcome **{name}**"
)

st.markdown(
    "Generate ATS-optimized recruiter-ready resumes and cover letters."
)

# =========================
# USAGE
# =========================

remaining_usage = get_remaining_usage(
    config,
    username
)

# =========================
# SIDEBAR
# =========================

with st.sidebar:

    st.header(
        "AI Resume Automation"
    )

    st.markdown(
        """
        ### Features

        - ATS Match Analysis
        - Resume Tailoring
        - Cover Letter Generation
        - DOCX Export
        - Recruiter Optimization
        - Achievement Rewriting
        - ATS Optimization Loop
        - Feedback Tracking
        - Usage Tracking
        - Generation History
        """
    )

    st.info(
        f"Daily Generations Left: {remaining_usage}"
    )

    st.divider()

    st.caption(
        "Built with Streamlit + OpenAI"
    )

    authenticator.logout(
        "Logout",
        "sidebar"
    )

# =========================
# INPUTS
# =========================

uploaded_resume = st.file_uploader(
    "Upload Resume",
    type=[
        "pdf",
        "docx",
        "txt"
    ]
)

if uploaded_resume:

    if not validate_file_size(
        uploaded_resume
    ):

        st.error(
            "Resume file too large. Maximum file size is 5MB."
        )

        st.stop()

job_description = st.text_area(
    "Paste Job Description",
    height=350
)

# =========================
# BUTTONS
# =========================

col1, col2 = st.columns([1, 1])

with col1:

    generate_clicked = st.button(
        "Generate Documents"
    )

with col2:

    if st.button(
        "New Analysis"
    ):

        st.session_state.clear()

        st.rerun()

# =========================
# MAIN PROCESS
# =========================

if generate_clicked:

    if not has_remaining_usage(
        config,
        username
    ):

        st.error(
            "Daily usage limit reached."
        )

        st.stop()

    if not uploaded_resume:

        st.warning(
            "Please upload a resume."
        )

        st.stop()

    if not job_description:

        st.warning(
            "Please paste a job description."
        )

        st.stop()

    resume_text = extract_resume_text(
        uploaded_resume
    )

    if not resume_text:

        st.error(
            "Could not process uploaded resume."
        )

        st.stop()

    try:

        with st.spinner(
            "Optimizing resume and generating documents..."
        ):

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            # =========================
            # RUN AI PIPELINE
            # =========================

            results = run_resume_pipeline(
                resume_text,
                job_description
            )

            tailored_resume = results[
                "tailored_resume"
            ]

            tailored_cover_letter = results[
                "tailored_cover_letter"
            ]

            original_ats_score = results[
                "original_ats_score"
            ]

            optimized_ats_score = results[
                "optimized_ats_score"
            ]

            matching_keywords = results[
                "matching_keywords"
            ]

            missing_keywords = results[
                "missing_keywords"
            ]

            job_fit_analysis = results[
                "job_fit_analysis"
            ]

            improvement_suggestions = results[
                "improvement_suggestions"
            ]

            # =========================
            # SAVE ANALYSIS
            # =========================

            analysis_filename = (
                f"analysis/ats_analysis_{timestamp}.txt"
            )

            analysis_content = f"""
ATS MATCH ANALYSIS

ORIGINAL ATS SCORE:
{original_ats_score}

OPTIMIZED ATS SCORE:
{optimized_ats_score}

MATCHING KEYWORDS:
{matching_keywords}

MISSING KEYWORDS:
{missing_keywords}

JOB FIT ANALYSIS:
{job_fit_analysis}

RESUME IMPROVEMENT SUGGESTIONS:
{improvement_suggestions}
"""

            with open(
                analysis_filename,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    analysis_content
                )

            # =========================
            # DOCX GENERATION
            # =========================

            resume_filename = (
                f"outputs/resume_{timestamp}.docx"
            )

            cover_letter_filename = (
                f"outputs/cover_letter_{timestamp}.docx"
            )

            resume_path = generate_resume_docx(
                tailored_resume,
                resume_filename
            )

            cover_letter_path = (
                generate_cover_letter_docx(
                    tailored_cover_letter,
                    cover_letter_filename
                )
            )

            # =========================
            # TRACKING
            # =========================

            increment_user_usage(
                username
            )

            save_generation_history(
                username,
                optimized_ats_score,
                job_description
            )

            # =========================
            # SESSION STATE
            # =========================

            st.session_state.tailored_resume = (
                tailored_resume
            )

            st.session_state.tailored_cover_letter = (
                tailored_cover_letter
            )

            st.session_state.resume_path = (
                resume_path
            )

            st.session_state.cover_letter_path = (
                cover_letter_path
            )

            st.session_state.timestamp = (
                timestamp
            )

            st.session_state.original_ats_score = (
                original_ats_score
            )

            st.session_state.optimized_ats_score = (
                optimized_ats_score
            )

            st.session_state.matching_keywords = (
                matching_keywords
            )

            st.session_state.missing_keywords = (
                missing_keywords
            )

            st.session_state.job_fit_analysis = (
                job_fit_analysis
            )

            st.session_state.improvement_suggestions = (
                improvement_suggestions
            )

            st.session_state.generated = True

    except Exception as error:

        st.error(
            f"Generation failed: {error}"
        )

        st.stop()

# =========================
# DISPLAY RESULTS
# =========================

if st.session_state.generated:

    st.success(
        "Documents generated successfully."
    )

    st.subheader(
        "ATS Match Analysis"
    )

    col1, col2 = st.columns(2)

    with col1:

        original_score = clean_ats_score(
            st.session_state.original_ats_score
        )

        optimized_score = clean_ats_score(
            st.session_state.optimized_ats_score
        )

        st.metric(
            "Original ATS Score",
            f"{original_score}%"
        )

        st.metric(
            "Optimized ATS Score",
            f"{optimized_score}%"
        )

        st.progress(
            optimized_score / 100
        )

        st.markdown(
            "### Matching Keywords"
        )

        st.write(
            st.session_state.matching_keywords
        )

    with col2:

        st.markdown(
            "### Missing Keywords"
        )

        st.write(
            st.session_state.missing_keywords
        )

    st.markdown(
        "### Job Fit Analysis"
    )

    st.write(
        st.session_state.job_fit_analysis
    )

    st.markdown(
        "### Resume Improvement Suggestions"
    )

    st.write(
        st.session_state.improvement_suggestions
    )

    st.divider()

    col1, col2 = st.columns(2)

    # =========================
    # RESUME
    # =========================

    with col1:

        st.subheader(
            "Tailored Resume"
        )

        with st.expander(
            "Preview Resume"
        ):

            st.text_area(
                "Resume Preview",
                st.session_state.tailored_resume,
                height=400,
                label_visibility="collapsed"
            )

        with open(
            st.session_state.resume_path,
            "rb"
        ) as file:

            st.download_button(
                "Download Resume",
                file,
                file_name=(
                    f"Resume_{st.session_state.timestamp}.docx"
                )
            )

    # =========================
    # COVER LETTER
    # =========================

    with col2:

        st.subheader(
            "Tailored Cover Letter"
        )

        with st.expander(
            "Preview Cover Letter"
        ):

            st.text_area(
                "Cover Letter Preview",
                st.session_state.tailored_cover_letter,
                height=400,
                label_visibility="collapsed"
            )

        with open(
            st.session_state.cover_letter_path,
            "rb"
        ) as file:

            st.download_button(
                "Download Cover Letter",
                file,
                file_name=(
                    f"Cover_Letter_{st.session_state.timestamp}.docx"
                )
            )

    # =========================
    # FEEDBACK
    # =========================

    st.divider()

    st.subheader(
        "Feedback"
    )

    feedback_type = st.radio(
        "Was this helpful?",
        [
            "Helpful",
            "Needs Improvement"
        ]
    )

    feedback_comment = st.text_area(
        "Additional Feedback"
    )

    if st.button(
        "Submit Feedback"
    ):

        save_feedback(
            username,
            feedback_type,
            feedback_comment
        )

        st.success(
            "Feedback submitted."
        )

# =========================
# HISTORY
# =========================

st.divider()

st.subheader(
    "My Generation History"
)

history = load_user_history(
    username
)

if len(history) == 0:

    st.info(
        "No previous generations found."
    )

else:

    for item in history[:10]:

        with st.expander(
            f"ATS Score: {item['ats_score']} | {item['timestamp']}"
        ):

            st.write(
                item["job_description_preview"]
            )

# =========================
# ADMIN DASHBOARD
# =========================

if username == "admin" and authentication_status:

    st.divider()

    st.subheader(
        "Admin Analytics Dashboard"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Users",
            get_total_users()
        )

    with col2:

        st.metric(
            "Total Generations",
            get_total_generations()
        )

    with col3:

        st.metric(
            "Total Feedback Entries",
            get_total_feedback()
        )

    feedback_data = load_feedback_data()

    st.divider()

    st.subheader(
        "Latest User Feedback"
    )

    if len(feedback_data) == 0:

        st.info(
            "No feedback yet."
        )

    else:

        for item in feedback_data[-5:]:

            with st.expander(
                f"{item['username']} - {item['feedback']}"
            ):

                st.write(
                    item["comment"]
                )

# =========================
# FOOTER
# =========================

st.divider()

st.caption(
    "AI Resume Automation System © 2026"
)