import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Schedule endpoints
export const getSchedules = async (date = null) => {
    const params = date ? { date } : {};
    const response = await api.get('/schedules', { params });
    return response.data;
};

export const triggerScrape = async () => {
    const response = await api.post('/ingest-scraped-data');
    return response.data;
};

// Notification endpoints
export const subscribe = async (email = null, pushSubscription = null) => {
    const response = await api.post('/subscribe', {
        email,
        push_subscription: pushSubscription,
    });
    return response.data;
};

export const unsubscribe = async (email = null, subscriptionId = null) => {
    const response = await api.post('/unsubscribe', {
        email,
        subscription_id: subscriptionId,
    });
    return response.data;
};

export const getSubscriptions = async () => {
    const response = await api.get('/subscriptions');
    return response.data;
};

export default api;
