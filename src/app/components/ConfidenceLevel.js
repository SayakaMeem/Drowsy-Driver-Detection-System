'use client';

import { useState, useEffect, useRef } from 'react';
import mlService from '../services/mlService';

export default function ConfidenceLevel({ confidence, alertness, leftEyeConfidence, rightEyeConfidence }) {
  const [displayConfidence, setDisplayConfidence] = useState(confidence);
  const [displayAlertness, setDisplayAlertness] = useState(alertness);
  const updateTimeoutRef = useRef(null);
  const lastUpdateRef = useRef({ confidence: 0, alertness: '' });
  const[newMetrics, setNewMetrics] = useState({
    eyeClosure: leftEyeConfidence || 0,
    blinkRate: 0,
    headPosition: 'Unknown',
    yawnCount: 0,
    leftEyeConfidence: leftEyeConfidence || 0,
    rightEyeConfidence: rightEyeConfidence || 0
  });

  useEffect(() => {
    // Clear existing timeout
    if (updateTimeoutRef.current) {
      clearTimeout(updateTimeoutRef.current);
    }

    // Only update if change is significant (more than 3 points)
    const confidenceChange = Math.abs(confidence - lastUpdateRef.current.confidence);
    const alertnessChange = alertness !== lastUpdateRef.current.alertness;

    if (confidenceChange >= 3 || alertnessChange) {
      // Debounce updates by 300ms
      updateTimeoutRef.current = setTimeout(() => {
        setDisplayConfidence(confidence);
        setDisplayAlertness(alertness);
        lastUpdateRef.current = { confidence, alertness };
      }, 300);
    }

    return () => {
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current);
      }
    };
  }, [confidence, alertness]);

  // Update metrics when confidence changes
  useEffect(() => {
    if (confidence > 0) {
       setNewMetrics(mlService. getDetectionMetrics(confidence));
       console.log('Updated metrics:', newMetrics);
      // setMetrics(newMetrics); // This state is no longer needed
    }
  }, [confidence]);

  const getConfidenceColor = (level) => {
    if (level >= 80) return 'text-green-600 bg-green-100';
    if (level >= 60) return 'text-yellow-600 bg-yellow-100';
    if (level >= 40) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  const getConfidenceStatus = (level) => {
    if (level >= 80) return 'Very Alert';
    if (level >= 60) return 'Alert';
    if (level >= 40) return 'Slightly Drowsy';
    return 'Drowsy';
  };

  const getProgressColor = (level) => {
    if (level >= 80) return 'bg-green-500';
    if (level >= 60) return 'bg-yellow-500';
    if (level >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-4">
      {/* Confidence Display */}
      <div className="text-center">
        <div className="text-4xl font-bold text-gray-800 mb-2">
          {Math.round(displayConfidence)}%
        </div>
        <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getConfidenceColor(displayConfidence)}`}>
          {displayAlertness || getConfidenceStatus(displayConfidence)}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm text-gray-600">
          <span>Confidence Level</span>
          <span>{Math.round(displayConfidence)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ease-out ${getProgressColor(displayConfidence)}`}
            style={{ width: `${displayConfidence}%` }}
          ></div>
        </div>
      </div>

      {/* Confidence Indicators */}
      <div className="grid grid-cols-4 gap-2 text-xs">
        <div className="text-center">
          <div className="w-2 h-2 bg-red-500 rounded-full mx-auto mb-1"></div>
          <span className="text-gray-600">Drowsy</span>
        </div>
        <div className="text-center">
          <div className="w-2 h-2 bg-orange-500 rounded-full mx-auto mb-1"></div>
          <span className="text-gray-600">Slight</span>
        </div>
        <div className="text-center">
          <div className="w-2 h-2 bg-yellow-500 rounded-full mx-auto mb-1"></div>
          <span className="text-gray-600">Alert</span>
        </div>
        <div className="text-center">
          <div className="w-2 h-2 bg-green-500 rounded-full mx-auto mb-1"></div>
          <span className="text-gray-600">Very Alert</span>
        </div>
      </div>

      {/* Detailed Metrics */}
      <div className="bg-gray-50 rounded-lg p-4 space-y-3">
        <h4 className="font-semibold text-gray-800">Detection Metrics</h4>
                 <div className="grid grid-cols-2 gap-4 text-sm">
           <div>
             <span className="text-gray-600"> Eye Closure:</span>
             <span className="floatright font-medium text-gray-600">
               {newMetrics.eyeClosure || 'Unknown' }
               {/* This state is no longer needed */}
             </span>
           </div>
           <div>
             <span className="text-gray-600">Blink Rate:</span>
             <span className="float-right font-medium text-gray-600">
               { newMetrics.blinkRate || 0 }
               {/* This state is no longer needed */}
             </span>
           </div>
           <div>
             <span className="text-gray-600">Head Position:</span>
             <span className="float-right font-medium text-gray-600">
               {newMetrics.headPosition || 'Unknown' }
               {/* This state is no longer needed */}
             </span>
           </div>
           <div>
             {/* <span className="text-gray-600">Yawn Count:</span> */}
             {/* <span className="float-right font-medium text-gray-600"> */}
               {/* { newMetrics.yawnCount || 0 } */}
               {/* This state is no longer needed */}
             {/* </span> */}
           </div>
         </div>
      </div>

             {/* Alert Status */}
       {mlService.shouldTriggerAlert(displayConfidence) && (
         <div className="bg-red-50 border border-red-200 rounded-lg p-4">
           <div className="flex items-center">
             <svg className="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
               <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
             </svg>
             <span className="text-red-800 font-medium">Drowsiness Alert!</span>
           </div>
           <p className="text-red-700 text-sm mt-1">
             {mlService.getAlertMessage(displayConfidence)}
           </p>
         </div>
       )}
    </div>
  );
} 