#!/usr/bin/env python3
"""
Face Detection Module using MTCNN
Provides face detection and cropping functionality for drowsiness detection
"""

import os
import numpy as np
from PIL import Image
import logging
import cv2 # Added for color space conversions

# MTCNN for face detection
try:
    from mtcnn import MTCNN
    MTCNN_AVAILABLE = True
except ImportError:
    MTCNN_AVAILABLE = False
    print("Warning: MTCNN not available. Install with: pip install mtcnn")

# Configure logging
logger = logging.getLogger(__name__)

class FaceDetector:
    """Face detection using MTCNN"""
    
    def __init__(self, min_face_size=20, scale_factor=0.709, steps_threshold=(0.6, 0.7, 0.7)):
        """
        Initialize MTCNN face detector
        
        Args:
            min_face_size (int): Minimum face size to detect
            scale_factor (float): Scale factor for image pyramid
            steps_threshold (tuple): Thresholds for the three stages of MTCNN
        """
        self.detector = None
        self.is_available = MTCNN_AVAILABLE
        self.min_face_size = min_face_size
        self.scale_factor = scale_factor
        self.steps_threshold = steps_threshold
        
        if self.is_available:
            try:
                # MTCNN constructor doesn't accept these parameters directly
                # We'll use the default constructor and set parameters later if needed
                self.detector = MTCNN()
                logger.info("MTCNN face detector initialized successfully")
                logger.info(f"Using default MTCNN parameters")
            except Exception as e:
                logger.error(f"Failed to initialize MTCNN: {str(e)}")
                self.is_available = False
        else:
            logger.warning("MTCNN not available. Face detection will be disabled.")
    
    def detect_faces(self, image):
        """
        Detect faces in the image and return bounding boxes
        
        Args:
            image: PIL Image or numpy array
            
        Returns:
            list: List of detected faces with bounding boxes and keypoints
        """
        if not self.is_available or self.detector is None:
            return []
        
        try:
            # Convert PIL image to numpy array if needed
            if isinstance(image, Image.Image):
                image_array = np.array(image)
            else:
                image_array = image
            
            # Ensure image is in RGB format for MTCNN, handling various input formats
            if len(image_array.shape) == 2: # Grayscale (H, W)
                image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
            elif len(image_array.shape) == 3 and image_array.shape[2] == 4: # RGBA (H, W, 4)
                image_array = image_array[:, :, :3] # Convert to RGB
            elif len(image_array.shape) == 3 and image_array.shape[2] == 1: # Grayscale with channel dim (H, W, 1)
                image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
            # If it's already (H, W, 3), it will pass through

            logger.debug(f"Input image_array shape for MTCNN detection: {image_array.shape}") # Debug log
            
            # Detect faces
            faces = self.detector.detect_faces(image_array)
            logger.info(f"📹Detected {len(faces)} faces in image") # Corrected: Log after detection
            
            return faces
            
        except Exception as e:
            logger.error(f"Error in face detection: {str(e)}")
            return []
    
    def crop_face(self, image, face_data, padding=0.2, target_size=None):
        """
        Crop the detected face with optional padding
        
        Args:
            image: PIL Image or numpy array
            face_data (dict): Face detection result from MTCNN
            padding (float): Padding factor around the face (0.2 = 20% padding)
            target_size (tuple): Optional target size for the cropped face (width, height)
            
        Returns:
            tuple: (cropped_image, bounding_box) or (None, None) if failed
        """
        try:
            if isinstance(image, Image.Image):
                # Ensure PIL image is RGB before converting to numpy
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image_array = np.array(image)
            elif isinstance(image, np.ndarray):
                # Ensure numpy array is 3-channel RGB before cropping
                if len(image.shape) == 2: # Grayscale (H, W)
                    image_array = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
                elif len(image.shape) == 3 and image.shape[2] == 4: # RGBA (H, W, 4)
                    image_array = image[:, :, :3] # Convert to RGB
                elif len(image.shape) == 3 and image.shape[2] == 1: # Grayscale with channel dim (H, W, 1)
                    image_array = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
                else: # Assume it's already RGB (H, W, 3) or other valid format
                    image_array = image
            else:
                raise ValueError("Image must be PIL Image or numpy array")

            logger.debug(f"Input image_array shape in crop_face: {image_array.shape}")

            # Get bounding box
            x, y, width, height = face_data['box']
            
            # Add padding
            img_height, img_width = image_array.shape[:2]
            pad_x = int(width * padding)
            pad_y = int(height * padding)
            
            # Calculate new coordinates with padding
            x1 = max(0, x - pad_x)
            y1 = max(0, y - pad_y)
            x2 = min(img_width, x + width + pad_x)
            y2 = min(img_height, y + height + pad_y)
            
            logger.debug(f"Crop coords: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
            logger.debug(f"Image dims: img_width={img_width}, img_height={img_height}")

            # --- IMPORTANT: Check for valid dimensions BEFORE cropping ---
            if x1 >= x2 or y1 >= y2:
                logger.error(f"Invalid crop dimensions after padding: x1={x1}, x2={x2}, y1={y1}, y2={y2}. Cannot crop.")
                return None, None

            # Crop the face
            face_crop = image_array[y1:y2, x1:x2]
            logger.debug(f"Shape of face_crop before Image.fromarray: {face_crop.shape}")
            
            # Convert back to PIL Image
            face_image = Image.fromarray(face_crop)
            
            # Resize to target size if specified
            if target_size:
                logger.debug(f"Resizing cropped face from {face_image.size} to {target_size}")
                face_image = face_image.resize(target_size, Image.Resampling.LANCZOS)
            
            bbox = (x1, y1, x2, y2)
            logger.info(f"✅Face cropped successfully: {bbox}")
            
            return face_image, bbox
            
        except Exception as e:
            logger.error(f"❌Error cropping face: {str(e)}")
            return None, None
    
    def get_largest_face(self, faces):
        """
        Get the largest face from detected faces
        
        Args:
            faces (list): List of detected faces
            
        Returns:
            dict: Largest face data or None if no faces
        """
        if not faces:
            return None
        
        # Sort by face area (width * height)
        faces_with_area = [(face, face['box'][2] * face['box'][3]) for face in faces]
        faces_with_area.sort(key=lambda x: x[1], reverse=True)
        
        largest_face = faces_with_area[0][0]
        logger.info(f"Selected largest face with area: {faces_with_area[0][1]} pixels")
        
        return largest_face
    
    def get_face_keypoints(self, face_data):
        """
        Extract key facial landmarks from face detection result
        
        Args:
            face_data (dict): Face detection result from MTCNN
            
        Returns:
            dict: Dictionary of facial landmarks
        """
        keypoints = face_data.get('keypoints', {})
        
        landmarks = {
            'left_eye': keypoints.get('left_eye', None),
            'right_eye': keypoints.get('right_eye', None),
            'nose': keypoints.get('nose', None),
            'mouth_left': keypoints.get('mouth_left', None),
            'mouth_right': keypoints.get('mouth_right', None)
        }
        
        return landmarks
    
    def detect_and_crop_largest_face(self, image, padding=0.2, target_size=None):
        """
        Detect faces and crop the largest one
        
        Args:
            image: PIL Image or numpy array
            padding (float): Padding factor around the face
            target_size (tuple): Optional target size for the cropped face
            
        Returns:
            tuple: (cropped_image, face_data, bbox) or (None, None, None) if failed
        """
        # Detect faces
        faces = self.detect_faces(image)
        
        if not faces:
            logger.warning("No faces detected in image")
            return None, None, None
        
        # Get largest face
        largest_face = self.get_largest_face(faces)
        
        if largest_face is None:
            logger.warning("Failed to get largest face (should not happen if faces were detected)")
            return None, None, None
        
        # Crop the face
        face_image, bbox = self.crop_face(image, largest_face, padding, target_size)
        
        if face_image is None:
            logger.warning("Failed to crop face")
            return None, None, None
        
        return face_image, largest_face, bbox
    
    def get_face_confidence(self, face_data):
        """
        Get confidence score for detected face
        
        Args:
            face_data (dict): Face detection result from MTCNN
            
        Returns:
            float: Confidence score (0-1)
        """
        return face_data.get('confidence', 0.0)
    
    def is_face_detection_available(self):
        """
        Check if face detection is available
        
        Returns:
            bool: True if MTCNN is available and initialized
        """
        return self.is_available and self.detector is not None
    
    def get_detection_stats(self):
        """
        Get face detection statistics and configuration
        
        Returns:
            dict: Detection statistics and configuration
        """
        return {
            'available': self.is_available,
            'initialized': self.detector is not None,
            'min_face_size': self.min_face_size,
            'scale_factor': self.scale_factor,
            'steps_threshold': self.steps_threshold
        }

# Utility functions
def create_face_detector(min_face_size=20, scale_factor=0.709, steps_threshold=(0.6, 0.7, 0.7)):
    """
    Factory function to create a face detector
    
    Args:
        min_face_size (int): Minimum face size to detect (not used in current MTCNN version)
        scale_factor (float): Scale factor for image pyramid (not used in current MTCNN version)
        steps_threshold (tuple): Thresholds for the three stages of MTCNN (not used in current MTCNN version)
        
    Returns:
        FaceDetector: Configured face detector instance
    """
    return FaceDetector(min_face_size, scale_factor, steps_threshold)

def validate_image(image):
    """
    Validate and prepare image for face detection
    
    Args:
        image: PIL Image or numpy array
        
    Returns:
        PIL Image: Validated and prepared image
    """
    try:
        if isinstance(image, Image.Image):
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return image
        elif isinstance(image, np.ndarray):
            # Convert numpy array to PIL Image
            if len(image.shape) == 3 and image.shape[2] == 4:
                # Convert RGBA to RGB
                image = image[:, :, :3]
            return Image.fromarray(image)
        else:
            raise ValueError("Image must be PIL Image or numpy array")
    except Exception as e:
        logger.error(f"Error validating image: {str(e)}")
        raise

if __name__ == "__main__":
    # Test the face detector
    logging.basicConfig(level=logging.INFO)
    
    # Create face detector
    detector = create_face_detector()
    
    print(f"Face detection available: {detector.is_face_detection_available()}")
    print(f"Detection stats: {detector.get_detection_stats()}")
