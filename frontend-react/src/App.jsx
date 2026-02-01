import { useState, useEffect, useCallback } from 'react';

// Icons
import { Clock } from 'lucide-react';

// Components
import Header from './components/layout/Header';
import ModeSwitcher from './components/layout/ModeSwitcher';
import Modal from './components/common/Modal';
import Toast from './components/common/Toast';
import SingleReceiptView from './components/receipts/SingleReceiptView';
import BulkReceiptView from './components/receipts/BulkReceiptView';
import HistoryView from './components/receipts/HistoryView';
import ResultView from './components/receipts/ResultView';

// Hooks
import { useHealthCheck } from './hooks/useHealthCheck';
import { useSingleProcessing } from './hooks/useSingleProcessing';
import { useBulkProcessing } from './hooks/useBulkProcessing';
import { useHistory } from './hooks/useHistory';

// Utils
import { API_BASE } from './utils/constants';

function App() {
    const [mode, setMode] = useState('single'); // 'single' | 'bulk' | 'history'
    const [useAI, setUseAI] = useState(false);
    const [showAIToast, setShowAIToast] = useState(false);
    const [modalImage, setModalImage] = useState(null);
    const [modalResult, setModalResult] = useState(null);

    const { healthStatus } = useHealthCheck();
    const { history, loading: historyLoading, refreshHistory } = useHistory(mode === 'history');

    const single = useSingleProcessing();
    const bulk = useBulkProcessing();

    // Cleanup effect for URL previews (Fixed: Only run on unmount to avoid revoking active URLs)
    useEffect(() => {
        return () => {

        };
    }, []);

    const handleAIToggle = (checked) => {
        setUseAI(checked);
        if (checked) {
            setShowAIToast(true);
            setTimeout(() => setShowAIToast(false), 3000);
        }
    };

    const handleViewImage = (fileObj, previewUrl) => {
        if (fileObj.type === "application/pdf") {
            window.open(previewUrl, "_blank");
        } else {
            setModalImage(previewUrl);
        }
    };

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

    const handleViewData = (data) => {
        setModalResult(data);
    };

    return (
        <div className="container">
            <Header healthStatus={healthStatus} />

            <Toast
                show={showAIToast}
                title="AI Analysis Enabled"
                subtitle="Processing time will increase significantly."
                icon={Clock}
            />

            <Modal
                isOpen={!!modalImage}
                onClose={() => setModalImage(null)}
                mode="image"
            >
                <img src={modalImage} className="modal-image" alt="Receipt" />
            </Modal>

            <Modal
                isOpen={!!modalResult}
                onClose={() => setModalResult(null)}
                title="Receipt Details"
                mode="data"
            >
                <ResultView data={modalResult} />
            </Modal>

            <ModeSwitcher currentMode={mode} setMode={setMode} />

            <div className="card main-card">
                {mode === 'single' && (
                    <SingleReceiptView
                        file={single.file}
                        preview={single.preview}
                        data={single.data}
                        loading={single.loading}
                        status={single.status}
                        error={single.error}
                        useAI={useAI}
                        setUseAI={handleAIToggle}
                        onFileChange={single.handleFileChange}
                        onViewImage={(file, preview) => handleViewImage(file, preview)}
                        onSubmit={() => single.submit(useAI)}
                    />
                )}

                {mode === 'bulk' && (
                    <BulkReceiptView
                        files={bulk.files}
                        processing={bulk.processing}
                        completedCount={bulk.completedCount}
                        eta={bulk.eta}
                        useAI={useAI}
                        onFileChange={bulk.handleFileChange}
                        onToggleAI={handleAIToggle}
                        onSubmit={() => bulk.submit(useAI)}
                        onClear={bulk.clearAll}
                        onRemove={bulk.removeFile}
                        onViewImage={(file) => handleViewImage(file, file.preview)}
                        onViewData={handleViewData}
                    />
                )}

                {mode === 'history' && (
                    <HistoryView
                        history={history}
                        loading={historyLoading}
                        onRefresh={refreshHistory}
                        onViewImage={(item) => handleViewImageHistory(item)}
                        onViewData={handleViewData}
                    />
                )}
            </div>
        </div>
    );
}

export default App;
