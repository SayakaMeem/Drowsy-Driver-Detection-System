'use client';
import { useEffect, useRef, useState } from 'react';

export default function FaceDetectionOverlay({ faceDetection, videoElement, isDetecting }) {
  const canvasRef = useRef(null);
  const [faceData, setFaceData] = useState(null);

  useEffect(() => {
    if (!faceDetection || !videoElement || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Set canvas size to match video
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;
    
    // Clear previous drawings
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Handle different face detection data formats
    if (faceDetection.success && faceDetection.faces && faceDetection.faces.length > 0) {
      // New format from Python backend
      faceDetection.faces.forEach((face, index) => {
        const bbox = face.bbox; // [x, y, width, height]
        const confidence = face.confidence;
        
        // Draw face rectangle
        ctx.strokeStyle = confidence > 0.8 ? '#00ff00' : confidence > 0.6 ? '#ffff00' : '#ff0000';
        ctx.lineWidth = 3;
        ctx.strokeRect(bbox[0], bbox[1], bbox[2], bbox[3]);
        
        // Add face label with confidence
        ctx.fillStyle = ctx.strokeStyle;
        ctx.font = 'bold 14px Arial';
        ctx.fillText(`Face ${index + 1} (${Math.round(confidence * 100)}%)`, bbox[0], bbox[1] - 10);
        
        // Draw keypoints if available
        if (face.keypoints) {
          const keypoints = face.keypoints;
          ctx.fillStyle = '#00ffff';
          ctx.lineWidth = 2;
          
          // Draw keypoints
          Object.values(keypoints).forEach(point => {
            if (point && point.length === 2) {
              ctx.beginPath();
              ctx.arc(point[0], point[1], 3, 0, 2 * Math.PI);
              ctx.fill();
            }
          });
          
          // Draw connections between keypoints
          ctx.strokeStyle = '#00ffff';
          ctx.lineWidth = 1;
          
          // Eye connections
          if (keypoints.left_eye && keypoints.right_eye) {
            ctx.beginPath();
            ctx.moveTo(keypoints.left_eye[0], keypoints.left_eye[1]);
            ctx.lineTo(keypoints.right_eye[0], keypoints.right_eye[1]);
            ctx.stroke();
          }
          
          // Nose to mouth connections
          if (keypoints.nose && keypoints.mouth_left && keypoints.mouth_right) {
            ctx.beginPath();
            ctx.moveTo(keypoints.nose[0], keypoints.nose[1]);
            ctx.lineTo(keypoints.mouth_left[0], keypoints.mouth_left[1]);
            ctx.moveTo(keypoints.nose[0], keypoints.nose[1]);
            ctx.lineTo(keypoints.mouth_right[0], keypoints.mouth_right[1]);
            ctx.stroke();
          }
        }
      });
      
      setFaceData(faceDetection.faces);
    } else if (faceDetection.face_regions && faceDetection.face_regions.length > 0) {
      // Legacy format
      faceDetection.face_regions.forEach((face, index) => {
        ctx.strokeStyle = '#00ff00';
        ctx.lineWidth = 2;
        ctx.strokeRect(face.x, face.y, face.width, face.height);
        
        // Add face label
        ctx.fillStyle = '#00ff00';
        ctx.font = '14px Arial';
        ctx.fillText(`Face ${index + 1}`, face.x, face.y - 5);
      });
      
      // Draw eye rectangles
      if (faceDetection.eye_regions) {
        faceDetection.eye_regions.forEach((eye, index) => {
          ctx.strokeStyle = '#ff0000';
          ctx.lineWidth = 2;
          ctx.strokeRect(eye.x, eye.y, eye.width, eye.height);
          
          // Add eye label
          ctx.fillStyle = '#ff0000';
          ctx.font = '12px Arial';
          ctx.fillText(`Eye ${index + 1}`, eye.x, eye.y - 5);
        });
      }
    }
  }, [faceDetection, videoElement]);

  // Don't render if no face detection data or not detecting
  if (!faceDetection || !isDetecting) {
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