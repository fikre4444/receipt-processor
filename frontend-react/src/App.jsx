import { useState, useEffect } from 'react'
import { Upload, CheckCircle, AlertCircle, Cpu, Activity, RefreshCw, ShieldAlert } from 'lucide-react';

function App() {
  const [file, setFile] = useState(null)
  const [useAI, setUseAI] = useState(false)
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  
  const [healthStatus, setHealthStatus] = useState("loading") // loading, ok, error

  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

  useEffect(() => {
    checkHealth()
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
    }
  }, [previewUrl])

  const checkHealth = async () => {
    setHealthStatus("loading")
    try {
      const res = await fetch(API_BASE)
      if (res.ok) setHealthStatus("ok")
      else setHealthStatus("error")
    } catch (e) {
      setHealthStatus("error")
    }
  }

   const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile)
      
      // Generate Preview URL
      const objectUrl = URL.createObjectURL(selectedFile)
      setPreviewUrl(objectUrl)
      
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
      const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const response = await fetch(`${API_BASE}/api/v1/process-receipt`, {
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

  const getTagStyle = (tag) => {
    if (tag === 'HIGH_VALUE') return { bg: '#fff7ed', text: '#c2410c', border: '#fdba74' } // Orange
    if (tag === 'FUTURE_DATE') return { bg: '#fef2f2', text: '#b91c1c', border: '#fca5a5' } // Red
    if (tag === 'OLD_RECEIPT') return { bg: '#fefce8', text: '#a16207', border: '#fde047' } // Yellow
    return { bg: '#f1f5f9', text: '#475569', border: '#cbd5e1' } // Grey
  }

  return (
    <div className="container">
      <header>
        <h1>Receipt Processor</h1>
        <p>AI-Powered Expense Extraction & Analysis</p>
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
          <div className={`upload-box ${file ? 'has-file' : ''}`}>
            <input 
              type="file" 
              accept=".jpg,.jpeg,.png"
              onChange={handleFileChange} 
              id="file-upload"
            />
            <label htmlFor="file-upload" className="upload-label">
              {file ? (
                <>
                   {previewUrl && (
                     <div className="image-preview-container">
                        <img src={previewUrl} alt="Receipt Preview" />
                     </div>
                   )}
                   <div className="file-name-chip">
                      <CheckCircle size={20} color="var(--primary)" fill="#e0e7ff" />
                      {file.name}
                   </div>
                   <span className="change-file-text">Click to change file</span>
                </>
              ) : (
                <>
                  <Upload size={48} className="empty-state-icon" />
                  <span className="empty-state-text">Click to Upload Receipt</span>
                  <span className="empty-state-subtext">Supports JPG, PNG</span>
                </>
              )}
            </label>
          </div>

          <div className="options">
            <label className="checkbox-label">
              <input type="checkbox" checked={useAI} onChange={(e) => setUseAI(e.target.checked)} />
              <span>Enable AI Summary Analysis</span>
            </label>
          </div>

          <button type="submit" className="primary-btn" disabled={loading || !file}>
            {loading ? <>Processing...</> : <>Extract Data <Cpu size={18} /></>}
          </button>
          
          {loading && <div className="scanner-animation"><div className="scanner-bar"></div></div>}
        </form>

        {error && <div className="error" style={{color: 'var(--error)', marginTop: '1rem', display:'flex', alignItems:'center', gap:'8px'}}><AlertCircle size={16}/> {error}</div>}
      </div>

      {data && (
        <div className="results card">
            {data.tags && data.tags.length > 0 && (
               <div className="tags-section">
                  <div className="tags-header"><ShieldAlert size={16}/> Analysis Flags</div>
                  <div className="tags-list">
                    {data.tags.map(tag => {
                        const style = getTagStyle(tag);
                        return (
                            <span key={tag} className="analysis-tag" style={{
                                backgroundColor: style.bg,
                                color: style.text,
                                borderColor: style.border
                            }}>
                                {tag.replace('_', ' ')}
                            </span>
                        )
                    })}
                  </div>
               </div>
            )}

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
                    <div className="summary-header"><Cpu size={18} /> AI Analysis</div>
                    <div className="summary-content">
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