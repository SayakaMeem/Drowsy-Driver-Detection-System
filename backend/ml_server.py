#!/usr/bin/env python3
"""
Drowsiness Detection ML Server
Loads and serves the trained Keras models for real-time drowsiness detection
"""

import os
import sys
import json
import base64
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
from PIL import Image
import io
import tensorflow as tf
from tensorflow import keras
import logging
import time # Import time for blink analysis

# Configure logging at the very beginning to ensure 'logger' is defined globally
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s') # Added format for clearer logs
logger = logging.getLogger(__name__)

# Import face detector module
try:
    # This import matches the structure of your provided face_detector.py
    from face_detector import FaceDetector
    FACE_DETECTOR_AVAILABLE = True
except ImportError as e:
    FACE_DETECTOR_AVAILABLE = False
    logger.error(f"Error importing FaceDetector module: {e}. Face detection will be disabled.")

# Import drowsiness analyzer module
try:
    from drowsiness_analyzer import DrowsinessAnalyzer
    DROWSINESS_ANALYZER_AVAILABLE = True
except ImportError as e:
    DROWSINESS_ANALYZER_AVAILABLE = False
    logger.error(f"Error importing DrowsinessAnalyzer: {e}. Advanced metrics will be limited.")


app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

class DrowsinessDetector:
    def __init__(self):
        self.model = None
        self.model_path = None
        self.is_loaded = False
        # IMPORTANT: Input shape remains (224, 224, 3) as per your provided base code
        # This is the input shape for the overall system, but the drowsiness model
        # itself expects a specific input size (e.g., 80x80).
        self.input_shape = (224, 224, 3) 
        # Define the actual input shape for the drowsiness classification model
        # This is crucial for models like InceptionV3, ResNet50, MobileNet trained on 80x80.
        self.drowsiness_model_input_shape = (80, 80, 3)
        
        # Initialize face detector using the factory function from face_detector.py
        if FACE_DETECTOR_AVAILABLE:
            self.face_detector = FaceDetector()
        else:
            self.face_detector = None
            logger.warning("Face detection will not be used as FaceDetector is not available.")

        # Initialize the DrowsinessAnalyzer
        if DROWSINESS_ANALYZER_AVAILABLE:
            self.drowsiness_analyzer = DrowsinessAnalyzer(
                open_eye_threshold=0.5, # Example: 50% confidence for open eyes
                blink_min_closed_duration_sec=0.08,
                blink_max_closed_duration_sec=0.4,
                blink_refractory_period_sec=0.2,
                blink_rate_window_sec=60,
                drowsiness_increment_per_closed_sec=5,
                drowsiness_decrement_per_open_sec=1,
                max_drowsiness_score=100
            )
        else:
            self.drowsiness_analyzer = None
            logger.warning("DrowsinessAnalyzer not available. Blink rate and detailed alertness will be simulated.")
        
    def load_model(self, model_path):
        """Load the Keras model from the specified path"""
        try:
            logger.info(f"Loading model from: {model_path}")
            
            if not os.path.exists(model_path):
                logger.error(f"Model file not found: {model_path}")
                return False
                
            # Load the Keras model
            self.model = keras.models.load_model(model_path)
            self.model_path = model_path
            self.is_loaded = True
            
            logger.info(f"Model loaded successfully: {model_path}")
            logger.info(f"Model summary: {self.model.summary()}")
            
            # Sanity check: Log the input shape of the loaded model
            # Note: model.input_shape[1:] excludes the batch dimension (None)
            if self.model.input_shape[1:] != self.drowsiness_model_input_shape[0:3]:
                logger.error(f"Loaded model input shape {self.model.input_shape[1:]} does not match expected drowsiness model input shape {self.drowsiness_model_input_shape[0:3]}")
                # You might want to set self.is_loaded = False here if this mismatch is critical
                # and should prevent the server from operating with this model.
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def preprocess_image(self, image_data):
        """
        Preprocess image for model inference, including face detection and eye cropping.
        Returns a dict with left and right eye images (NumPy arrays) and face detection landmarks (list).
        """
        face_landmarks_results = []
        left_eye_img = None
        right_eye_img = None
        try:
            # Decode base64 image
            if isinstance(image_data, str):
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                image_bytes = base64.b64decode(image_data)
                original_pil_image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            else:
                original_pil_image = Image.open(io.BytesIO(image_data)).convert('RGB')
            logger.debug(f"Original PIL image mode: {original_pil_image.mode}, size: {original_pil_image.size}")
            
            if self.face_detector is not None and self.face_detector.is_face_detection_available():
                # Detect faces and get landmarks
                faces = self.face_detector.detect_faces(original_pil_image)
                if faces:
                    for face in faces:
                        face_landmarks_results.append({
                            'box': [int(val) for val in face['box']],
                            'keypoints': {k: [int(v_coord) for v_coord in v] for k, v in face['keypoints'].items()},
                            'confidence': float(face['confidence'])
                        })
                    # Crop eyes from the largest face for prediction
                    largest_face = max(faces, key=lambda face: face['box'][2] * face['box'][3])
                    left_eye_pil, right_eye_pil = self.face_detector.crop_eyes(
                        original_pil_image, largest_face, eye_size=(self.drowsiness_model_input_shape[0], self.drowsiness_model_input_shape[1]), padding=0.3)
                    if left_eye_pil is not None and right_eye_pil is not None:
                        left_eye_img = np.array(left_eye_pil).astype('float32') / 255.0
                        right_eye_img = np.array(right_eye_pil).astype('float32') / 255.0
                        left_eye_img = np.expand_dims(left_eye_img, axis=0)
                        right_eye_img = np.expand_dims(right_eye_img, axis=0)
                        logger.info(f"Eyes cropped successfully to {self.drowsiness_model_input_shape}")
                    else:
                        logger.warning("Eye cropping failed.")
                else:
                    logger.warning("No face detected in image.")
            else:
                logger.info("Face detection not available.")
            
            if left_eye_img is None or right_eye_img is None:
                logger.warning("Eye cropping failed. Returning None for eye images.")
            return {'left_eye': left_eye_img, 'right_eye': right_eye_img, 'face_landmarks_results': face_landmarks_results}
        except Exception as e:
            logger.error(f"Error in preprocess_image: {str(e)}")
            return {'left_eye': None, 'right_eye': None, 'face_landmarks_results': []}

    def predict(self, image_data):
        """Run inference on the preprocessed left and right eye images and include face detection results."""
        try:
            if not self.is_loaded:
                raise ValueError("Model not loaded")
            preprocessed = self.preprocess_image(image_data)
            left_eye_img = preprocessed['left_eye']
            right_eye_img = preprocessed['right_eye']
            face_landmarks_results = preprocessed['face_landmarks_results']
            if left_eye_img is None or right_eye_img is None:
                logger.error("Failed to preprocess eye images for prediction.")
                return {
                    'success': False,
                    'error': 'Eye image preprocessing failed',
                    'left_eye_confidence': 0,
                    'right_eye_confidence': 0,
                    'left_eye_prediction': [],
                    'right_eye_prediction': [],
                    'model_used': os.path.basename(self.model_path) if self.model_path else None,
                    'face_landmarks_results': face_landmarks_results
                }
            # Run inference for each eye
            left_pred = self.model.predict(left_eye_img, verbose=0)
            right_pred = self.model.predict(right_eye_img, verbose=0)
            # Assuming binary classification: [closed_prob, open_prob]. Index 1 is 'Open-Eyes'
            left_conf = float(left_pred[0][1]) * 100
            right_conf = float(right_pred[0][1]) * 100
            left_conf = max(0, min(100, left_conf))
            right_conf = max(0, min(100, right_conf))
            logger.info(f"Left eye prediction: {left_pred.tolist()}, confidence: {left_conf:.2f}%")
            logger.info(f"Right eye prediction: {right_pred.tolist()}, confidence: {right_conf:.2f}%")
            return {
                'success': True,
                'left_eye_confidence': left_conf,
                'right_eye_confidence': right_conf,
                'left_eye_prediction': left_pred.tolist(),
                'right_eye_prediction': right_pred.tolist(),
                'model_used': os.path.basename(self.model_path) if self.model_path else None,
                'face_landmarks_results': face_landmarks_results
            }
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'left_eye_confidence': 0,
                'right_eye_confidence': 0,
                'left_eye_prediction': [],
                'right_eye_prediction': [],
                'model_used': os.path.basename(self.model_path) if self.model_path else None,
                'face_landmarks_results': []
            }

