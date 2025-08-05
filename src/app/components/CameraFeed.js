'use client';

import { useRef, useEffect, useState } from 'react';
import mlService from '../services/mlService';
import FaceDetectionOverlay from './FaceDetectionOverlay';

export default function CameraFeed({ isDetecting, onConfidenceUpdate }) {
  const videoRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isModelLoaded, setIsModelLoaded] = useState(false);
  const [faceDetection, setFaceDetection] = useState(null);

  useEffect(() => {
    if (isDetecting && !stream) {
      startCamera();
    } else if (!isDetecting && stream) {
      stopCamera();
    }
  }, [isDetecting]);

  // Initialize ML model when component mounts
  useEffect(() => {
    const initializeML = async () => {
      setIsLoading(true);
      const success = await mlService.initializeModel();
      setIsModelLoaded(success);
      setIsLoading(false);
    };
    
    initializeML();
  }, []);

  // Set up face detection callback
  useEffect(() => {
    mlService.setFaceDetectionCallback((faceData) => {
      setFaceDetection(faceData);
    });
  }, []);

  const startCamera = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        }
      });
      
      setStream(mediaStream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      console.error('Error accessing camera:', err);
      setError('Unable to access camera. Please check permissions.');
    } finally {
      setIsLoading(false);
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    // Stop ML detection
    mlService.stopDetection();
    // Clear face detection data
    setFaceDetection(null);
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  // Start ML detection when video is ready and detecting is active
  useEffect(() => {
    if (isDetecting && stream && videoRef.current && isModelLoaded) {
      mlService.startDetection(videoRef.current, onConfidenceUpdate);
    }
  }, [isDetecting, stream, isModelLoaded, onConfidenceUpdate]);

  return (
    <div className="relative">
      {/* Camera Container */}
      <div className="relative bg-gray-900 rounded-lg overflow-hidden aspect-video">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75 z-10">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-white">
                {!isModelLoaded ? 'Loading ML Model...' : 'Starting camera...'}
              </p>
            </div>
          </div>
        )}

        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75 z-10">
            <div className="text-center p-4">
              <svg className="w-16 h-16 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <p className="text-white text-sm">{error}</p>
              <button
                onClick={startCamera}
                className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {!isDetecting && !error && !isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75 z-10">
            <div className="text-center">
              <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <p className="text-white">Camera inactive</p>
              <p className="text-gray-400 text-sm">Click "Start Detecting" to begin</p>
            </div>
          </div>
        )}

        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-full h-full object-cover"
        />

        {/* Face Detection Overlay */}
        <FaceDetectionOverlay 
          faceDetection={faceDetection}
          videoElement={videoRef.current}
          isDetecting={isDetecting}
        />

        {/* Status Indicators */}
        {isDetecting && stream && (
          <div className="absolute top-4 right-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium z-20">
            Active
          </div>
        )}

        {/* Face Detection Status */}
        {isDetecting && faceDetection && faceDetection.success && (
          <div className="absolute top-4 left-4 bg-blue-500 text-white px-3 py-1 rounded-full text-sm font-medium z-20">
            {faceDetection.faces_detected || 0} Face{faceDetection.faces_detected !== 1 ? 's' : ''} Detected
          </div>
        )}
      </div>

      {/* Camera Controls */}
      <div className="mt-4 flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${isDetecting ? 'bg-green-500' : 'bg-gray-400'}`}></div>
            <span className="text-sm text-gray-600">
              {isDetecting ? 'Recording' : 'Stopped'}
            </span>
          </div>
          
          {/* Face Detection Status */}
          {isDetecting && faceDetection && (
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${faceDetection.success ? 'bg-blue-500' : 'bg-gray-400'}`}></div>
              <span className="text-sm text-gray-600">
                Face Detection: {faceDetection.success ? 'Active' : 'Inactive'}
              </span>
            </div>
          )}
        </div>

        <div className="flex space-x-2">
          <button
            onClick={() => {
              if (isDetecting) {
                stopCamera();
              } else {
                startCamera();
              }
            }}
            className="px-3 py-1 text-sm bg-gray-200 hover:bg-gray-300 rounded transition-colors"
          >
            {isDetecting ? 'Stop' : 'Start'} Camera
          </button>
        </div>
      </div>

      {/* Camera Info */}
      <div className="mt-2 text-xs text-gray-500">
        <p>Resolution: 640x480 | FPS: 30 | Status: {isDetecting ? 'Active' : 'Inactive'}</p>
        {faceDetection && faceDetection.detection_stats && (
          <p>Face Detection: {faceDetection.detection_stats.available ? 'Available' : 'Unavailable'} | 
             Min Face Size: {faceDetection.detection_stats.min_face_size}px</p>
        )}
      </div>
    </div>
  );
} 