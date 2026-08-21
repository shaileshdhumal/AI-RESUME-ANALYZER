# AI Resume Analyzer

Upload a PDF, DOCX, or TXT resume for AI-powered extraction, scoring, and optional job-description matching.

## Run locally

1. Copy `.env.example` to `.env` and set `GROQ_API_KEY`.
2. Start the API: `uvicorn main:app --reload`.
3. In another terminal, run `npm install` then `npm run dev` from `frontend`.

The frontend is available at `http://localhost:5173`; the API health check is at `http://localhost:8000/api/health`.

## Deploy with Docker

Set `GROQ_API_KEY` as a deployment secret, then build and run:

```sh
docker build -t resume-analyzer .
docker run --rm -p 8000:8000 -e GROQ_API_KEY=your_key resume-analyzer
```

The container serves both the compiled React app and API on one port. For Render, Railway, Fly.io, or Cloud Run, deploy from the included `Dockerfile`, expose port `8000` (or set `PORT`), and configure `GROQ_API_KEY` in the host's secret/environment-variable UI.

If you deploy the frontend separately, set `VITE_API_URL` at build time and add its public origin to `CORS_ORIGINS` on the API.
