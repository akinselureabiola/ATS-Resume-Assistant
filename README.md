# AI Career Assistant

AI Career Assistant is a Python-based automation project that analyzes a resume against a job description using the OpenAI API.

The goal of the project is to help improve resumes for ATS (Applicant Tracking Systems) while also generating more tailored application materials such as:
- Resume improvement suggestions
- ATS keyword optimization
- Tailored resume summaries
- Customized cover letters
- Interview preparation topics
- Realistic career fit analysis

The project was built as a practical learning project while improving skills in:
- Python scripting
- API integration
- Automation workflows
- Prompt engineering
- File handling
- DOCX generation

---

# Features

## Resume Analysis
The tool compares a candidate's resume against a pasted job description and provides:
- Realistic resume match scoring
- Strengths and transferable skills
- ATS keyword suggestions
- Missing skill analysis
- Recruiter concern analysis

## Tailored Resume Suggestions
The application rewrites sections of the resume to better align with the target role while keeping the content realistic and truthful.

## Cover Letter Generation
The project generates a tailored cover letter based on:
- The resume
- The target job description
- Transferable technical skills
- ATS optimization principles

## Career Guidance
The tool also gives realistic advice on:
- Whether the candidate should apply
- Skill gaps
- Areas to improve before applying

## DOCX Export
Generated resumes and cover letters are automatically exported as Microsoft Word documents.

---

# Technologies Used

- Python
- OpenAI API (GPT-4.1-mini)
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
```

---

# Setup & Usage

### 1. Clone the repository
```bash
git clone https://github.com/akinselureabiola/ATS-Resume-Assistant.git
cd ATS-Resume-Assistant
```

### 2. Install dependencies
```bash
pip install openai python-docx python-dotenv
```

### 3. Add your OpenAI API key
Create a `.env` file in the root folder and add:
OPENAI_API_KEY=your-api-key-here

### 4. Add your resume
Create a `resume.txt` file in the root folder and paste your resume content into it.

### 5. Run the tool
```bash
python app.py
```

When prompted, paste the job description and type `END` on a new line when finished.

### 6. Check your outputs
Generated files are saved automatically to:
- `analyses/` — career fit analysis (.txt)
- `tailored_resumes/` — tailored resume suggestions (.docx)
- `cover_letters/` — tailored cover letter (.docx)

---

# Sample Output

## Screenshots

### Tool Running
![Tool Start](screenshots/tool-start.png)

### Files Generated Successfully
![Output Generated](screenshots/output-generated.png)

---

# Notes

- This tool is designed to assist job seekers in understanding their resume fit before applying
- All generated content is based on the candidate's real experience — nothing is invented
- Best used as a guide alongside your own judgment, not as a replacement for it