# Global detector instance
detector = DrowsinessDetector()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': detector.is_loaded,
        'model_path': detector.model_path if detector.is_loaded else None,
        # Updated check for face_detector availability
        'face_detection_available': detector.face_detector.is_face_detection_available() if detector.face_detector else False,
        'drowsiness_analyzer_available': DROWSINESS_ANALYZER_AVAILABLE,
        'timestamp': str(np.datetime64('now'))
    })

@app.route('/load-model', methods=['POST'])
def load_model_endpoint(): # Renamed to avoid conflict with class method
    """Load a specific model"""
    try:
        data = request.get_json()
        model_path = data.get('model_path')
        
        if not model_path:
            return jsonify({'error': 'No model path provided'}), 400
        
        # Try to load the model
        success = detector.load_model(model_path)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Model loaded successfully: {model_path}',
                'model_path': model_path
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to load model: {model_path}'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in load-model endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/detect-drowsiness', methods=['POST'])
def detect_drowsiness():
    """Main drowsiness detection endpoint"""
    try:
        data = request.get_json()
        image_data = data.get('image')
        timestamp = data.get('timestamp')
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        drowsiness_prediction_result = detector.predict(image_data)
        left_eye_conf = drowsiness_prediction_result['left_eye_confidence']
        right_eye_conf = drowsiness_prediction_result['right_eye_confidence']
        logger.info(f"👁️👁️👁️👁️Left eye confidence: {left_eye_conf}, Right eye confidence: {right_eye_conf}")
        # Optionally, you can run drowsiness analyzer logic for each eye or combine
        response = {
            'success': drowsiness_prediction_result['success'],
            'left_eye_confidence': left_eye_conf,
            'right_eye_confidence': right_eye_conf,
            'left_eye_prediction': drowsiness_prediction_result['left_eye_prediction'],
            'right_eye_prediction': drowsiness_prediction_result['right_eye_prediction'],
            'model_used': drowsiness_prediction_result['model_used'],
            'face_detection_landmarks': drowsiness_prediction_result.get('face_landmarks_results', [])
        }
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in drowsiness detection endpoint: {str(e)}")
        return jsonify({'error': 'Detection failed', 'details': str(e)}), 500

