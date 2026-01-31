import React from 'react';

export default function DoctorCard({ schedule }) {
    const isRegular = schedule.category?.includes('Regular') || schedule.category?.includes('Dentist');

    return (
        <div className="card hover:border-purple-300 animate-fade-in">
            <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-800 mb-1">
                        {schedule.name}
                    </h3>
                    <span className={isRegular ? 'badge-regular' : 'badge-specialist'}>
                        {schedule.category}
                    </span>
                </div>
                <div className="w-10 h-10 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center">
                    <span className="text-xl">{isRegular ? '👨‍⚕️' : '🩺'}</span>
                </div>
            </div>

            <div className="space-y-2 mt-4">
                <div className="flex items-center gap-2 text-gray-700">
                    <span className="text-lg">🕒</span>
                    <span className="font-semibold">{schedule.timing}</span>
                </div>

                {schedule.room && (
                    <div className="flex items-center gap-2 text-gray-600">
                        <span className="text-lg">📍</span>
                        <span>{schedule.room}</span>
                    </div>
                )}

                <div className="flex items-center gap-2 text-gray-600 text-sm">
                    <span className="text-lg">📅</span>
                    <span>{schedule.date}</span>
                </div>
            </div>
        </div>
    );
}
