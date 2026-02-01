import { API_BASE } from './constants';

export const getTagStyle = (tag) => {
    if (tag === 'HIGH_VALUE') return { bg: '#fff7ed', text: '#c2410c', border: '#fdba74' }
    if (tag === 'FUTURE_DATE') return { bg: '#fef2f2', text: '#b91c1c', border: '#fca5a5' }
    if (tag === 'OLD_RECEIPT') return { bg: '#fefce8', text: '#a16207', border: '#fde047' }
    return { bg: '#f1f5f9', text: '#475569', border: '#cbd5e1' }
};

export const getFileUrl = (id) => `${API_BASE}/api/v1/receipts/${id}/file`;

export const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
    }).format(amount || 0);
};

export const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
};
