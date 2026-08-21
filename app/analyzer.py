import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class ResumeAnalyzer:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = "openai/gpt-oss-120b"

    def _ask_ai(self, prompt: str) -> dict:
        """Send a prompt to the AI and return the parsed JSON result."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def analyze(self, resume_text: str) -> dict:
        prompt = f"""
        You are an expert HR and technical recruiter.
        Analyze the following resume and extract the information into STRICT JSON format.
        Do not include any explanations, markdown formatting, or words outside the JSON.

        Return exactly these keys:
        - "name": string (candidate's full name)
        - "email": string or null
        - "phone": string or null
        - "skills": list of strings (extract all technical and soft skills)
        - "experience_years": integer (estimate total years based on dates)
        - "summary": string (a 1-sentence professional summary)
        - "score": integer from 0 to 100 (rate the resume quality)

        RESUME TEXT:
        {resume_text}
        """
        return self._ask_ai(prompt)

    def match_job(self, resume_text: str, job_description: str) -> dict:
        prompt = f"""
        You are an expert technical recruiter and ATS (Applicant Tracking System).
        Compare the CANDIDATE RESUME against the JOB DESCRIPTION.
        Return STRICT JSON only. No explanations, no markdown, nothing outside the JSON.

        Return exactly these keys:
        - "match_score": integer 0-100 (how well the resume fits the job)
        - "matched_skills": list of strings (skills in the resume that the job requires)
        - "missing_skills": list of strings (skills the job requires but the resume lacks)
        - "keyword_suggestions": list of strings (keywords to add to improve ATS ranking)
        - "verdict": string (one short sentence: Strong/Good/Weak match + why)

        JOB DESCRIPTION:
        {job_description}

        CANDIDATE RESUME:
        {resume_text}
        """
        return self._ask_ai(prompt)
    
    # uvicorn main:app --reload