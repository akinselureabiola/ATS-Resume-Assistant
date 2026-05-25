import json
from pathlib import Path
from datetime import datetime
import os
import bcrypt

import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader

import streamlit as st

from dotenv import load_dotenv
from openai import OpenAI

from pypdf import PdfReader
from docx import Document

from system_prompts import (
    ATS_ANALYSIS_PROMPT,
    RESUME_GENERATION_PROMPT,
    COVER_LETTER_PROMPT
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
# OPENAI CLIENT
# =========================

import streamlit as st
from openai import OpenAI

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
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
# LOAD AUTH CONFIG
# =========================

with open(
    "auth_config.yaml",
    "r"
) as file:

    config = yaml.load(
        file,
        Loader=SafeLoader
    )

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# =========================
# SIGNUP SYSTEM
# =========================

def save_user(
    name,
    email,
    username,
    password
):

    hashed_password = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

    config["credentials"]["usernames"][username] = {
        "email": email,
        "name": name,
        "password": hashed_password,
        "role": "user",
        "daily_limit": 5
    }

    with open(
        "users.yaml",
        "w"
    ) as file:

        yaml.dump(
            config,
            file,
            default_flow_style=False
        )

# =========================
# AUTH TABS
# =========================

login_tab, signup_tab = st.tabs(
    [
        "Login",
        "Sign Up"
    ]
)

# =========================
# LOGIN TAB
# =========================

with login_tab:

    authenticator.login()

# =========================
# SIGNUP TAB
# =========================

with signup_tab:

    st.subheader(
        "Create Account"
    )

    signup_name = st.text_input(
        "Full Name"
    )

    signup_email = st.text_input(
        "Email"
    )

    signup_username = st.text_input(
        "Username"
    )

    signup_password = st.text_input(
        "Password",
        type="password"
    )

    signup_confirm_password = st.text_input(
        "Confirm Password",
        type="password"
    )

    if st.button(
        "Create Account"
    ):

        existing_emails = [

            user_data["email"]

            for user_data in config["credentials"]["usernames"].values()
        ]

        if not signup_name:

            st.error(
                "Please enter full name."
            )

        elif not signup_email:

            st.error(
                "Please enter email."
            )

        elif not signup_username:

            st.error(
                "Please enter username."
            )

        elif not signup_password:

            st.error(
                "Please enter password."
            )

        elif (
            signup_username
            in config["credentials"]["usernames"]
        ):

            st.error(
                "Username already exists."
            )

        elif signup_email in existing_emails:

            st.error(
                "Email already exists."
            )

        elif (
            signup_password
            != signup_confirm_password
        ):

            st.error(
                "Passwords do not match."
            )

        else:

            save_user(
                signup_name,
                signup_email,
                signup_username,
                signup_password
            )

            st.success(
                "Account created successfully."
            )

            st.info(
                "Refresh the page and login."
            )

# =========================
# AUTH STATUS
# =========================

authentication_status = st.session_state.get(
    "authentication_status"
)

name = st.session_state.get(
    "name"
)

username = st.session_state.get(
    "username"
)

if authentication_status is False:

    st.error(
        "Incorrect username or password."
    )

    st.stop()

if authentication_status is None:

    st.warning(
        "Please login to continue."
    )

    st.stop()

# =========================
# SESSION STATE
# =========================

if "generated" not in st.session_state:

    st.session_state.generated = False

# =========================
# USAGE LIMIT SYSTEM
# =========================

DAILY_LIMIT = 9999

def get_usage_file(username):

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    return (
        f"data/usage/{username}_{today}.json"
    )

def get_user_usage(username):

    usage_file = get_usage_file(
        username
    )

    if os.path.exists(usage_file):

        with open(
            usage_file,
            "r"
        ) as file:

            data = json.load(file)

            return data.get(
                "generations",
                0
            )

    return 0

def increment_user_usage(username):

    usage_file = get_usage_file(
        username
    )

    current_usage = get_user_usage(
        username
    )

    data = {
        "username": username,
        "generations": current_usage + 1
    }

    with open(
        usage_file,
        "w"
    ) as file:

        json.dump(
            data,
            file,
            indent=2
        )

# =========================
# SAVE HISTORY
# =========================

def save_generation_history(
    username,
    ats_score,
    job_description
):

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    history_data = {
        "username": username,
        "timestamp": timestamp,
        "ats_score": ats_score,
        "job_description_preview": (
            job_description[:300]
        )
    }

    history_file = (
        f"data/history/{username}_{timestamp}.json"
    )

    with open(
        history_file,
        "w"
    ) as file:

        json.dump(
            history_data,
            file,
            indent=2
        )

# =========================
# LOAD USER HISTORY
# =========================

def load_user_history(username):

    history_files = sorted(
        os.listdir("data/history"),
        reverse=True
    )

    user_history = []

    for file in history_files:

        if file.startswith(username):

            file_path = (
                f"data/history/{file}"
            )

            with open(
                file_path,
                "r"
            ) as history_file:

                data = json.load(
                    history_file
                )

                user_history.append(
                    data
                )

    return user_history

# =========================
# FEEDBACK SYSTEM
# =========================

def save_feedback(
    username,
    feedback_type,
    feedback_comment
):

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    feedback_data = {
        "username": username,
        "timestamp": timestamp,
        "feedback": feedback_type,
        "comment": feedback_comment
    }

    feedback_file = (
        f"data/feedback/{username}_{timestamp}.json"
    )

    with open(
        feedback_file,
        "w"
    ) as file:

        json.dump(
            feedback_data,
            file,
            indent=2
        )

def load_feedback_data():

    feedback_files = os.listdir(
        "data/feedback"
    )

    feedback_data = []

    for file in feedback_files:

        file_path = (
            f"data/feedback/{file}"
        )

        with open(
            file_path,
            "r"
        ) as feedback_file:

            data = json.load(
                feedback_file
            )

            feedback_data.append(
                data
            )

    return feedback_data

# =========================
# ADMIN ANALYTICS
# =========================

def get_total_generations():

    return len(
        os.listdir("data/history")
    )

def get_total_feedback():

    return len(
        os.listdir("data/feedback")
    )

def get_total_users():

    users = set()

    for file in os.listdir(
        "data/history"
    ):

        username = file.split("_")[0]

        users.add(username)

    return len(users)

# =========================
# HELPERS
# =========================

def clean_ats_score(score_text):

    try:

        digits = "".join(
            filter(str.isdigit, score_text)
        )

        return int(digits)

    except:

        return 0

def extract_text_from_pdf(file):

    reader = PdfReader(file)

    text = ""

    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:

            text += extracted + "\n"

    return text

def extract_text_from_docx(file):

    doc = Document(file)

    text = []

    for paragraph in doc.paragraphs:

        text.append(paragraph.text)

    return "\n".join(text)

def extract_resume_text(uploaded_file):

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".txt"):

        return uploaded_file.read().decode(
            "utf-8"
        )

    elif file_name.endswith(".pdf"):

        return extract_text_from_pdf(
            uploaded_file
        )

    elif file_name.endswith(".docx"):

        return extract_text_from_docx(
            uploaded_file
        )

    else:

        return None

