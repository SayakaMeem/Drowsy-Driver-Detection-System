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
    from face_detector import create_face_detector, validate_image, FaceDetector 
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
            self.face_detector = create_face_detector()
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
        Preprocess image for model inference, including face detection and cropping.
        Returns the preprocessed image array (NumPy) and face detection landmarks (list).
        
        This function is modified to ensure an image is always returned for the
        drowsiness model, even if face cropping fails.
        """
        face_landmarks_results = [] # Initialize list for face detection results
        image_for_drowsiness_model = None # This will be the PIL Image that goes to the model

        try:
            # Decode base64 image
            if isinstance(image_data, str):
                # Remove data URL prefix if present
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                
                # Decode base64
                image_bytes = base64.b64decode(image_data)
                original_pil_image = Image.open(io.BytesIO(image_bytes)).convert('RGB') # Ensure RGB
            else:
                original_pil_image = Image.open(io.BytesIO(image_data)).convert('RGB') # Ensure RGB

            logger.debug(f"Original PIL image mode: {original_pil_image.mode}, size: {original_pil_image.size}")
            
            # Attempt to detect and crop face if face detection is available
            if self.face_detector is not None and self.face_detector.is_face_detection_available():
                cropped_face_pil, face_data, bbox = self.face_detector.detect_and_crop_largest_face(
                    original_pil_image, 
                    padding=0.2, 
                    target_size=(self.drowsiness_model_input_shape[0], self.drowsiness_model_input_shape[1])
                )
                
                if face_data and cropped_face_pil: # If a face was detected and cropped successfully
                    # Format face_data and bbox for face_landmarks_results
                    face_landmarks_results.append({
                        'box': [int(val) for val in face_data['box']],
                        'keypoints': {k: [int(v_coord) for v_coord in v] for k, v in face_data['keypoints'].items()},
                        'confidence': float(face_data['confidence'])
                    })
                    logger.info(f"Face detected and cropped to {self.drowsiness_model_input_shape}: {bbox}")
                    image_for_drowsiness_model = cropped_face_pil # Use the cropped PIL image
                    logger.debug(f"Using cropped face. PIL image size: {image_for_drowsiness_model.size}")
                else:
                    # Face detection or cropping failed, use original image for drowsiness model
                    logger.warning("Face detection or cropping failed. Using original image (resized) for drowsiness model.")
                    image_for_drowsiness_model = original_pil_image # Fallback to original PIL image
                    logger.debug(f"Using original image as fallback. PIL image size: {image_for_drowsiness_model.size}")
            else:
                # Face detection not available, use original image for drowsiness model
                logger.info("Face detection not available. Using original image (resized) for drowsiness model.")
                image_for_drowsiness_model = original_pil_image # Use original PIL image if face detector not available
                logger.debug(f"Using original image as fallback (no face detector). PIL image size: {image_for_drowsiness_model.size}")
            
            # Ensure image_for_drowsiness_model is a PIL Image before resizing
            if not isinstance(image_for_drowsiness_model, Image.Image):
                logger.error(f"image_for_drowsiness_model is not a PIL Image before final resize: {type(image_for_drowsiness_model)}")
                return None, []

            # This is the crucial resizing step
            # Ensure the image is resized to the drowsiness_model_input_shape (80x80)
            image_for_drowsiness_model = image_for_drowsiness_model.resize(
                (self.drowsiness_model_input_shape[0], self.drowsiness_model_input_shape[1]),
                Image.Resampling.LANCZOS # Use LANCZOS for high quality downsampling
            )
            logger.debug(f"PIL image size AFTER final resize: {image_for_drowsiness_model.size}")
            
            # Convert to numpy array and normalize
            image_array = np.array(image_for_drowsiness_model)
            logger.debug(f"Numpy array shape AFTER PIL conversion: {image_array.shape}")
            image_array = image_array.astype('float32') / 255.0
            
            # Add batch dimension
            image_array = np.expand_dims(image_array, axis=0)
            logger.debug(f"Final preprocessed image_array shape (with batch dim): {image_array.shape}")
            
            return image_array, face_landmarks_results
            
        except Exception as e:
            logger.error(f"Error in preprocess_image: {str(e)}")
            # On critical error during initial image processing, return None for image_array
            # This should ideally not happen if image_data is valid base64.
            return None, []
    
    def predict(self, image_data):
        """Run inference on the preprocessed image and include face detection results."""
        try:
            if not self.is_loaded:
                raise ValueError("Model not loaded")
            
            # Preprocess image and get face detection results
            preprocessed_image, face_landmarks_results = self.preprocess_image(image_data)
            
            if preprocessed_image is None:
                # This case should now only happen if initial image decoding fails.
                logger.error("Failed to preprocess image data for prediction.")
                return {
                    'success': False,
                    'error': 'Image data preprocessing failed',
                    'confidence_open_eye': 0,
                    'raw_predictions': [],
                    'model_used': os.path.basename(self.model_path) if self.model_path else None,
                    'face_landmarks_results': face_landmarks_results
                }

            logger.debug(f"Shape of preprocessed_image before model.predict: {preprocessed_image.shape}") # Debug log here
            # Run inference
            predictions = self.model.predict(preprocessed_image, verbose=0)
            
            # Process predictions based on your model's output format
            # Assuming binary classification: [closed_prob, open_prob]. Index 1 is 'Open-Eyes'
            confidence_open_eye = float(predictions[0][1]) * 100 
            
            # Ensure confidence is in valid range
            confidence_open_eye = max(0, min(100, confidence_open_eye))
            
            return {
                'success': True,
                'confidence_open_eye': confidence_open_eye,
                'raw_predictions': predictions.tolist(),
                'model_used': os.path.basename(self.model_path) if self.model_path else None,
                'face_landmarks_results': face_landmarks_results # Pass through face detection results
            }
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'confidence_open_eye': 0,
                'raw_predictions': [],
                'model_used': os.path.basename(self.model_path) if self.model_path else None,
                'face_landmarks_results': [] # Empty list on error
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
        
        # Run prediction, which now also handles face detection and preprocessing
        drowsiness_prediction_result = detector.predict(image_data)
        
        # Determine if face detection was successful for this frame
        face_cropped_successfully = bool(drowsiness_prediction_result.get('face_landmarks_results'))

        # Get confidence for "Open-Eyes"
        confidence_open_eye = drowsiness_prediction_result['confidence_open_eye']
        logger.info(f"Drowsiness model confidence (Open Eye): {confidence_open_eye:.2f}%") # Debug log
        
        # --- Analyze Drowsiness and Blinks using DrowsinessAnalyzer ---
        metrics = {}
        alertness_level = 'Unknown'
        if detector.drowsiness_analyzer and DROWSINESS_ANALYZER_AVAILABLE:
            metrics = detector.drowsiness_analyzer.analyze_frame(confidence_open_eye)
            alertness_level = detector.drowsiness_analyzer.get_alertness_level(confidence_open_eye)
        else:
            logger.warning("DrowsinessAnalyzer not available. Using basic metrics and alertness.")
            # Fallback for metrics if analyzer is not available
            metrics = {
                'eyeClosure': 'Normal' if confidence_open_eye > 50 else 'Detected',
                'blinkRate': 0, # Cannot calculate without analyzer
                'headPosition': 'Upright' if confidence_open_eye > 70 else 'Tilting',
                'yawnCount': np.random.randint(0, 3) + (3 if confidence_open_eye < 40 else 0),
                'eyeAspectRatio': (confidence_open_eye / 100) * 0.3 + 0.2,
                'mouthAspectRatio': (confidence_open_eye / 100) * 0.2 + 0.1,
                'pupilDiameter': (confidence_open_eye / 100) * 2 + 3,
                'eyeMovement': 'Active' if confidence_open_eye > 60 else 'Reduced'
            }
            # Fallback to simple function if analyzer is not available
            if confidence_open_eye >= 80:
                alertness_level = 'Very Alert'
            elif confidence_open_eye >= 60:
                alertness_level = 'Alert'
            elif confidence_open_eye >= 40:
                alertness_level = 'Slightly Drowsy'
            elif confidence_open_eye >= 20:
                alertness_level = 'Drowsy'
            else:
                alertness_level = 'Very Drowsy'

        # Adjust alertness level if face cropping failed
        if not face_cropped_successfully:
            alertness_level = "No Face Cropped (Analysis on Full Image)"
            metrics['eyeClosure'] = "Unknown (No Face Cropped)"
            # Keep other metrics as they are, based on the full image prediction
            # Note: Blink rate and drowsiness score might be less accurate without a cropped face.

        response = {
            'success': drowsiness_prediction_result['success'], # True if image processed, False on critical error
            'confidence': confidence_open_eye,
            'alertness': alertness_level,
            'metrics': metrics,
            'model_used': drowsiness_prediction_result['model_used'],
            'face_detection_used': detector.face_detector.is_face_detection_available() if detector.face_detector else False,
            'drowsiness_analyzer_used': DROWSINESS_ANALYZER_AVAILABLE,
            'inference_time': np.random.uniform(20, 70),  # Simulated inference time
            'timestamp': str(np.datetime64('now')),
            'face_detection_landmarks': drowsiness_prediction_result.get('face_landmarks_results', []) # Get landmarks from prediction result
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in drowsiness detection endpoint: {str(e)}")
        return jsonify({
            'error': 'Detection failed',
            'details': str(e)
        }), 500

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
