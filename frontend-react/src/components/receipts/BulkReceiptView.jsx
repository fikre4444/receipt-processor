import PropTypes from 'prop-types';
import { Upload, Clock, Loader2 } from 'lucide-react';
import FileRow from './FileRow';

const BulkReceiptView = ({
    files,
    processing,
    completedCount,
    eta,
    useAI,
    onFileChange,
    onToggleAI,
    onSubmit,
    onClear,
    onRemove,
    onViewImage,
    onViewData
}) => {
    return (
        <div className="bulk-container fade-in">
            <div className="upload-mini">
                <input
                    type="file"
                    multiple
                    accept=".jpg,.png,.pdf"
                    id="bulk-up"
                    onChange={onFileChange}
                />
                <label htmlFor="bulk-up" className="bulk-label">
                    <Upload size={20} /> Add Files
                </label>
                <span className="file-count">{files.length} files selected</span>

                <div
                    className={`ai-toggle-btn ${useAI ? 'active' : ''} ml-auto`}
                    onClick={() => onToggleAI(!useAI)}
                >
                    <div className="toggle-track">
                        <div className="toggle-thumb"></div>
                    </div>
                    <span className="toggle-label">AI Analysis {useAI ? 'ON' : 'OFF'}</span>
                </div>
            </div>

            {files.length > 0 && (
                <div className="bulk-actions">
                    <button
                        className="primary-btn"
                        onClick={onSubmit}
                        disabled={processing || files.every(f => f.status === 'success')}
                    >
                        {processing ? 'Processing...' : `Process All (${files.filter(f => f.status === 'idle').length})`}
                    </button>

                    <button
                        className="secondary-btn"
                        onClick={onClear}
                        disabled={processing}
                    >
                        Clear List
                    </button>
                </div>
            )}

            {processing && (
                <div className="progress-section">
                    <div className="progress-text">
                        <span>Processing {completedCount} / {files.length}</span>
                        {eta && <span className="eta"><Clock size={12} /> ~{eta}s left</span>}
                    </div>
                    <div className="progress-track">
                        <div
                            className="progress-fill"
                            style={{ width: `${(completedCount / files.length) * 100}%` }}
                        ></div>
                    </div>
                </div>
            )}

            <div className="file-list-scroll">
                {files.map(f => (
                    <FileRow
                        key={f.id}
                        file={f}
                        onViewImage={onViewImage}
                        onViewData={onViewData}
                        onRemove={onRemove}
                        isProcessing={f.status === 'processing'}
                    />
                ))}
                {files.length === 0 && <div className="empty-bulk">No files added yet.</div>}
            </div>
        </div>
    );
};

BulkReceiptView.propTypes = {
    files: PropTypes.array.isRequired,
    processing: PropTypes.bool.isRequired,
    completedCount: PropTypes.number.isRequired,
    eta: PropTypes.number,
    useAI: PropTypes.bool.isRequired,
    onFileChange: PropTypes.func.isRequired,
    onToggleAI: PropTypes.func.isRequired,
    onSubmit: PropTypes.func.isRequired,
    onClear: PropTypes.func.isRequired,
    onRemove: PropTypes.func.isRequired,
    onViewImage: PropTypes.func.isRequired,
    onViewData: PropTypes.func.isRequired,
};

export default BulkReceiptView;
