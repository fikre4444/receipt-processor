import { useState, useEffect } from 'react'
import { Upload, CheckCircle, AlertCircle, Cpu, Activity, RefreshCw } from 'lucide-react';

function App() {
  const [file, setFile] = useState(null)
  const [useAI, setUseAI] = useState(false)
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  
  const [healthStatus, setHealthStatus] = useState("loading") // loading, ok, error

  useEffect(() => {
    checkHealth()
  }, [])

  const checkHealth = async () => {
    setHealthStatus("loading")
    try {
      const res = await fetch("http://localhost:8000/")
      if (res.ok) setHealthStatus("ok")
      else setHealthStatus("error")
    } catch (e) {
      setHealthStatus("error")
    }
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError(null)
      setData(null) 
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) return

    setLoading(true)
    setError(null)
    setData(null)

    const formData = new FormData()
    formData.append("file", file)
    formData.append("generate_summary", useAI)

    try {
      const response = await fetch("http://localhost:8000/api/v1/process-receipt", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Upload failed")
      }

      const result = await response.json()
      setData(result.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <header>
        <h1>Receipt Processor</h1>
        <p>AI-Powered Expense Extraction Service</p>
      </header>

      <div className="card">
        <div 
          className={`health-badge ${healthStatus === 'ok' ? 'health-ok' : healthStatus === 'error' ? 'health-err' : 'health-loading'}`}
          onClick={checkHealth}
          title="Click to retry connection"
        >
          {healthStatus === 'loading' && <RefreshCw className="spin" size={12} />}
          {healthStatus === 'ok' && <Activity size={12} />}
          {healthStatus === 'error' && <AlertCircle size={12} />}
          <span>{healthStatus === 'ok' ? 'System Online' : healthStatus === 'error' ? 'Backend Offline' : 'Checking...'}</span>
        </div>

        <form onSubmit={handleSubmit}>
          <div className={`upload-box ${file ? 'active' : ''}`}>
            <input 
              type="file" 
              accept=".jpg,.jpeg,.png"
              onChange={handleFileChange} 
              id="file-upload"
            />
            <label htmlFor="file-upload" className="upload-label">
              {file ? (
                <>
                   <CheckCircle size={48} color="var(--success)" />
                   <span style={{color: 'var(--text-main)'}}>{file.name}</span>
                </>
              ) : (
                <>
                  <Upload size={48} />
                  <span>Click to select Receipt Image</span>
                </>
              )}
            </label>
          </div>

          <div className="options">
            <label className="checkbox-label">
              <input 
                type="checkbox" 
                checked={useAI} 
                onChange={(e) => setUseAI(e.target.checked)} 
              />
              <span>Enable AI Summary Analysis</span>
            </label>
          </div>

          <button type="submit" className="primary-btn" disabled={loading || !file}>
            {loading ? (
               <>Processing...</>
            ) : (
               <>Extract Data <Cpu size={18} /></>
            )}
          </button>
          
          {loading && (
            <div className="scanner-animation">
              <div className="scanner-bar"></div>
            </div>
          )}
        </form>

        {error && <div className="error" style={{color: 'var(--error)', marginTop: '1rem', display:'flex', alignItems:'center', gap:'8px'}}><AlertCircle size={16}/> {error}</div>}
      </div>

      {data && (
        <div className="results card">
            <div className="grid">
                <div className="stat">
                    <span>Total Amount</span>
                    <strong>${data.total ? data.total.toFixed(2) : "0.00"}</strong>
                </div>
                <div className="stat">
                    <span>Date</span>
                    <strong>{data.date || "Not Found"}</strong>
                </div>
            </div>
            
            {data.summary && (
                <div className="summary-box">
                    <div className="summary-header">
                       <Cpu size={18} /> AI Analysis
                    </div>
                    <div className="summary-content">
                        {/* 
                           For formatting the AI output: 
                           If the AI returns newlines, render them properly 
                        */}
                        {data.summary.split('\n').map((line, i) => (
                            <div key={i} style={{marginBottom: '4px'}}>{line}</div>
                        ))}
                    </div>
                </div>
            )}

            <details style={{cursor: 'pointer', color: 'var(--text-muted)'}}>
                <summary>View Raw OCR Text</summary>
                <pre style={{marginTop: '10px'}}>{data.raw_text}</pre>
            </details>
        </div>
      )}
    </div>
  )
}

export default App