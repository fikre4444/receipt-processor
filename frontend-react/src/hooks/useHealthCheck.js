import { useState, useEffect } from 'react';
import { checkHealth as checkHealthApi } from '../services/api';

export const useHealthCheck = () => {
    const [healthStatus, setHealthStatus] = useState("loading");

    const checkStatus = async () => {
        setHealthStatus("loading");
        try {
            await checkHealthApi();
            setHealthStatus("ok");
        } catch (e) {
            setHealthStatus("error");
        }
    };

    useEffect(() => {
        checkStatus();
    }, []);

    return { healthStatus, checkStatus };
};
