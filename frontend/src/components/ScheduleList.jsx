import React from 'react';
import DoctorCard from './DoctorCard';

export default function ScheduleList({ schedules, loading, error }) {
    if (loading) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading schedules...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card bg-red-50 border-red-200">
                <div className="flex items-center gap-3 text-red-700">
                    <span className="text-2xl">⚠️</span>
                    <div>
                        <h3 className="font-semibold">Error loading schedules</h3>
                        <p className="text-sm">{error}</p>
                    </div>
                </div>
            </div>
        );
    }

    if (!schedules || schedules.length === 0) {
        return (
            <div className="card bg-gray-50 border-gray-200">
                <div className="text-center py-8">
                    <span className="text-6xl mb-4 block">📅</span>
                    <h3 className="text-xl font-semibold text-gray-700 mb-2">
                        No Schedules Found
                    </h3>
                    <p className="text-gray-600">
                        Try selecting a different date or check back later.
                    </p>
                </div>
            </div>
        );
    }

    // Group schedules by date
    const groupedSchedules = schedules.reduce((acc, schedule) => {
        const date = schedule.date || 'Unknown Date';
        if (!acc[date]) {
            acc[date] = [];
        }
        acc[date].push(schedule);
        return acc;
    }, {});

    return (
        <div className="space-y-8">
            {Object.entries(groupedSchedules).map(([date, dateSchedules]) => (
                <div key={date} className="animate-slide-up">
                    <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                        <span>📅</span>
                        <span>{date}</span>
                        <span className="text-sm font-normal text-gray-500">
                            ({dateSchedules.length} doctor{dateSchedules.length !== 1 ? 's' : ''})
                        </span>
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {dateSchedules.map((schedule, index) => (
                            <DoctorCard key={schedule.id || index} schedule={schedule} />
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
}
