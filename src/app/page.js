'use client';

import { useState, useRef, useEffect } from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import CameraFeed from './components/CameraFeed';
import ConfidenceLevel from './components/ConfidenceLevel';

export default function Home() {
  const [isDetecting, setIsDetecting] = useState(false);
  const [confidence, setConfidence] = useState(0);
  const [alertness, setAlertness] = useState('');
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleConfidenceUpdate = (newConfidence, newAlertness) => {
    setConfidence(newConfidence);
    setAlertness(newAlertness);
  };

  const startDetection = () => {
    setIsDetecting(true);
  };

  const stopDetection = () => {
    setIsDetecting(false);
    setConfidence(0);
    setAlertness('');
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header isMenuOpen={isMenuOpen} setIsMenuOpen={setIsMenuOpen} />
      
      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Page Title */}
          <div className="text-center mb-8">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
              Drowsiness Detection System
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Monitor driver alertness in real-time using advanced computer vision technology
            </p>
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Camera Feed Section */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                Live Camera Feed
              </h2>
              <CameraFeed 
                isDetecting={isDetecting} 
                onConfidenceUpdate={handleConfidenceUpdate}
              />
            </div>

            {/* Control Panel */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                Detection Controls
              </h2>
              
              {/* Confidence Level */}
              <div className="mb-6">
                <ConfidenceLevel confidence={confidence} alertness={alertness} />
              </div>

              {/* Control Buttons */}
              <div className="space-y-4">
                <button
                  onClick={isDetecting ? stopDetection : startDetection}
                  className={`w-full py-4 px-6 rounded-lg font-semibold text-lg transition-all duration-300 ${
                    isDetecting
                      ? 'bg-red-500 hover:bg-red-600 text-white'
                      : 'bg-green-500 hover:bg-green-600 text-white'
                  }`}
                >
                  {isDetecting ? 'Stop Detecting' : 'Start Detecting'}
                </button>
                
                <div className="grid grid-cols-2 gap-4">
                  <button className="py-3 px-4 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors">
                    Settings
                  </button>
                  <button className="py-3 px-4 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-medium transition-colors">
                    History
                  </button>
                </div>
              </div>

              {/* Status Indicator */}
              <div className="mt-6 p-4 bg-gray-100 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-gray-700 font-medium">Status:</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    isDetecting 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {isDetecting ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Statistics Section */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {isDetecting ? Math.floor(Math.random() * 100) : 0}
              </div>
              <div className="text-gray-600">Detection Count</div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {isDetecting ? Math.floor(Math.random() * 60) : 0}
              </div>
              <div className="text-gray-600">Session Time (min)</div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-3xl font-bold text-orange-600 mb-2">
                {isDetecting ? Math.floor(Math.random() * 10) : 0}
              </div>
              <div className="text-gray-600">Alerts Triggered</div>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}