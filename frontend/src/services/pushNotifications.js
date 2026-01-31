const VAPID_PUBLIC_KEY = import.meta.env.VITE_VAPID_PUBLIC_KEY || '';

// Convert VAPID key from base64 to Uint8Array
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

export const registerServiceWorker = async () => {
    if (!('serviceWorker' in navigator)) {
        console.warn('Service Worker not supported');
        return null;
    }

    try {
        const registration = await navigator.serviceWorker.register('/sw.js');
        console.log('Service Worker registered:', registration);
        return registration;
    } catch (error) {
        console.error('Service Worker registration failed:', error);
        return null;
    }
};

export const requestNotificationPermission = async () => {
    if (!('Notification' in window)) {
        console.warn('Notifications not supported');
        return 'denied';
    }

    const permission = await Notification.requestPermission();
    return permission;
};

export const subscribeToPush = async () => {
    const registration = await registerServiceWorker();

    if (!registration) {
        throw new Error('Service Worker registration failed');
    }

    const permission = await requestNotificationPermission();

    if (permission !== 'granted') {
        throw new Error('Notification permission denied');
    }

    try {
        const subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
        });

        return subscription.toJSON();
    } catch (error) {
        console.error('Push subscription failed:', error);
        throw error;
    }
};

export const unsubscribeFromPush = async () => {
    const registration = await navigator.serviceWorker.getRegistration();

    if (!registration) {
        return;
    }

    const subscription = await registration.pushManager.getSubscription();

    if (subscription) {
        await subscription.unsubscribe();
    }
};

export const isPushSupported = () => {
    return 'serviceWorker' in navigator && 'PushManager' in window;
};
