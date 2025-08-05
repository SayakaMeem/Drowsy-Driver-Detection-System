'use client';
import { useEffect, useRef } from 'react';

export default function FaceDetectionOverlay({ faceDetection, videoElement }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!faceDetection || !videoElement || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Set canvas size to match video
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;
    
    // Clear previous drawings
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    if (faceDetection.success) {
      // Draw face rectangles
      faceDetection.face_regions.forEach(face => {
        ctx.strokeStyle = '#00ff00';
        ctx.lineWidth = 2;
        ctx.strokeRect(face.x, face.y, face.width, face.height);
        
        // Add face label
        ctx.fillStyle = '#00ff00';
        ctx.font = '14px Arial';
        ctx.fillText('Face', face.x, face.y - 5);
      });
      
      // Draw eye rectangles
      faceDetection.eye_regions.forEach(eye => {
        ctx.strokeStyle = '#ff0000';
        ctx.lineWidth = 2;
        ctx.strokeRect(eye.x, eye.y, eye.width, eye.height);
        
        // Add eye label
        ctx.fillStyle = '#ff0000';
        ctx.font = '12px Arial';
        ctx.fillText('Eye', eye.x, eye.y - 5);
      });
    }
  }, [faceDetection, videoElement]);

  if (!faceDetection || !faceDetection.success) {
    return null;
  }

  return (
    <canvas
      ref={canvasRef}
      className="absolute top-0 left-0 pointer-events-none"
      style={{
        width: '100%',
        height: '100%',
        zIndex: 10
      }}
    />
  );
} 