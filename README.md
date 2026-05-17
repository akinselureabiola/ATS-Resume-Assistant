# AI Career Assistant

AI Career Assistant is a Python-based automation project that analyzes a resume against a job description using the OpenAI API.

The goal of the project is to help improve resumes for ATS (Applicant Tracking Systems) while also generating more tailored application materials such as:
- resume improvement suggestions
- ATS keyword optimization
- tailored resume summaries
- customized cover letters
- interview preparation topics
- realistic career fit analysis

The project was built mainly as a practical learning project while improving my skills in:
- Python scripting
- API integration
- automation workflows
- prompt engineering
- file handling
- DOCX generation

---

# Features

## Resume Analysis
The tool compares a candidate’s resume against a pasted job description and provides:
- realistic resume match scoring
- strengths and transferable skills
- ATS keyword suggestions
- missing skill analysis
- recruiter concern analysis

## Tailored Resume Suggestions
The application rewrites sections of the resume to better align with the target role while keeping the content realistic and truthful.

## Cover Letter Generation
The project generates a tailored cover letter based on:
- the resume
- the target job description
- transferable technical skills
- ATS optimization principles

## Career Guidance
The tool also gives realistic advice on:
- whether the candidate should apply
- skill gaps
- areas to improve before applying

## DOCX Export
Generated resumes and cover letters are automatically exported as Microsoft Word documents.

---

# Technologies Used

- Python
- OpenAI API
- python-docx
- python-dotenv

---

# Project Structure

```bash
AI-Career-Assistant/
│
├── app.py
├── resume.txt
├── .env
│
├── analyses/
│   └── career analysis output files
│
├── tailored_resumes/
│   └── generated resume documents
│
├── cover_letters/
│   └── generated cover letter documents