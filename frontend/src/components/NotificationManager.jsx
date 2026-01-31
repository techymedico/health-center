import React, { useState } from 'react';
import { subscribe, unsubscribe } from '../services/api';
import { subscribeToPush, isPushSupported } from '../services/pushNotifications';

export default function NotificationManager() {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [messageType, setMessageType] = useState('info'); // 'success' | 'error' | 'info'
    const [isSubscribed, setIsSubscribed] = useState(false);

    const showMessage = (text, type = 'info') => {
        setMessage(text);
        setMessageType(type);
        setTimeout(() => setMessage(''), 5000);
    };

    const handleEmailSubscribe = async (e) => {
        e.preventDefault();

        if (!email) {
            showMessage('Please enter your email', 'error');
            return;
        }

        setLoading(true);
        try {
            await subscribe(email, null);
            showMessage(`✅ Subscribed successfully! You'll receive email notifications at ${email}`, 'success');
            setIsSubscribed(true);
            setEmail('');
        } catch (error) {
            showMessage(`❌ Subscription failed: ${error.message}`, 'error');
        } finally {
            setLoading(false);
        }
    };

    const handlePushSubscribe = async () => {
        if (!isPushSupported()) {
            showMessage('❌ Push notifications are not supported in your browser', 'error');
            return;
        }

        setLoading(true);
        try {
            const pushSubscription = await subscribeToPush();
            await subscribe(null, pushSubscription);
            showMessage('✅ Push notifications enabled successfully!', 'success');
            setIsSubscribed(true);
        } catch (error) {
            showMessage(`❌ Push subscription failed: ${error.message}`, 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleUnsubscribe = async () => {
        if (!window.confirm('Are you sure you want to unsubscribe?')) {
            return;
        }

        setLoading(true);
        try {
            await unsubscribe(email || null, null);
            showMessage('✅ Unsubscribed successfully', 'success');
            setIsSubscribed(false);
        } catch (error) {
            showMessage(`❌ Unsubscribe failed: ${error.message}`, 'error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div id="notifications" className="card bg-gradient-to-r from-blue-50 to-purple-50 border-purple-200">
            <div className="flex items-center gap-3 mb-4">
                <span className="text-3xl">🔔</span>
                <div>
                    <h2 className="text-2xl font-bold text-gray-800">Notifications</h2>
                    <p className="text-sm text-gray-600">
                        Get notified when doctors are about to start their duty
                    </p>
                </div>
            </div>

            {message && (
                <div className={`mb-4 p-4 rounded-lg ${messageType === 'success' ? 'bg-green-100 text-green-700' :
                        messageType === 'error' ? 'bg-red-100 text-red-700' :
                            'bg-blue-100 text-blue-700'
                    }`}>
                    {message}
                </div>
            )}

            <div className="space-y-6">
                {/* Email Subscription */}
                <div>
                    <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                        <span>📧</span>
                        Email Notifications
                    </h3>
                    <form onSubmit={handleEmailSubscribe} className="flex gap-2">
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="your.email@example.com"
                            className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500"
                            disabled={loading}
                        />
                        <button
                            type="submit"
                            disabled={loading}
                            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Subscribe
                        </button>
                    </form>
                </div>

                {/* Push Notifications */}
                <div>
                    <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                        <span>📱</span>
                        Browser Push Notifications
                    </h3>
                    <button
                        onClick={handlePushSubscribe}
                        disabled={loading || !isPushSupported()}
                        className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed w-full"
                    >
                        {isPushSupported() ? 'Enable Push Notifications' : 'Not Supported'}
                    </button>
                    <p className="text-xs text-gray-500 mt-2">
                        You'll receive notifications even when the browser is closed (requires permission)
                    </p>
                </div>

                {/* Unsubscribe */}
                {isSubscribed && (
                    <div className="pt-4 border-t border-gray-300">
                        <button
                            onClick={handleUnsubscribe}
                            disabled={loading}
                            className="btn-secondary text-red-600 hover:bg-red-50 w-full"
                        >
                            Unsubscribe from All Notifications
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
