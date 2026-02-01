import { useState, useEffect, useCallback } from 'react';
import { fetchHistory as fetchHistoryApi } from '../services/api';

export const useHistory = (shouldFetch) => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const loadHistory = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await fetchHistoryApi();
            setHistory(data);
        } catch (err) {
            setError(err.message);
            console.error("Failed to fetch history", err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (shouldFetch) {
            loadHistory();
        }
    }, [shouldFetch, loadHistory]);

    return { history, loading, error, refreshHistory: loadHistory };
};
