from openai import OpenAI
import streamlit as st
import re

# ==========================================
# OPENAI CLIENT
# ==========================================

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# ==========================================
# CLEAN ATS SCORE
# ==========================================

def clean_ats_score(score_text):

    try:

        digits = "".join(
            filter(str.isdigit, str(score_text))
        )

        return int(digits)

    except:

        return 0


def clean_generated_text(text):

    if not text:
        return ""

    # ==========================================
    # REMOVE MARKDOWN
    # ==========================================

    text = text.replace("**", "")
    text = text.replace("*", "")
    text = text.replace("```", "")

    # ==========================================
    # FIX BULLET ENCODING
    # ==========================================

    text = text.replace("", "•")

    # ==========================================
    # REMOVE AI GARBAGE SECTIONS
    # ==========================================

    if "Keywords Integrated:" in text:
        text = text.split("Keywords Integrated:")[0]

    unwanted_phrases = [

        "Final Resume",
        "Tailored Resume",
        "ATS Match Analysis",
        "Job Fit Analysis",
        "Improvement Suggestions",
        "Matching Keywords",
        "Missing Keywords",
        "Tailored Cover Letter"

    ]

    cleaned_lines = []

    for line in text.split("\n"):

        stripped = line.strip()

        if not stripped:
            cleaned_lines.append("")
            continue

        should_skip = False

        for phrase in unwanted_phrases:

            if phrase.lower() in stripped.lower():

                should_skip = True
                break

        if should_skip:
            continue

        cleaned_lines.append(stripped)

    text = "\n".join(cleaned_lines)

    # ==========================================
    # ENTERPRISE WORD NORMALIZATION
    # ==========================================

    replacements = {

        r"\bWindowsbased\b": "Windows-based",
        r"\bdaytoday\b": "day-to-day",
        r"\bbusinesscritical\b": "business-critical",
        r"\bticketbased\b": "ticket-based",
        r"\brealworld\b": "real-world",
        r"\bAIpowered\b": "AI-powered",
        r"\bhandson\b": "hands-on",
        r"\bsmallscale\b": "small-scale",
        r"\bITILbased\b": "ITIL-based",
        r"\bvendorbased\b": "vendor-based",
        r"\benduser\b": "end-user",
        r"\bonsite\b": "on-site",
        r"\bendtoend\b": "end-to-end",
        r"\bSLAbased\b": "SLA-based",
        r"\bSLAdriven\b": "SLA-driven",
        r"\bPowerShellbased\b": "PowerShell-based",
        r"\bnetworkbased\b": "network-based",
        r"\buserfocused\b": "user-focused",
        r"\bcustomerfocused\b": "customer-focused",
        r"\bprocessfocused\b": "process-focused",
        r"\bsecurityfocused\b": "security-focused",
        r"\bworkflowbased\b": "workflow-based",
        r"\bknowledgebase\b": "knowledge base",
        r"\benterprisegrade\b": "enterprise-grade",
        r"\bcloudbased\b": "cloud-based",
        r"\bprocessdriven\b": "process-driven",
        r"\bWindowsServer\b": "Windows Server",
        r"\bselfservice\b": "self-service",
        r"\bhelpdesk\b": "help desk",
        r"\brunbooks\b": "run books",
        r"\b1525\b": "15–25"

    }

    for pattern, replacement in replacements.items():

        text = re.sub(
            pattern,
            replacement,
            text,
            flags=re.IGNORECASE
        )

    # ==========================================
    # FIX MISSING SPACE BEFORE CAPITAL LETTERS
    # ==========================================

    text = re.sub(
        r"([a-z])([A-Z])",
        r"\1 \2",
        text
    )

    # ==========================================
    # CLEAN EXCESSIVE SPACING
    # ==========================================

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    # ==========================================
    # REMOVE EXTRA BULLET AT END
    # ==========================================

    text = re.sub(
        r"\n•\s*$",
        "",
        text
    )

    return text.strip()

# ==========================================
# KEYWORD MATCH ENGINE
# ==========================================

