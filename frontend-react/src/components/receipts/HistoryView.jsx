import PropTypes from 'prop-types';
import { RefreshCw, Loader2 } from 'lucide-react';
import FileRow from './FileRow';
import { API_BASE } from '../../utils/constants';

const HistoryView = ({
    history,
    loading,
    onRefresh,
    onViewImage,
    onViewData
}) => {
    return (
        <div className="history-container fade-in">
            <div className="history-header">
                <h3>Processing History</h3>
                <button
                    className="icon-btn"
                    onClick={onRefresh}
                    title="Refresh History"
                >
                    <RefreshCw size={16} />
                </button>
            </div>

            {loading ? (
                <div className="loading-state">
                    <Loader2 className="spin" /> Loading History...
                </div>
            ) : (
                <div className="history-list">
                    {history.map(item => {
                        // Adapt history item to FileRow expectations
                        const adaptedItem = {
                            ...item,
                            filename: item.filename || 'receipt.jpg',
                            status: item.status, // expected to be 'completed' or 'error'
                            preview: `${API_BASE}/api/v1/receipts/${item.id}/file`
                        };

                        return (
                            <FileRow
                                key={item.id}
                                file={adaptedItem}
                                onViewImage={onViewImage}
                                onViewData={onViewData}
                                isHistory={true}
                            />
                        );
                    })}
                    {history.length === 0 && (
                        <div className="empty-bulk">No history found.</div>
                    )}
                </div>
            )}
        </div>
    );
};

HistoryView.propTypes = {
    history: PropTypes.array.isRequired,
    loading: PropTypes.bool.isRequired,
    onRefresh: PropTypes.func.isRequired,
    onViewImage: PropTypes.func.isRequired,
    onViewData: PropTypes.func.isRequired,
};

export default HistoryView;