@app.route('/detect-faces', methods=['POST'])
def detect_faces():
    """Face detection endpoint"""
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode image
        if isinstance(image_data, str):
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
        else:
            image = Image.open(io.BytesIO(image_data))
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Detect faces
        if detector.face_detector is None:
            return jsonify({
                'success': False,
                'error': 'Face detection not available',
                'face_detection_available': False
            }), 500
        
        faces = detector.face_detector.detect_faces(image)
        
        # Process face data
        face_data = []
        for face in faces:
            bbox = face['box']
            confidence = detector.face_detector.get_face_confidence(face)
            keypoints = detector.face_detector.get_face_keypoints(face)
            
            # Convert numpy types to Python types for JSON serialization
            bbox = [int(x) for x in bbox]
            confidence = float(confidence)
            
            # Convert keypoints to serializable format
            serializable_keypoints = {}
            for key, value in keypoints.items():
                if value is not None:
                    serializable_keypoints[key] = [int(x) for x in value]
                else:
                    serializable_keypoints[key] = None
            
            face_data.append({
                'bbox': bbox,  # [x, y, width, height]
                'confidence': confidence,
                'keypoints': serializable_keypoints
            })
        
        return jsonify({
            'success': True,
            'faces_detected': len(faces),
            'faces': face_data,
            'face_detection_available': detector.face_detector.is_face_detection_available(),
            'detection_stats': detector.face_detector.get_detection_stats()
        })
        
    except Exception as e:
        logger.error(f"Error in face detection: {str(e)}")
        return jsonify({
            'error': 'Face detection failed',
            'details': str(e)
        }), 500