def extract_section(
    text,
    start,
    end=None
):

    try:

        if end:

            return (
                text
                .split(start)[1]
                .split(end)[0]
                .strip()
            )

        return (
            text
            .split(start)[1]
            .strip()
        )

    except:

        return "Not available"

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
# SIDEBAR
# =========================

current_usage = get_user_usage(
    username
)

remaining_usage = max(
    DAILY_LIMIT - current_usage,
    0
)

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

    file_size_mb = (
        uploaded_resume.size / 1024 / 1024
    )

    if file_size_mb > 5:

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

    if current_usage >= DAILY_LIMIT:

        st.error(
            "Daily usage limit reached."
        )

        st.stop()

    if not uploaded_resume:

        st.warning(
            "Please upload a resume."
        )

    elif not job_description:

        st.warning(
            "Please paste a job description."
        )

    else:

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
                "Generating recruiter-ready documents..."
            ):

                timestamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )

                ats_prompt = f"""
RESUME:

{resume_text}

JOB DESCRIPTION:

{job_description}
"""

                ats_response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": ATS_ANALYSIS_PROMPT
                        },
                        {
                            "role": "user",
                            "content": ats_prompt
                        }
                    ],
                    temperature=0.4
                )

                ats_output = (
                    ats_response
                    .choices[0]
                    .message
                    .content
                )

                ats_score = extract_section(
                    ats_output,
                    "===ATS_SCORE===",
                    "===MATCHING_KEYWORDS==="
                )

                matching_keywords = extract_section(
                    ats_output,
                    "===MATCHING_KEYWORDS===",
                    "===MISSING_KEYWORDS==="
                )

                missing_keywords = extract_section(
                    ats_output,
                    "===MISSING_KEYWORDS===",
                    "===JOB_FIT_ANALYSIS==="
                )

                job_fit_analysis = extract_section(
                    ats_output,
                    "===JOB_FIT_ANALYSIS===",
                    "===IMPROVEMENT_SUGGESTIONS==="
                )

                improvement_suggestions = extract_section(
                    ats_output,
                    "===IMPROVEMENT_SUGGESTIONS==="
                )

                resume_prompt = f"""
MASTER RESUME:

{resume_text}

JOB DESCRIPTION:

{job_description}
"""

                resume_response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": RESUME_GENERATION_PROMPT
                        },
                        {
                            "role": "user",
                            "content": resume_prompt
                        }
                    ],
                    temperature=0.7
                )

                tailored_resume = (
                    resume_response
                    .choices[0]
                    .message
                    .content
                    .replace(
                        "Final Resume",
                        ""
                    )
                    .strip()
                )

                cover_prompt = f"""
MASTER RESUME:

{resume_text}

JOB DESCRIPTION:

{job_description}
"""

                cover_response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": COVER_LETTER_PROMPT
                        },
                        {
                            "role": "user",
                            "content": cover_prompt
                        }
                    ],
                    temperature=0.7
                )

                tailored_cover_letter = (
                    cover_response
                    .choices[0]
                    .message
                    .content
                    .replace(
                        "Final Cover Letter",
                        ""
                    )
                    .strip()
                )

            analysis_filename = (
                f"analysis/ats_analysis_{timestamp}.txt"
            )

            analysis_content = f"""
ATS MATCH ANALYSIS

Estimated ATS Match Score:
{ats_score}

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

            cover_letter_path = generate_cover_letter_docx(
                tailored_cover_letter,
                cover_letter_filename
            )

            increment_user_usage(
                username
            )

            save_generation_history(
                username,
                ats_score,
                job_description
            )

            st.session_state.tailored_resume = tailored_resume

            st.session_state.tailored_cover_letter = (
                tailored_cover_letter
            )

            st.session_state.resume_path = resume_path

            st.session_state.cover_letter_path = (
                cover_letter_path
            )

            st.session_state.timestamp = timestamp

            st.session_state.ats_score = ats_score

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

        clean_score = clean_ats_score(
            st.session_state.ats_score
        )

        st.metric(
            "Estimated ATS Match Score",
            f"{clean_score}%"
        )

        st.progress(
            clean_score / 100
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
# USER HISTORY
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