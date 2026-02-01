import { useState, useRef, useCallback } from 'react';
import { processBulkReceipts, getTaskStatus } from '../services/api';

export const useBulkProcessing = () => {
    const [files, setFiles] = useState([]);
    const [processing, setProcessing] = useState(false);
    const [completedCount, setCompletedCount] = useState(0);
    const [eta, setEta] = useState(null);
    const startTimeRef = useRef(null);

    const handleFileChange = useCallback((e) => {
        if (e.target.files) {
            const newFiles = Array.from(e.target.files).map(f => ({
                id: crypto.randomUUID(),
                file: f,
                filename: f.name,
                preview: URL.createObjectURL(f),
                status: 'idle',
                data: null,
                taskId: null
            }));
            setFiles(prev => [...prev, ...newFiles]);
        }
    }, []);

    const removeFile = useCallback((id) => {
        setFiles(prev => prev.filter(f => f.id !== id));
    }, []);

    const clearAll = useCallback(() => {
        setFiles([]);
        setCompletedCount(0);
        setEta(null);
    }, []);

    const monitorProgress = useCallback(async (currentFiles) => {
        let pending = currentFiles.filter(i => i.taskId && i.status !== 'success' && i.status !== 'error');

        const poll = async () => {
            if (pending.length === 0) {
                setProcessing(false);
                setEta(null);
                return;
            }

            const checks = pending.map(async (item) => {
                try {
                    const json = await getTaskStatus(item.taskId);
                    if (json.state === 'SUCCESS') return { id: item.id, status: 'success', data: json.result.data };
                    if (json.state === 'FAILURE') return { id: item.id, status: 'error' };
                    return null;
                } catch {
                    return null;
                }
            });

            const results = await Promise.all(checks);

            setFiles(prev => {
                const next = [...prev];
                results.forEach(r => {
                    if (r) {
                        const idx = next.findIndex(x => x.id === r.id);
                        if (idx !== -1) {
                            next[idx].status = r.status;
                            if (r.data) next[idx].data = r.data;
                        }
                    }
                });

                const finished = next.filter(x => x.status === 'success' || x.status === 'error').length;
                setCompletedCount(finished);

                if (finished > 0 && finished < next.length) {
                    const elapsed = (Date.now() - startTimeRef.current) / 1000;
                    const avg = elapsed / finished;
                    setEta(Math.ceil(avg * (next.length - finished)));
                }

                return next;
            });
        };

        const runPoll = async () => {
            await poll();
            // Since we need the LATEST files state, we check if any are still processing
            setFiles(latestFiles => {
                const stillPending = latestFiles.filter(i => i.taskId && i.status === 'processing');
                if (stillPending.length > 0) {
                    setTimeout(runPoll, 2000);
                } else {
                    setProcessing(false);
                    setEta(null);
                }
                return latestFiles;
            });
        };

        runPoll();
    }, []);

    const submit = useCallback(async (useAI) => {
        const idleFiles = files.filter(f => f.status === 'idle');
        if (idleFiles.length === 0) return;

        setProcessing(true);
        setCompletedCount(0);
        startTimeRef.current = Date.now();

        try {
            const { tasks } = await processBulkReceipts(idleFiles.map(f => f.file), useAI);

            setFiles(prev => {
                const updated = [...prev];
                tasks.forEach(t => {
                    const idx = updated.findIndex(f => f.filename === t.filename && f.status === 'idle');
                    if (idx !== -1) {
                        updated[idx].status = 'processing';
                        updated[idx].taskId = t.task_id;
                    }
                });

                // Start monitoring with the updated list
                setTimeout(() => monitorProgress(updated), 0);
                return updated;
            });
        } catch (e) {
            console.error(e);
            setProcessing(false);
        }
    }, [files, monitorProgress]);

    return {
        files,
        processing,
        completedCount,
        eta,
        handleFileChange,
        removeFile,
        clearAll,
        submit
    };
};