@app.route('/models', methods=['GET'])
def list_models():
    """List available models from the models directory"""
    try:
        # Look for model files in the models directory
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        # Corrected path: models are in backend/app/models
        models_dir = os.path.join(backend_dir, 'app', 'models')
        model_files = []
        
        logger.info(f"Looking for models in: {models_dir}")
        
        if os.path.exists(models_dir):
            for file in os.listdir(models_dir):
                if file.endswith(('.keras', '.h5')):
                    model_path = os.path.join(models_dir, file)
                    model_files.append({
                        'name': file,
                        'path': model_path,
                        'size': os.path.getsize(model_path)
                    })
                    logger.info(f"Found model: {file}")
        else:
            logger.warning(f"Models directory not found: {models_dir}")
        
        logger.info(f"Total models found: {len(model_files)}")
        
        return jsonify({
            'models': model_files,
            'current_model': detector.model_path if detector.is_loaded else None,
            'face_detection_available': detector.face_detector.is_face_detection_available() if detector.face_detector else False,
            'drowsiness_analyzer_available': DROWSINESS_ANALYZER_AVAILABLE
        })
        
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/debug/models', methods=['GET'])
def debug_models():
    """Debug endpoint to check model locations"""
    try:
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        # Corrected path: models are in backend/app/models
        models_dir = os.path.join(backend_dir, 'app', 'models')
        
        backend_files = os.listdir(backend_dir)
        models_dir_files = os.listdir(models_dir) if os.path.exists(models_dir) else []
        
        return jsonify({
            'backend_directory': backend_dir,
            'models_directory': models_dir,
            'backend_files': [f for f in backend_files if f.endswith(('.keras', '.h5'))],
            'models_dir_files': [f for f in models_dir_files if f.endswith(('.keras', '.h5'))],
            'all_backend_files': backend_files[:10],
            'all_models_dir_files': models_dir_files[:10]
        })
        
    except Exception as e:
        logger.error(f"Error in debug/models: {str(e)}")
        return jsonify({'error': str(e)}), 500

# These functions are now fallbacks if DrowsinessAnalyzer is not available
# They are kept to ensure the code functions even without the analyzer module.
def generate_metrics(confidence):
    """Generate detection metrics based on confidence (fallback)"""
    base_blink_rate = 15
    base_yawn_count = np.random.randint(0, 3)
    
    return {
        'eyeClosure': 'Normal' if confidence > 50 else 'Detected',
        'blinkRate': int(base_blink_rate + (100 - confidence) / 10),
        'headPosition': 'Upright' if confidence > 70 else 'Tilting',
        'yawnCount': base_yawn_count + (3 if confidence < 40 else 0),
        'eyeAspectRatio': (confidence / 100) * 0.3 + 0.2, # Simulated
        'mouthAspectRatio': (confidence / 100) * 0.2 + 0.1, # Simulated
        'pupilDiameter': (confidence / 100) * 2 + 3, # Simulated
        'eyeMovement': 'Active' if confidence > 60 else 'Reduced' # Simulated
    }

def get_alertness_level(confidence):
    """Get alertness level based on confidence (fallback)"""
    if confidence >= 80:
        return 'Very Alert'
    elif confidence >= 60:
        return 'Alert'
    elif confidence >= 40:
        return 'Slightly Drowsy'
    elif confidence >= 20:
        return 'Drowsy'
    else:
        return 'Very Drowsy'

if __name__ == '__main__':
    # Try to load the default model on startup from models directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    # Corrected path: models are in backend/app/models
    models_dir = os.path.join(backend_dir, 'app', 'models') 
    
    logger.info(f"Backend directory: {backend_dir}")
    logger.info(f"Models directory to check: {models_dir}")
    
    if os.path.exists(models_dir):
        logger.info(f"Available files in models directory:")
        for file in os.listdir(models_dir):
            logger.info(f"   - {file}")
    else:
        logger.warning(f"Models directory does not exist: {models_dir}")
    
    # Try to find a suitable default model in the models directory
    default_models = [
        'drowsiness_mobilenet_model.h5',  # Smallest and fastest
        'best_mobilenet_model.h5',
        'drowsiness_vgg16_model.h5',
        'best_vgg16_model.h5',
        'drowsiness_inceptionv3_model.h5',
        'best_inceptionv3_model.h5',
        'drowsiness_resnet_model.h5',
        'best_resnet_model.h5'
    ]
    
    default_model_loaded = False
    for model_name in default_models:
        default_model_path = os.path.join(models_dir, model_name)
        logger.info(f"Checking for model: {default_model_path}")
        if os.path.exists(default_model_path):
            logger.info(f"Loading default model: {default_model_path}")
            if detector.load_model(default_model_path):
                default_model_loaded = True
                break
            else:
                logger.warning(f"Failed to load model: {default_model_path}")
        else:
            logger.info(f"Model not found: {default_model_path}")
    
    if not default_model_loaded:
        logger.warning("No suitable default model found in models directory")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
