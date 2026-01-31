import React from 'react';

export default function Header() {
    return (
        <header className="glass sticky top-0 z-50 mb-8">
            <div className="container mx-auto px-6 py-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                            <span className="text-2xl">🏥</span>
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                                IITJ Health Center
                            </h1>
                            <p className="text-sm text-gray-600">Doctor Schedule</p>
                        </div>
                    </div>

                    <div className="flex gap-3">
                        <a
                            href="#notifications"
                            className="btn-secondary flex items-center gap-2"
                        >
                            <span>🔔</span>
                            <span className="hidden sm:inline">Notifications</span>
                        </a>
                    </div>
                </div>
            </div>
        </header>
    );
}
