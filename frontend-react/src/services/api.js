import { API_BASE } from '../utils/constants';

export const checkHealth = async () => {
    const res = await fetch(`${API_BASE}/`);
    if (!res.ok) throw new Error('System Offline');
    return true;
};

export const fetchHistory = async () => {
    const res = await fetch(`${API_BASE}/api/v1/receipts/history`);
    if (!res.ok) throw new Error('Failed to fetch history');
    return res.json();
};

export const processReceipt = async (file, useAI) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("generate_summary", useAI);

    const res = await fetch(`${API_BASE}/api/v1/process-receipt`, {
        method: "POST",
        body: formData,
    });
    if (!res.ok) throw new Error("Upload Failed");
    return res.json();
};

export const processBulkReceipts = async (files, useAI) => {
    const formData = new FormData();
    files.forEach(f => formData.append("files", f));
    formData.append("generate_summary", useAI);

    const res = await fetch(`${API_BASE}/api/v1/process-receipt/bulk`, {
        method: "POST",
        body: formData,
    });
    if (!res.ok) throw new Error("Bulk Upload Failed");
    return res.json();
};

export const getTaskStatus = async (taskId) => {
    const res = await fetch(`${API_BASE}/api/v1/tasks/${taskId}`);
    if (!res.ok) throw new Error("Failed to get task status");
    return res.json();
};