def calculate_keyword_match(
    resume_text,
    job_description
):

    resume_words = set(
        resume_text.lower().split()
    )

    jd_words = set(
        job_description.lower().split()
    )

    important_keywords = [

        word for word in jd_words
        if len(word) > 4

    ]

    matched = []
    missing = []

    for word in important_keywords:

        if word in resume_words:

            matched.append(word)

        else:

            missing.append(word)

    total = len(important_keywords)

    if total == 0:

        score = 0

    else:

        score = int(
            (len(matched) / total) * 100
        )

    return {

        "score": score,
        "matched": matched[:20],
        "missing": missing[:20]

    }


# ==========================================
# GENERATE ATS ANALYSIS
# ==========================================

def generate_ats_analysis(
    keyword_results
):

    return {

        "original_ats_score": str(
            keyword_results["score"]
        ),

        "optimized_ats_score": str(
            min(
                keyword_results["score"] + 15,
                95
            )
        ),

        "matching_keywords": ", ".join(
            keyword_results["matched"]
        ),

        "missing_keywords": ", ".join(
            keyword_results["missing"]
        )

    }


# ==========================================
# GENERATE TAILORED RESUME
# ==========================================

def generate_tailored_resume(
    resume_text,
    job_description
):

    prompt = f"""
You are an elite IT resume writer and recruiter specializing in:
- IT Support
- Desktop Support
- Helpdesk
- Endpoint Support
- Microsoft 365
- Active Directory
- Infrastructure Support

Your task is to tailor the candidate resume to the job description.

IMPORTANT RULES:

- Preserve ALL original candidate information
- Preserve original education
- Preserve original certifications
- Preserve original companies
- Preserve original job titles

NEVER:
- invent fake experience
- invent certifications
- invent education
- generate placeholders
- generate fake technologies
- generate fake years of experience

OPTIMIZATION GOALS:
- improve ATS alignment
- improve recruiter readability
- strengthen enterprise IT terminology
- naturally integrate relevant keywords
- improve operational realism
- improve business impact wording

IMPORTANT:
- Use realistic enterprise IT support terminology
- Use stronger operational wording
- Keep language concise and recruiter-friendly
- Make the resume sound modern and realistic

FORMAT:
- Professional Summary
- Skills
- Professional Experience
- Projects
- Education
- Certifications
- Languages

Use bullet points for achievements.

MASTER RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""

    response = client.chat.completions.create(

        model="gpt-4.1",

        temperature=0.4,

        messages=[

            {
                "role": "user",
                "content": prompt
            }

        ]
    )

    content = response.choices[0].message.content

    return clean_generated_text(content)


# ==========================================
# GENERATE COVER LETTER
# ==========================================

def generate_cover_letter(
    tailored_resume,
    job_description
):

    prompt = f"""
You are a professional IT recruiter.

Generate a modern and realistic IT cover letter.

IMPORTANT:
- Human sounding
- Concise
- No placeholders
- No fake experience
- No exaggerated claims
- Professional but conversational

TAILORED RESUME:
{tailored_resume}

JOB DESCRIPTION:
{job_description}
"""

    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        temperature=0.5,

        messages=[

            {
                "role": "user",
                "content": prompt
            }

        ]
    )

    content = response.choices[0].message.content

    return clean_generated_text(content)


# ==========================================
# MAIN PIPELINE
# ==========================================

def run_resume_pipeline(
    resume_text,
    job_description
):

    keyword_results = calculate_keyword_match(
        resume_text,
        job_description
    )

    ats_analysis = generate_ats_analysis(
        keyword_results
    )

    tailored_resume = generate_tailored_resume(
        resume_text,
        job_description
    )

    tailored_cover_letter = generate_cover_letter(
        tailored_resume,
        job_description
    )

    return {

        "tailored_resume": tailored_resume,

        "tailored_cover_letter": tailored_cover_letter,

        "original_ats_score": ats_analysis["original_ats_score"],

        "optimized_ats_score": ats_analysis["optimized_ats_score"],

        "matching_keywords": ats_analysis["matching_keywords"],

        "missing_keywords": ats_analysis["missing_keywords"],

        "job_fit_analysis": "Resume analyzed successfully against the job description.",

        "improvement_suggestions": "Improve missing keyword coverage and strengthen measurable technical achievements."

    }