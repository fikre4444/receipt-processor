import PropTypes from 'prop-types';
import { Upload, CheckCircle, Eye, Cpu, Loader2, AlertCircle } from 'lucide-react';
import ResultView from './ResultView';

const SingleReceiptView = ({
    file,
    preview,
    data,
    loading,
    status,
    error,
    useAI,
    setUseAI,
    onFileChange,
    onViewImage,
    onSubmit
}) => {
    return (
        <form onSubmit={(e) => { e.preventDefault(); onSubmit(); }} className="fade-in">
            <div className={`upload-box ${file ? 'has-file' : ''}`}>
                <input
                    type="file"
                    accept=".jpg,.png,.pdf"
                    id="single-up"
                    onChange={onFileChange}
                />
                <label htmlFor="single-up">
                    {file ? (
                        <div className="file-info-group">
                            <div className="file-name-chip">
                                <CheckCircle size={20} color="var(--primary)" fill="#e0e7ff" />
                                <span className="truncate-name">{file.name}</span>
                            </div>
                            <button
                                type="button"
                                className="view-receipt-btn"
                                onClick={() => onViewImage(file, preview)}
                            >
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
                    <input
                        type="checkbox"
                        checked={useAI}
                        onChange={e => setUseAI(e.target.checked)}
                    />
                    Enable AI Analysis
                </label>
            </div>

            <button
                type="submit"
                className="primary-btn"
                disabled={loading || !file}
            >
                {loading ? (
                    <><Loader2 className="spin" size={18} /> {status}</>
                ) : (
                    <>Extract Data <Cpu size={18} /></>
                )}
            </button>

            {error && <div className="error-msg"><AlertCircle size={16} /> {error}</div>}

            <ResultView data={data} />
        </form>
    );
};

SingleReceiptView.propTypes = {
    file: PropTypes.object,
    preview: PropTypes.string,
    data: PropTypes.object,
    loading: PropTypes.bool.isRequired,
    status: PropTypes.string,
    error: PropTypes.string,
    useAI: PropTypes.bool.isRequired,
    setUseAI: PropTypes.func.isRequired,
    onFileChange: PropTypes.func.isRequired,
    onViewImage: PropTypes.func.isRequired,
    onSubmit: PropTypes.func.isRequired,
};

export default SingleReceiptView;
