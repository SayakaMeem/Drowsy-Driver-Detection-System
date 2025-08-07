#!/usr/bin/env python3
"""
Face Detection Module using MTCNN
Provides face detection and cropping functionality for drowsiness detection
"""

import cv2
import numpy as np
from mtcnn.mtcnn import MTCNN
import logging
from PIL import Image

logger = logging.getLogger(__name__)

class FaceDetector:
    """
    A class to handle face detection using MTCNN.
    """
    def __init__(self):
        logger.info("Initializing MTCNN face detector...")
        self.detector = MTCNN()
        logger.info("MTCNN face detector initialized.")

    def is_face_detection_available(self):
        # Always True if the detector is initialized
        return self.detector is not None

    def detect_and_crop_face(self, image, padding=0.2, target_size=(80, 80)):
        """
        Detect faces and crop the largest one with padding support.
        Returns (cropped_face_pil, face_data, bbox) or (None, None, None) if failed.
        """
        try:
            # Convert PIL image to numpy array if needed
            if isinstance(image, Image.Image):
                image_np_rgb = np.array(image)
            else:
                image_np_rgb = image

            if image_np_rgb is None or image_np_rgb.size == 0:
                logger.error("Input image for face detection is empty or None.")
                return None, None, None

            faces = self.detector.detect_faces(image_np_rgb)
            if not faces:
                logger.warning("No face detected in the image.")
                return None, None, None

            # Get largest face
            largest_face = max(faces, key=lambda face: face['box'][2] * face['box'][3])
            x, y, width, height = largest_face['box']
            
            # Add padding
            img_h, img_w, _ = image_np_rgb.shape
            pad_x = int(width * padding)
            pad_y = int(height * padding)
            
            # Calculate new coordinates with padding
            x1 = max(0, x - pad_x)
            y1 = max(0, y - pad_y)
            x2 = min(img_w, x + width + pad_x)
            y2 = min(img_h, y + height + pad_y)
            
            # Crop the face
            cropped_face = image_np_rgb[y1:y2, x1:x2]
            if cropped_face.size == 0:
                logger.warning("Cropped face region is empty after padding.")
                return None, None, None
            
            # Convert to PIL Image and resize
            cropped_face_pil = Image.fromarray(cropped_face)
            if target_size:
                cropped_face_pil = cropped_face_pil.resize(target_size, Image.Resampling.LANCZOS)
            
            bbox = (x1, y1, x2, y2)
            return cropped_face_pil, largest_face, bbox
            
        except Exception as e:
            logger.error(f"Error in detect_and_crop_face: {str(e)}")
            return None, None, None

    def detect_faces(self, image):
        """Detect all faces in the image"""
        try:
            if isinstance(image, Image.Image):
                image_np_rgb = np.array(image)
            else:
                image_np_rgb = image
            
            if image_np_rgb is None or image_np_rgb.size == 0:
                return []
            
            faces = self.detector.detect_faces(image_np_rgb)
            return faces
        except Exception as e:
            logger.error(f"Error in detect_faces: {str(e)}")
            return []

    def get_face_confidence(self, face_data):
        """Get confidence score for detected face"""
        return face_data.get('confidence', 0.0)

    def get_face_keypoints(self, face_data):
        """Get facial landmarks from face detection result"""
        return face_data.get('keypoints', {})

    def get_face_landmarks(self, image_np_rgb):
        if image_np_rgb is None or image_np_rgb.size == 0:
            logger.error("Input image for landmark detection is empty or None.")
            return []
        faces = self.detector.detect_faces(image_np_rgb)
        formatted_faces = []
        for face in faces:
            formatted_faces.append({
                'box': [int(val) for val in face['box']],
                'keypoints': {key: [int(val) for val in value] for key, value in face['keypoints'].items()},
                'confidence': float(face['confidence'])
            })
        return formatted_faces

    def crop_eyes(self, image, face_data, eye_size=(40, 40), padding=0.3):
        """
        Crop left and right eye regions from the image using face_data keypoints.
        Returns (left_eye_pil, right_eye_pil) or (None, None) if failed.
        """
        try:
            if isinstance(image, Image.Image):
                image_np = np.array(image)
            else:
                image_np = image
            keypoints = face_data.get('keypoints', {})
            left_eye = keypoints.get('left_eye')
            right_eye = keypoints.get('right_eye')
            if left_eye is None or right_eye is None:
                return None, None
            for eye, name in zip([left_eye, right_eye], ['left', 'right']):
                x, y = eye
                w, h = eye_size
                pad_w = int(w * padding)
                pad_h = int(h * padding)
                x1 = max(0, x - w//2 - pad_w)
                y1 = max(0, y - h//2 - pad_h)
                x2 = min(image_np.shape[1], x + w//2 + pad_w)
                y2 = min(image_np.shape[0], y + h//2 + pad_h)
                crop = image_np[y1:y2, x1:x2]
                if crop.size == 0:
                    return None, None
                pil_crop = Image.fromarray(crop).resize(eye_size, Image.Resampling.LANCZOS)
                if name == 'left':
                    left_eye_pil = pil_crop
                else:
                    right_eye_pil = pil_crop
            return left_eye_pil, right_eye_pil
        except Exception as e:
            logger.error(f"Error in crop_eyes: {str(e)}")
            return None, None

    def get_detection_stats(self):
        """Get face detection statistics and configuration"""
        return {
            'available': self.is_face_detection_available(),
            'initialized': self.detector is not None,
            'min_face_size': 20,
            'scale_factor': 0.709,
            'steps_threshold': (0.6, 0.7, 0.7)
        }
