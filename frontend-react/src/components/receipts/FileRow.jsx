import PropTypes from 'prop-types';
import { FileText, Loader2, Eye, FileJson, Trash2 } from 'lucide-react';

const FileRow = ({
    file,
    onViewImage,
    onViewData,
    onRemove,
    isHistory = false,
    isProcessing = false
}) => {
    const isPdf = file.filename.toLowerCase().endsWith('.pdf');

    return (
        <div className={`file-row ${file.status || ''} ${isHistory ? 'history-item' : ''}`}>
            <div className="file-icon" onClick={() => onViewImage(file)}>
                {isPdf ? (
                    <FileText size={20} color={isHistory ? "#64748b" : undefined} />
                ) : (
                    <img src={file.preview} alt={file.filename} />
                )}
            </div>

            <div className="file-details">
                <div className="name">{file.merchant || file.filename}</div>
                <div className="status">
                    {file.status === 'idle' && 'Ready'}
                    {file.status === 'queued' && 'Queued'}
                    {file.status === 'processing' && (
                        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <Loader2 size={10} className="spin" /> Processing...
                        </span>
                    )}
                    {file.status === 'success' && <span className="txt-success">Complete</span>}
                    {file.status === 'completed' && <span className="txt-success">Complete</span>}
                    {file.status === 'error' && <span className="txt-err">Failed</span>}

                    {isHistory && file.date && (
                        <span className="history-date">
                            {file.date} • {new Date(file.created_at).toLocaleDateString()}
                        </span>
                    )}
                </div>
            </div>

            {isHistory && (
                <div className="history-amount">
                    {file.total ? `$${file.total.toFixed(2)}` : '--'}
                </div>
            )}

            <div className="row-actions">
                <button className="icon-btn" onClick={() => onViewImage(file)} title="View Original">
                    <Eye size={18} />
                </button>

                {(file.status === 'success' || file.status === 'completed') && (
                    <button
                        className="icon-btn success"
                        onClick={() => onViewData(file.data || file)}
                        title="View Extracted Data"
                    >
                        <FileJson size={18} />
                    </button>
                )}

                {!isHistory && file.status !== 'processing' && (
                    <button className="icon-btn danger" onClick={() => onRemove(file.id)} title="Remove">
                        <Trash2 size={16} />
                    </button>
                )}
            </div>

            {file.status === 'processing' && (
                <div className="row-scanner">
                    <div className="row-scanner-bar"></div>
                </div>
            )}
        </div>
    );
};

FileRow.propTypes = {
    file: PropTypes.object.isRequired,
    onViewImage: PropTypes.func.isRequired,
    onViewData: PropTypes.func.isRequired,
    onRemove: PropTypes.func,
    isHistory: PropTypes.bool,
    isProcessing: PropTypes.bool,
};

export default FileRow;
