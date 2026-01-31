import React from 'react';
import { format, addDays } from 'date-fns';

export default function DateFilter({ selectedDate, onDateChange }) {
    const today = new Date();

    const quickFilters = [
        { label: 'Today', date: today },
        { label: 'Tomorrow', date: addDays(today, 1) },
    ];

    const handleQuickFilter = (date) => {
        const formatted = format(date, 'dd/MM/yyyy');
        onDateChange(formatted);
    };

    const handleClear = () => {
        onDateChange('');
    };

    return (
        <div className="card mb-6">
            <div className="flex flex-wrap items-center gap-3">
                <span className="text-gray-700 font-semibold">Filter by date:</span>

                <div className="flex flex-wrap gap-2">
                    {quickFilters.map((filter) => (
                        <button
                            key={filter.label}
                            onClick={() => handleQuickFilter(filter.date)}
                            className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 text-white text-sm font-medium hover:shadow-lg transition-all duration-300 hover:scale-105"
                        >
                            {filter.label}
                        </button>
                    ))}

                    {selectedDate && (
                        <button
                            onClick={handleClear}
                            className="px-4 py-2 rounded-lg bg-gray-200 text-gray-700 text-sm font-medium hover:bg-gray-300 transition-all duration-300"
                        >
                            Clear Filter
                        </button>
                    )}
                </div>

                {selectedDate && (
                    <span className="text-sm text-gray-600 ml-auto">
                        Showing: <span className="font-semibold text-purple-600">{selectedDate}</span>
                    </span>
                )}
            </div>
        </div>
    );
}
