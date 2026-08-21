import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [jobDescription, setJobDescription] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [dragging, setDragging] = useState(false)

  const handleFile = (f) => {
    if (!f) return
    const valid = ['.pdf', '.docx', '.txt']
    const ext = f.name.substring(f.name.lastIndexOf('.')).toLowerCase()
    if (!valid.includes(ext)) {
      setError('Please upload a PDF, DOCX, or TXT file.')
      return
    }
    setError('')
    setFile(f)
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    handleFile(e.dataTransfer.files[0])
  }

  const handleAnalyze = async () => {
    if (!file) {
      setError('Please upload a resume first.')
      return
    }
    setLoading(true)
    setError('')
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('job_description', jobDescription)

    try {
      const res = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        body: formData,
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Server error' }))
        throw new Error(typeof err.detail === 'string' ? err.detail : 'Server error ' + res.status)
      }
      setResult(await res.json())
    } catch (err) {
      setError('Failed to analyze: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const analysis = result?.ai_analysis
  const match = result?.job_match

  return (
    <div className="app">
      <header>
        <h1>📄 AI Resume Analyzer</h1>
        <p>Upload a resume for instant AI analysis &amp; job matching.</p>
      </header>

      <div className="card">
        <div
          className={`dropzone ${dragging ? 'dragging' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          onClick={() => document.getElementById('fileInput').click()}
        >
          <input
            id="fileInput"
            type="file"
            accept=".pdf,.docx,.txt"
            hidden
            onChange={(e) => handleFile(e.target.files[0])}
          />
          {file
            ? <span className="filename">📎 {file.name}</span>
            : <span>📤 Drag &amp; drop resume here, or click to browse</span>}
        </div>

        <textarea
          className="jobdesc"
          placeholder="Paste a job description (optional) to get a match score..."
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
        />

        <button className="btn" onClick={handleAnalyze} disabled={loading}>
          {loading ? '⏳ Analyzing...' : '🚀 Analyze Resume'}
        </button>

        {error && <p className="error">⚠️ {error}</p>}
      </div>

      {match && (
        <div className="card">
          <h2>🎯 Job Match</h2>
          <div className="score-row">
            <div className="big-score">{match.match_score}<span>/100</span></div>
            <p className="verdict">{match.verdict}</p>
          </div>
          <div className="cols">
            <div>
              <h3 className="good">✅ Matched Skills</h3>
              <div className="chips">
                {match.matched_skills?.map((s) => <span key={s} className="chip good">{s}</span>)}
              </div>
            </div>
            <div>
              <h3 className="bad">❌ Missing Skills</h3>
              <div className="chips">
                {match.missing_skills?.map((s) => <span key={s} className="chip bad">{s}</span>)}
              </div>
            </div>
          </div>
          {match.keyword_suggestions?.length > 0 && (
            <div>
              <h3>💡 Keywords to Add</h3>
              <div className="chips">
                {match.keyword_suggestions.map((s) => <span key={s} className="chip tip">{s}</span>)}
              </div>
            </div>
          )}
        </div>
      )}

      {analysis && (
        <div className="card">
          <h2>📄 Resume Analysis</h2>
          <div className="score-row">
            <div className="big-score">{analysis.score}<span>/100</span></div>
            <div>
              <p><strong>Name:</strong> {analysis.name}</p>
              <p><strong>Email:</strong> {analysis.email || 'N/A'}</p>
              <p><strong>Phone:</strong> {analysis.phone || 'N/A'}</p>
              <p><strong>Experience:</strong> ~{analysis.experience_years} years</p>
            </div>
          </div>
          <h3>🛠️ Skills</h3>
          <div className="chips">
            {analysis.skills?.map((s) => <span key={s} className="chip">{s}</span>)}
          </div>
          <h3>📝 Summary</h3>
          <p className="summary">{analysis.summary}</p>
        </div>
      )}
    </div>
  )
}

export default App