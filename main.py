import os
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.parser import ResumeParser
from app.analyzer import ResumeAnalyzer

app = FastAPI(title="AI Resume Analyzer API")

# Allow the React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "AI Resume Analyzer API is running. Visit /docs to test."}


@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(""),
):
    """Upload a resume (and optionally a job description) for AI analysis."""
    if not file.filename.endswith((".pdf", ".docx", ".txt")):
        raise HTTPException(status_code=400, detail="Use a PDF, DOCX, or TXT file.")

    temp_path = os.path.join(tempfile.gettempdir(), file.filename)
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        parser = ResumeParser()
        parsed_data = parser.extract(temp_path)

        analyzer = ResumeAnalyzer()
        ai_result = analyzer.analyze(parsed_data["text"])

        # Job matching (only if a job description was provided)
        match_result = None
        if job_description.strip():
            match_result = analyzer.match_job(parsed_data["text"], job_description)

        return {
            "file_info": {
                "filename": parsed_data["file_name"],
                "word_count": parsed_data["word_count"],
            },
            "ai_analysis": ai_result,
            "job_match": match_result,
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
# uvicorn main:app --reload