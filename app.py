"""
AI Career Assistant
Analyzes your resume against a job description and generates:
- Match score and gap analysis
- Tailored resume sections
- ATS-optimized cover letter
- Interview prep topics
"""

import os
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI
from docx import Document


# Setup

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def print_header(title: str) -> None:
    print(f"\n{'=' * 40}")
    print(f"  {title}")
    print(f"{'=' * 40}\n")


def load_resume(filepath: str = "resume.txt") -> str:
    """Load resume from a text file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: '{filepath}' not found. Make sure it's in the same directory.")
        exit(1)


def get_job_description() -> str:
    # Get job description from terminal
    print("Paste the job description below.")
    print("When finished, type END on a new line.\n")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


def build_prompt(resume_text, job_description):
    return f"""
Analyze the candidate's resume against the provided job description.
Return your response in the EXACT format below — use the section delimiters as shown.

===TAILORED_RESUME===

RESUME MATCH ANALYSIS

1. REALISTIC MATCH SCORE
Give a realistic percentage match with a brief explanation.

2. STRONGEST MATCHING SKILLS
- skill 1
- skill 2

3. IMPORTANT ATS KEYWORDS
- keyword 1
- keyword 2

4. MISSING OR WEAK AREAS
- missing skill 1
- missing skill 2

5. TAILORED PROFESSIONAL SUMMARY
Generate:
- A stronger ATS-optimized professional summary
- Specifically tailored to this role
- 4–6 lines long
- Realistic and human-sounding
- Emphasizing transferable skills honestly
- Aligned with the job description

6. TAILORED SKILLS SECTION
Generate a more optimized ATS-friendly skills section based on the role.

6A. TAILORED EXPERIENCE BULLETS
Rewrite the candidate's existing experience bullets to better align with the job description.
Requirements:
- Keep all experience realistic and truthful
- Improve ATS keyword alignment
- Use stronger action verbs
- Keep bullets concise and professional
- Do not invent technologies not mentioned in the original resume

7. RESUME IMPROVEMENT SUGGESTIONS
Give practical, specific improvements.

8. LIKELY RECRUITER CONCERNS
List realistic concerns a recruiter might flag.

9. INTERVIEW TOPICS TO PREPARE
- topic 1
- topic 2

===TAILORED_COVER_LETTER===

10. TAILORED COVER LETTER
Generate a realistic cover letter tailored to the role.
Requirements:
- Sound natural and human — avoid robotic AI language
- Professional but conversational tone
- Length: 300–450 words
- Highlight transferable technical skills honestly
- Explain motivation for the role naturally
- Reference relevant technologies from the job description
- Emphasize problem-solving, troubleshooting, and adaptability
- Do NOT invent fake experience or exaggerate qualifications
- Structure: introduction, body paragraphs, and conclusion

===CAREER_ANALYSIS===

11. SHOULD THIS CANDIDATE APPLY?
Give honest, practical advice. Consider experience level, skill gaps, and role fit.


CANDIDATE RESUME

{resume_text}

JOB DESCRIPTION

{job_description}
"""


SYSTEM_PROMPT = """
You are an experienced IT recruiter, ATS optimization specialist, and career advisor.

Core behavior rules:
1. Prioritize honesty and realism over sounding impressive.
2. Never exaggerate candidate experience or invent qualifications.
3. Write naturally — like a thoughtful, knowledgeable person, not a chatbot.
4. Avoid corporate buzzwords, generic motivational language, and repetitive AI phrasing.
5. Keep writing professional but grounded and human.
6. Vary sentence structure naturally.
7. Tailor tone to context: warm for cover letters, clear and direct for resume tips, honest for match analysis.
8. Keep ATS optimization realistic and truthful.
9. Do not fabricate technologies, certifications, or work experience.
10. Explain skill gaps honestly and constructively.
11. Make cover letters sound authentic and believable — like a real candidate wrote them.
12. Prioritize practical usefulness over polished-sounding output.
"""


def call_openai(prompt: str) -> str:
    """Send the prompt to OpenAI and return the response text."""
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content


def parse_sections(analysis: str) -> tuple[str, str, str]:
    """
    Split the AI response into three sections.
    Returns (resume_section, cover_letter_section, career_analysis_section).
    Falls back to empty strings on parse failure.
    """
    try:
        resume_section = (
            analysis
            .split("===TAILORED_RESUME===")[1]
            .split("===TAILORED_COVER_LETTER===")[0]
            .strip()
        )
        cover_letter_section = (
            analysis
            .split("===TAILORED_COVER_LETTER===")[1]
            .split("===CAREER_ANALYSIS===")[0]
            .strip()
        )
        career_analysis_section = (
            analysis
            .split("===CAREER_ANALYSIS===")[1]
            .strip()
        )
        return resume_section, cover_letter_section, career_analysis_section

    except (IndexError, Exception) as e:
        print(f"\nWarning: Could not split sections cleanly ({e}).")
        print("Printing full AI response instead.\n")
        print(analysis)
        return "", "", ""


def save_outputs(
    career_analysis: str,
    resume_section: str,
    cover_letter: str,
) -> None:
    """Create output folders and save files."""

    # Create folders
    os.makedirs("analyses", exist_ok=True)
    os.makedirs("tailored_resumes", exist_ok=True)
    os.makedirs("cover_letters", exist_ok=True)

    # Create timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

    # Save Career Analysis (.txt)

    analysis_path = f"analyses/career_analysis_{timestamp}.txt"

    with open(analysis_path, "w", encoding="utf-8") as f:
        f.write(career_analysis)

    # Save Tailored Resume (.docx)

    resume_path = f"tailored_resumes/tailored_resume_{timestamp}.docx"

    resume_doc = Document()
    resume_doc.add_heading("Tailored Resume", level=1)
    resume_doc.add_paragraph(resume_section)
    resume_doc.save(resume_path)

    # Save Cover Letter (.docx)

    cover_letter_path = f"cover_letters/cover_letter_{timestamp}.docx"

    cover_doc = Document()
    cover_doc.add_heading("Cover Letter", level=1)
    cover_doc.add_paragraph(cover_letter)
    cover_doc.save(cover_letter_path)

    # Success Message

    print_header("FILES GENERATED SUCCESSFULLY")

    print(f"  → {analysis_path}")
    print(f"  → {resume_path}")
    print(f"  → {cover_letter_path}")

    print()

# Main

# Main

def main():

    # TODO:
    # add PDF resume support later
    # improve DOCX formatting
    # maybe add LinkedIn job URL input

    print_header("AI CAREER ASSISTANT")

    resume_text = load_resume()
    job_description = get_job_description()

    print("\nAnalyzing your resume against the job description...")
    print("This may take 15–30 seconds depending on length.\n")

    prompt = build_prompt(resume_text, job_description)

    try:
        analysis = call_openai(prompt)
    except Exception as e:
        print(f"\nOpenAI API error: {e}")
        exit(1)

    resume_section, cover_letter_section, career_analysis_section = parse_sections(analysis)

    if career_analysis_section:
        save_outputs(career_analysis_section, resume_section, cover_letter_section)
    else:
        print("\nNo structured output was saved due to parsing issues.")
        print("Check the printed output above for the full AI response.")


if __name__ == "__main__":
    main()