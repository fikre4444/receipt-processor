import { useState, useCallback } from 'react';
import { processReceipt, getTaskStatus } from '../services/api';

export const useSingleProcessing = () => {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState("");
    const [error, setError] = useState(null);

    const handleFileChange = useCallback((e) => {
        if (e.target.files && e.target.files[0]) {
            const f = e.target.files[0];
            setFile(f);
            setPreview(URL.createObjectURL(f));
            setData(null);
            setError(null);
        }
    }, []);

    const pollTask = useCallback(async (taskId) => {
        const MAX_ATTEMPTS = 60;
        let attempts = 0;
        while (attempts < MAX_ATTEMPTS) {
            const result = await getTaskStatus(taskId);
            if (result.state === 'SUCCESS') return result.result;
            if (result.state === 'FAILURE') throw new Error(result.error);
            setStatus(result.status || "Processing...");
            await new Promise(r => setTimeout(r, 1000));
            attempts++;
        }
        throw new Error("Timeout");
    }, []);

    const submit = useCallback(async (useAI) => {
        if (!file) return;
        setLoading(true);
        setError(null);
        setStatus("Uploading...");

        try {
            const { task_id } = await processReceipt(file, useAI);
            setStatus("Queued...");
            const result = await pollTask(task_id);
            setData(result.data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [file, pollTask]);

    const reset = useCallback(() => {
        setFile(null);
        setPreview(null);
        setData(null);
        setError(null);
        setStatus("");
    }, []);

    return {
        file,
        preview,
        data,
        loading,
        status,
        error,
        handleFileChange,
        submit,
        reset
    };
};
