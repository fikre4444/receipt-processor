import { useState, useEffect, useRef } from 'react'
import { Upload, CheckCircle, AlertCircle, Cpu, Activity, RefreshCw, ShieldAlert, Loader2, Eye, X, FileText, Layers, FileDigit, Trash2, Clock, ChevronRight, FileJson } from 'lucide-react';

function App() {
  // --- GLOBAL STATE --- (for switching between single receipt and bulk mode)
  const [mode, setMode] = useState('single') // 'single' | 'bulk'
  const [healthStatus, setHealthStatus] = useState("loading")
  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
  
  // --- SINGLE MODE STATE ---
  const [singleFile, setSingleFile] = useState(null)
  const [singleData, setSingleData] = useState(null)
  const [singlePreview, setSinglePreview] = useState(null)
  const [singleLoading, setSingleLoading] = useState(false)
  const [singleStatus, setSingleStatus] = useState("")
  const [singleError, setSingleError] = useState(null)

  // --- BULK MODE STATE ---
  const [bulkFiles, setBulkFiles] = useState([]) 
  const [bulkProcessing, setBulkProcessing] = useState(false)
  const [completedCount, setCompletedCount] = useState(0)
  const [eta, setEta] = useState(null)
  const startTimeRef = useRef(null)

  // --- SHARED STATE ---
  const [useAI, setUseAI] = useState(false)
  const [modalImage, setModalImage] = useState(null) // For Image Popup
  const [modalResult, setModalResult] = useState(null) // NEW: For Data Popup

  const [showAIToast, setShowAIToast] = useState(false)

  useEffect(() => { checkHealth() }, [])

  useEffect(() => {
    return () => {
        if (singlePreview) URL.revokeObjectURL(singlePreview)
        bulkFiles.forEach(f => URL.revokeObjectURL(f.preview))
    }
  }, [])

  const handleAIToggle = (checked) => {
    setUseAI(checked)
    if (checked) {
        setShowAIToast(true)
        setTimeout(() => setShowAIToast(false), 3000)
    }
  }

  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  // Fetch history whenever mode changes to 'history'
  useEffect(() => {
    if (mode === 'history') {
      fetchHistory();
    }
  }, [mode]);

  const fetchHistory = async () => {
    setHistoryLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/receipts/history`);
      const data = await res.json();
      setHistory(data);
    } catch (err) {
      console.error("Failed to fetch history", err);
    } finally {
      setHistoryLoading(false);
    }
  };

  const getFileUrl = (id) => `${API_BASE}/api/v1/receipts/${id}/file`;

  const handleViewImageHistory = (item) => {
    let url = "";
    let isPdf = false;

    if (item.id && !item.file) {
      url = `${API_BASE}/api/v1/receipts/${item.id}/file`;
      isPdf = item.filename?.toLowerCase().endsWith(".pdf");
    } else {
      url = item.preview || URL.createObjectURL(item.file);
      isPdf = item.file?.type === "application/pdf" || item.filename?.toLowerCase().endsWith(".pdf");
    }

    if (isPdf) {
      window.open(url, "_blank");
    } else {
      setModalImage(url);
    }
  };

  const clearAll = () => {
    setBulkFiles([]);
    setCompletedCount(0);
    setEta(null);
  }

  const checkHealth = async () => {
    setHealthStatus("loading")
    try {
      const res = await fetch(`${API_BASE}/`) 
      if (res.ok) setHealthStatus("ok")
      else setHealthStatus("error")
    } catch (e) { setHealthStatus("error") }
  }

  const handleViewImage = (fileObj, previewUrl) => {
    if (fileObj.type === "application/pdf") {
        window.open(previewUrl, "_blank");
    } else {
        setModalImage(previewUrl);
    }
  }

  const removeBulkFile = (id) => {
    setBulkFiles(prev => prev.filter(f => f.id !== id));
  }

  const renderResultView = (data) => {
    if (!data) return null;
    const hasBreakdown = data.subtotal || data.tax || data.tip || data.discount || data.other_fees;
    return (
        <div className="result-container fade-in">
            <div className="merchant-header">
                <div className="merchant-label">Merchant</div>
                <div className="merchant-name">{data.merchant || "Unknown Merchant"}</div>
            </div>

            <div className="grid">
                <div className="stat">
                    <span>Grand Total</span>
                    <strong className="total-main">${data.total?.toFixed(2) || '0.00'}</strong>
                </div>
                <div className="stat">
                    <span>Date Extracted</span>
                    <strong>{data.date || 'N/A'}</strong>
                </div>
            </div>

            {hasBreakdown && (
                <div className="breakdown-section">
                    <div className="section-title">Financial Breakdown</div>
                    <div className="breakdown-list">
                        {data.subtotal > 0 && (
                            <div className="breakdown-row">
                                <span>Subtotal</span>
                                <span>${data.subtotal.toFixed(2)}</span>
                            </div>
                        )}
                        {data.tax > 0 && (
                            <div className="breakdown-row">
                                <span>Tax / VAT</span>
                                <span>+ ${data.tax.toFixed(2)}</span>
                            </div>
                        )}
                        {data.tip > 0 && (
                            <div className="breakdown-row highlight-blue">
                                <span>Tip / Service Charge</span>
                                <span>+ ${data.tip.toFixed(2)}</span>
                            </div>
                        )}
                        {data.discount > 0 && (
                            <div className="breakdown-row highlight-green">
                                <span>Discount / Savings</span>
                                <span>- ${data.discount.toFixed(2)}</span>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* AI Summary */}
            {data.summary && (
                <div className="summary-box">
                    <div className="summary-header"><Cpu size={16}/> AI Analysis</div>
                    <div className="summary-text">{data.summary}</div>
                </div>
            )}

            {/* Analysis Tags */}
            {data.tags?.length > 0 && (
                <div className="tags-section">
                    <div className="tags-header"><ShieldAlert size={14}/> Audit Flags</div>
                    <div className="tags-list">
                        {data.tags.map(t => (
                            <span key={t} className="tag" style={{...getTagStyle(t), border: `1px solid ${getTagStyle(t).border}`}}>
                                {t.replace('_', ' ')}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {/* Raw OCR Text */}
            <details className="raw-ocr-details">
                <summary>View Raw OCR Text <ChevronRight size={14} className="chevron"/></summary>
                <pre>{data.raw_text}</pre>
            </details>
        </div>
    )
  }

  // ==========================================
  // SINGLE MODE LOGIC
  // ==========================================
  const handleSingleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const f = e.target.files[0];
      setSingleFile(f)
      setSinglePreview(URL.createObjectURL(f))
      setSingleData(null)
      setSingleError(null)
    }
  }

  const pollSingleTask = async (taskId) => {
    const MAX_ATTEMPTS = 60; 
    let attempts = 0;
    while (attempts < MAX_ATTEMPTS) {
      const res = await fetch(`${API_BASE}/api/v1/tasks/${taskId}`);
      const result = await res.json();
      if (result.state === 'SUCCESS') return result.result;
      if (result.state === 'FAILURE') throw new Error(result.error);
      setSingleStatus(result.status || "Processing...");
      await new Promise(r => setTimeout(r, 1000));
      attempts++;
    }
    throw new Error("Timeout");
  };

  const submitSingle = async (e) => {
    e.preventDefault();
    if (!singleFile) return;
    setSingleLoading(true); setSingleError(null); setSingleStatus("Uploading...");
    
    const formData = new FormData();
    formData.append("file", singleFile);
    formData.append("generate_summary", useAI);

    try {
        const res = await fetch(`${API_BASE}/api/v1/process-receipt`, { method: "POST", body: formData });
        if (!res.ok) throw new Error("Upload Failed");
        const { task_id } = await res.json();
        
        setSingleStatus("Queued...");
        const result = await pollSingleTask(task_id);
        setSingleData(result.data);
    } catch (err) {
        setSingleError(err.message);
    } finally {
        setSingleLoading(false);
    }
  }

  // ==========================================
  // BULK MODE LOGIC
  // ==========================================
  const handleBulkFileChange = (e) => {
    if (e.target.files) {
        const newFiles = Array.from(e.target.files).map(f => ({
            id: crypto.randomUUID(),
            file: f,
            filename: f.name,
            preview: URL.createObjectURL(f),
            status: 'idle', 
            data: null
        }));
        setBulkFiles(prev => [...prev, ...newFiles]);
    }
  }

  const monitorBatchProgress = async (currentBatch) => {
    let pending = currentBatch.filter(i => i.taskId && i.status !== 'success' && i.status !== 'error')
    
    const poll = async () => {
        if (pending.length === 0) {
            setBulkProcessing(false); setEta(null); return;
        }

        const checks = pending.map(async (item) => {
            try {
                const res = await fetch(`${API_BASE}/api/v1/tasks/${item.taskId}`)
                const json = await res.json()
                if (json.state === 'SUCCESS') return { id: item.id, status: 'success', data: json.result.data }
                if (json.state === 'FAILURE') return { id: item.id, status: 'error' }
                return null
            } catch { return null }
        })

        const results = await Promise.all(checks)
        
        setBulkFiles(prev => {
            const next = [...prev]
            let finishedCount = 0
            
            results.forEach(r => {
                if (r) {
                    const idx = next.findIndex(x => x.id === r.id)
                    if (idx !== -1) {
                        next[idx].status = r.status
                        if (r.data) next[idx].data = r.data
                    }
                }
            })

            const finished = next.filter(x => x.status === 'success' || x.status === 'error').length
            setCompletedCount(finished)
            
            if (finished > 0 && finished < next.length) {
                const elapsed = (Date.now() - startTimeRef.current) / 1000
                const avg = elapsed / finished
                setEta(Math.ceil(avg * (next.length - finished)))
            }
            
            return next
        })

        pending = bulkFiles.filter(i => i.taskId && i.status !== 'success' && i.status !== 'error')
        if (results.some(r => !r) || pending.length > 0) setTimeout(() => monitorBatchProgress(bulkFiles), 2000)
    }
    poll()
  }

  const submitBulk = async (e) => {
    e.preventDefault();
    const idleFiles = bulkFiles.filter(f => f.status === 'idle');
    if (idleFiles.length === 0) return;

    setBulkProcessing(true);
    setCompletedCount(0);
    startTimeRef.current = Date.now();

    const formData = new FormData();
    idleFiles.forEach(f => formData.append("files", f.file));
    formData.append("generate_summary", useAI);

    try {
        const res = await fetch(`${API_BASE}/api/v1/process-receipt/bulk`, { method: "POST", body: formData });
        const { tasks } = await res.json();
        
        const updated = [...bulkFiles];
        tasks.forEach(t => {
            const idx = updated.findIndex(f => f.filename === t.filename && f.status === 'idle');
            if (idx !== -1) {
                updated[idx].status = 'processing';
                updated[idx].taskId = t.task_id;
            }
        });
        setBulkFiles(updated);
        monitorBatchProgress(updated);
    } catch (e) {
        console.error(e);
        setBulkProcessing(false);
    }
  }

  const getTagStyle = (tag) => {
    if (tag === 'HIGH_VALUE') return { bg: '#fff7ed', text: '#c2410c', border: '#fdba74' }
    if (tag === 'FUTURE_DATE') return { bg: '#fef2f2', text: '#b91c1c', border: '#fca5a5' }
    if (tag === 'OLD_RECEIPT') return { bg: '#fefce8', text: '#a16207', border: '#fde047' }
    return { bg: '#f1f5f9', text: '#475569', border: '#cbd5e1' }
  }

  return (
    <div className="container">
      <header>
        <h1>Receipt Processor</h1>
        <div className="header-meta">
            <span className={`health-pill ${healthStatus}`}>
                 {healthStatus === 'ok' ? <Activity size={12}/> : <AlertCircle size={12}/>} 
                 {healthStatus === 'ok' ? 'System Online' : 'Offline'}
            </span>
        </div>
      </header>

      {/* --- IMAGE MODAL --- */}
      {modalImage && (
        <div className="modal-overlay" onClick={() => setModalImage(null)}>
            <div className="modal-content image-mode" onClick={e => e.stopPropagation()}>
                <button className="modal-close-btn" onClick={() => setModalImage(null)}><X size={24} /></button>
                <img src={modalImage} className="modal-image" />
            </div>
        </div>
      )}

       {/* --- NEW: AI Warning Toast --- */}
      {showAIToast && (
        <div className="ai-toast fade-in">
            <Clock size={16} />
            <div>
                <strong>AI Analysis Enabled</strong>
                <div style={{fontSize: '0.75rem', opacity: 0.9}}>Processing time will increase significantly.</div>
            </div>
        </div>
      )}

      {/* --- RESULT DATA MODAL (NEW) --- */}
      {modalResult && (
        <div className="modal-overlay" onClick={() => setModalResult(null)}>
            <div className="modal-content data-mode" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <h3>Receipt Details</h3>
                    <button className="icon-btn" onClick={() => setModalResult(null)}><X size={20}/></button>
                </div>
                <div className="modal-body">
                    {renderResultView(modalResult)}
                </div>
            </div>
        </div>
      )}

      {/* --- MODE SWITCHER --- */}
      <div className="mode-switcher">
        <div className={`mode-option ${mode === 'single' ? 'active' : ''}`} onClick={() => setMode('single')}>
            <FileDigit size={16} /> Single Receipt
        </div>
        <div className={`mode-option ${mode === 'bulk' ? 'active' : ''}`} onClick={() => setMode('bulk')}>
            <Layers size={16} /> Batch Processing
        </div>
        <div className={`mode-option ${mode === 'history' ? 'active' : ''}`} onClick={() => setMode('history')}>
            <Clock size={16} /> History
        </div>
      </div>

      <div className="card main-card">
        
        {/* === SINGLE MODE === */}
        {mode === 'single' && (
            <form onSubmit={submitSingle} className="fade-in">
                <div className={`upload-box ${singleFile ? 'has-file' : ''}`}>
                    <input type="file" accept=".jpg,.png,.pdf" id="single-up" onChange={handleSingleFileChange} />
                    <label htmlFor="single-up">
                        {singleFile ? (
                            <div className="file-info-group">
                                <div className="file-name-chip">
                                    <CheckCircle size={20} color="var(--primary)" fill="#e0e7ff" />
                                    <span className="truncate-name">{singleFile.name}</span>
                                </div>
                                <button type="button" className="view-receipt-btn" onClick={() => handleViewImage(singleFile, singlePreview)}>
                                    <Eye size={16} /> View Receipt
                                </button>
                            </div>
                        ) : (
                            <>
                                <Upload size={48} className="empty-icon" />
                                <span className="empty-text">Upload Receipt</span>
                                <span className="empty-sub">JPG, PNG, PDF</span>
                            </>
                        )}
                    </label>
                </div>
                
                <div className="options">
                    <label className="checkbox-label">
                        <input type="checkbox" checked={useAI} onChange={e => setUseAI(e.target.checked)} />
                        Enable AI Analysis
                    </label>
                </div>

                <button type="submit" className="primary-btn" disabled={singleLoading || !singleFile}>
                    {singleLoading ? <><Loader2 className="spin" size={18}/> {singleStatus}</> : <>Extract Data <Cpu size={18} /></>}
                </button>

                {singleError && <div className="error-msg"><AlertCircle size={16}/> {singleError}</div>}

                {/* Render Result (Using Helper) */}
                {renderResultView(singleData)}
            </form>
        )}

        {/* === BULK MODE === */}
        {mode === 'bulk' && (
            <div className="bulk-container fade-in">
                 <div className="upload-mini">
                    <input type="file" multiple accept=".jpg,.png,.pdf" id="bulk-up" onChange={handleBulkFileChange} />
                    <label htmlFor="bulk-up" className="bulk-label">
                        <Upload size={20} /> Add Files
                    </label>
                    <span className="file-count">{bulkFiles.length} files selected</span>
                    
                    {/* CHANGED: Replaced standard checkbox with a distinct Toggle Button */}
                    <div 
                        className={`ai-toggle-btn ${useAI ? 'active' : ''} ml-auto`} 
                        onClick={() => handleAIToggle(!useAI)}
                    >
                        <div className="toggle-track">
                            <div className="toggle-thumb"></div>
                        </div>
                        <span className="toggle-label">AI Analysis {useAI ? 'ON' : 'OFF'}</span>
                    </div>

                 </div>

                 {bulkFiles.length > 0 && (
                    <div className="bulk-actions">
                         {/* EXISTING PROCESS BUTTON */}
                         <button className="primary-btn" onClick={submitBulk} disabled={bulkProcessing || bulkFiles.every(f => f.status === 'success')}>
                            {bulkProcessing ? 'Processing...' : `Process All (${bulkFiles.filter(f => f.status === 'idle').length})`}
                         </button>

                         {/* NEW: CLEAR ALL BUTTON */}
                         <button className="secondary-btn" onClick={clearAll} disabled={bulkProcessing}>
                            Clear List
                         </button>
                    </div>
                 )}

                 {bulkProcessing && (
                    <div className="progress-section">
                        <div className="progress-text">
                            <span>Processing {completedCount} / {bulkFiles.length}</span>
                            {eta && <span className="eta"><Clock size={12}/> ~{eta}s left</span>}
                        </div>
                        <div className="progress-track"><div className="progress-fill" style={{width: `${(completedCount / bulkFiles.length) * 100}%`}}></div></div>
                    </div>
                 )}

                 <div className="file-list-scroll">
                    {bulkFiles.map(f => (
                        <div key={f.id} className={`file-row ${f.status}`}>
                            <div className="file-icon" onClick={() => handleViewImage(f.file, f.preview)}>
                                {f.filename.endsWith('.pdf') ? <FileText size={20}/> : <img src={f.preview}/>}
                            </div>
                            <div className="file-details">
                                <div className="name">{f.filename}</div>
                                <div className="status">
                                    {f.status === 'idle' && 'Ready'}
                                    {f.status === 'queued' && 'Queued'}
                                    {f.status === 'processing' && (
                                        <span style={{display: 'flex', alignItems:'center', gap: '4px'}}>
                                            <Loader2 size={10} className="spin"/> Processing...
                                        </span>
                                    )}
                                    {f.status === 'success' && <span className="txt-success">Complete</span>}
                                    {f.status === 'error' && <span className="txt-err">Failed</span>}
                                </div>
                            </div>
                            <div className="row-actions">
                                {/* VIEW IMAGE BUTTON */}
                                <button className="icon-btn" onClick={() => handleViewImage(f.file, f.preview)} title="View Original">
                                    <Eye size={18}/>
                                </button>
                                
                                {/* NEW: VIEW DATA BUTTON */}
                                {f.status === 'success' && (
                                    <button className="icon-btn success" onClick={() => setModalResult(f.data)} title="View Extracted Data">
                                        <FileJson size={18}/>
                                    </button>
                                )}
                                {/* REMOVE BUTTON */}
                                {f.status !== 'processing' && (
                                    <button className="icon-btn danger" onClick={() => removeBulkFile(f.id)} title="Remove">
                                        <Trash2 size={16}/>
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                    {bulkFiles.length === 0 && <div className="empty-bulk">No files added yet.</div>}
                 </div>
            </div>
        )}
        {/* === HISTORY MODE === */}
        {mode === 'history' && (
          <div className="history-container fade-in">
            <div className="history-header">
                <h3>Processing History</h3>
                <button className="icon-btn" onClick={fetchHistory} title="Refresh History"><RefreshCw size={16} /></button>
            </div>

            {historyLoading ? (
                <div className="loading-state"><Loader2 className="spin" /> Loading History...</div>
            ) : (
                <div className="history-list">
                    {history.map(item => (
                        <div key={item.id} className={`history-item ${item.status}`}>
                            <div className="history-main">
                                {/* Thumbnail - Clicking opens the view */}
                                <div className="history-icon" onClick={() => handleViewImageHistory(item)}>
                                    {item.filename.endsWith('.pdf') ? (
                                        <FileText size={20} color="#64748b"/>
                                    ) : (
                                        <img src={`${API_BASE}/api/v1/receipts/${item.id}/file`} alt=""/>
                                    )}
                                </div>
                                
                                {/* Data Info - Clicking opens the result modal */}
                                <div className="history-info" onClick={() => item.status === 'completed' && setModalResult(item)}>
                                    <div className="history-merchant">{item.merchant || item.filename}</div>
                                    <div className="history-date">
                                        {item.date || 'No Date'} • {new Date(item.created_at).toLocaleDateString()}
                                    </div>
                                </div>

                                <div className="history-amount">
                                    {item.total ? `$${item.total.toFixed(2)}` : '--'}
                                </div>

                                {/* ROW ACTIONS */}
                                <div className="history-row-actions">
                                    {/* View Original Receipt Button */}
                                    <button className="icon-btn" onClick={() => handleViewImageHistory(item)} title="View Original">
                                        <Eye size={18} />
                                    </button>
                                    
                                    {/* View Extracted Data Button */}
                                    {item.status === 'completed' && (
                                        <button className="icon-btn success" onClick={() => setModalResult(item)} title="View Data">
                                            <FileJson size={18} />
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default App