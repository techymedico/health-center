// Service Worker for Push Notifications
self.addEventListener('push', function (event) {
    const data = event.data ? event.data.json() : {};

    const title = data.title || '🏥 IITJ Health Center';
    const options = {
        body: data.body || 'New notification',
        icon: data.icon || '/icon-192.png',
        badge: data.badge || '/badge-72.png',
        vibrate: [200, 100, 200],
        tag: 'doctor-notification',
        requireInteraction: true,
        actions: [
            {
                action: 'view',
                title: 'View Schedule'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

self.addEventListener('notificationclick', function (event) {
    event.notification.close();

    if (event.action === 'view' || !event.action) {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Basic caching for offline support (optional)
const CACHE_NAME = 'iitj-health-v1';

self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(clients.claim());
});
