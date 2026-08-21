import os
import shutil
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.analyzer import ResumeAnalyzer
from app.parser import ResumeParser

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", 10 * 1024 * 1024))
ALLOWED_SUFFIXES = {".pdf", ".docx", ".txt"}


@asynccontextmanager
async def lifespan(_: FastAPI):
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY must be configured before starting the API.")
    yield


app = FastAPI(title="AI Resume Analyzer API", version="1.0.0", lifespan=lifespan)
cors_origins = [origin.strip() for origin in os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",") if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=cors_origins, allow_credentials=True,
                   allow_methods=["POST", "GET"], allow_headers=["*"])


@app.get("/api/health")
def health_check():
    """Lightweight health check for deployment platforms."""
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze_resume(file: UploadFile = File(...), job_description: str = Form("")):
    """Analyze a PDF, DOCX, or UTF-8 TXT resume and optionally match a job description."""
    original_name = Path(file.filename or "resume").name
    suffix = Path(original_name).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=400, detail="Use a PDF, DOCX, or TXT file.")
    if len(job_description) > 20_000:
        raise HTTPException(status_code=400, detail="Job description must be 20,000 characters or fewer.")

    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temporary_file:
            temp_path = Path(temporary_file.name)
            shutil.copyfileobj(file.file, temporary_file, length=1024 * 1024)
        if temp_path.stat().st_size > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail=(
                f"File is too large. Maximum size is {MAX_UPLOAD_BYTES // (1024 * 1024)} MB."
            ))

        parsed_data = ResumeParser().extract(str(temp_path))
        if not parsed_data["text"]:
            raise HTTPException(status_code=400, detail="No readable text was found in this resume.")

        analyzer = ResumeAnalyzer()
        ai_result = analyzer.analyze(parsed_data["text"])
        match_result = analyzer.match_job(parsed_data["text"], job_description) if job_description.strip() else None
        return {"file_info": {"filename": original_name, "word_count": parsed_data["word_count"]},
                "ai_analysis": ai_result, "job_match": match_result}
    except HTTPException:
        raise
    except (ValueError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=400, detail=f"Could not read this resume: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Analysis service is temporarily unavailable.") from exc
    finally:
        await file.close()
        if temp_path:
            temp_path.unlink(missing_ok=True)


if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def frontend(full_path: str):
        requested_file = FRONTEND_DIST / full_path
        return FileResponse(requested_file if full_path and requested_file.is_file() else FRONTEND_DIST / "index.html")
