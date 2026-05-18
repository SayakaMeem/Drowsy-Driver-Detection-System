'use client';

import { useState, useEffect } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import Dashboard from '../components/Dashboard';

export default function DashboardPage() {
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const response = await fetch('/api/sessions?limit=50');
      const data = await response.json();
      setSessions(data.sessions);
      
      // Set the most recent session as current
      if (data.sessions.length > 0) {
        setCurrentSessionId(data.sessions[0].session_id);
      }
    } catch (error) {
      console.error('Error fetching sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (minutes) => {
    if (!minutes) return '0 min';
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col bg-gray-50">
        <Header />
        <main className="flex-1 container mx-auto px-4 py-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      
      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto">
          {/* Page Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-2">Analytics Dashboard</h1>
            <p className="text-lg text-gray-600">
              Monitor drowsiness detection performance and trends
            </p>
          </div>

          {/* Session Selector */}
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold text-gray-800 mb-2">Select Session</h2>
                <p className="text-gray-600">
                  Choose a detection session to view detailed analytics
                </p>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-3 text-gray-600">
                <select
                  value={currentSessionId || ''}
                  onChange={(e) => setCurrentSessionId(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">All Sessions (Combined)</option>
                  {sessions.map((session) => (
                    <option key={session.session_id} value={session.session_id}>
                      Session {session.session_id} - {formatDate(session.start_time)}
                    </option>
                  ))}
                </select>
                
                <button
                  onClick={fetchSessions}
                  className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors"
                >
                  Refresh
                </button>
              </div>
            </div>

            {/* Session Summary */}
            {currentSessionId && sessions.find(s => s.session_id === currentSessionId) && (
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-3">Session Summary</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-gray-800">
                  {(() => {
                    const session = sessions.find(s => s.session_id === currentSessionId);
                    return (
                      <>
                        <div>
                          <p className="text-sm text-gray-600">Session ID</p>
                          <p className="font-medium">{session.session_id}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Start Time</p>
                          <p className="font-medium">{formatDate(session.start_time)}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Duration</p>
                          <p className="font-medium">{formatDuration(session.duration_minutes)}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Detections</p>
                          <p className="font-medium">{session.total_detections}</p>
                        </div>
                      </>
                    );
                  })()}
                </div>
              </div>
            )}
          </div>

          {/* Dashboard Content */}
          <Dashboard sessionId={currentSessionId} />

          {/* Recent Sessions Table */}
          <div className="bg-white rounded-xl shadow-lg p-6 mt-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Recent Sessions</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Session ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Start Time
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Duration
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Detections
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Alerts
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {sessions.slice(0, 10).map((session) => (
                    <tr 
                      key={session.session_id}
                      className={`hover:bg-gray-50 cursor-pointer ${
                        currentSessionId === session.session_id ? 'bg-blue-50' : ''
                      }`}
                      onClick={() => setCurrentSessionId(session.session_id)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {session.session_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(session.start_time)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDuration(session.duration_minutes)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {session.total_detections}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          session.alerts_triggered > 0 
                            ? 'bg-red-100 text-red-800' 
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {session.alerts_triggered}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          session.end_time 
                            ? 'bg-gray-100 text-gray-800' 
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {session.end_time ? 'Completed' : 'Active'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
