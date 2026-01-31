import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import DateFilter from './components/DateFilter';
import ScheduleList from './components/ScheduleList';
import NotificationManager from './components/NotificationManager';
import { getSchedules } from './services/api';
import './index.css';

function App() {
    const [schedules, setSchedules] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedDate, setSelectedDate] = useState('');

    useEffect(() => {
        fetchSchedules();
    }, [selectedDate]);

    const fetchSchedules = async () => {
        setLoading(true);
        setError(null);

        try {
            const data = await getSchedules(selectedDate || null);
            setSchedules(data.data || []);
        } catch (err) {
            setError(err.message || 'Failed to fetch schedules');
            console.error('Fetch error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleRefresh = () => {
        fetchSchedules();
    };

    return (
        <div className="min-h-screen">
            <Header />

            <main className="container mx-auto px-6 pb-12">
                {/* Stats/Info Bar */}
                <div className="card bg-gradient-to-r from-blue-600 to-purple-600 text-white mb-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="text-2xl font-bold mb-1">Welcome to IITJ Health Center</h2>
                            <p className="text-blue-100">View doctor schedules and get notified</p>
                        </div>
                        <button
                            onClick={handleRefresh}
                            className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg font-semibold transition-all duration-300"
                        >
                            🔄 Refresh
                        </button>
                    </div>
                </div>

                {/* Date Filter */}
                <DateFilter selectedDate={selectedDate} onDateChange={setSelectedDate} />

                {/* Schedule List */}
                <ScheduleList schedules={schedules} loading={loading} error={error} />

                {/* Notification Manager */}
                <div className="mt-12">
                    <NotificationManager />
                </div>
            </main>

            {/* Footer */}
            <footer className="glass mt-12 py-6">
                <div className="container mx-auto px-6 text-center text-gray-600">
                    <p className="text-sm">
                        Made with ❤️ for IITJ Community
                    </p>
                    <p className="text-xs mt-1">
                        Data updates every 6 hours automatically
                    </p>
                </div>
            </footer>
        </div>
    );
}

export default App;
