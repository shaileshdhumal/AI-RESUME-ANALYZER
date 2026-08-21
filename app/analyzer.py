import json
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class ResumeAnalyzer:
    """Small wrapper around Groq's structured JSON chat response."""

    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not configured")
        self.client = Groq(api_key=api_key)
        self.model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    def _ask_ai(self, prompt: str) -> dict:
        response = self.client.chat.completions.create(
            model=self.model, messages=[{"role": "user", "content": prompt}], temperature=0.1,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("The analysis provider returned an empty response")
        result = json.loads(content)
        if not isinstance(result, dict):
            raise ValueError("The analysis provider returned an invalid response")
        return result

    def analyze(self, resume_text: str) -> dict:
        return self._ask_ai(f'''You are an expert HR and technical recruiter. Analyze the following resume.
Return strict JSON only with exactly these keys: name (string), email (string or null),
phone (string or null), skills (list of strings), experience_years (integer),
summary (one-sentence string), score (integer 0-100).

RESUME TEXT:
{resume_text}''')

    def match_job(self, resume_text: str, job_description: str) -> dict:
        return self._ask_ai(f'''You are an expert technical recruiter and ATS. Compare the candidate resume with the job description.
Return strict JSON only with exactly these keys: match_score (integer 0-100),
matched_skills (list of strings), missing_skills (list of strings),
keyword_suggestions (list of strings), verdict (one short sentence).

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_text}''')
