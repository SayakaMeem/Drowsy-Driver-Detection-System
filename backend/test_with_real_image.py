#!/usr/bin/env python3
"""
Test face detection with a real image
"""

import os
import sys
import numpy as np
from PIL import Image
import logging
import requests
from io import BytesIO

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import face detector
from face_detector import FaceDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_test_image():
    """Download a test image with faces"""
    try:
        # Download a sample image with faces (you can replace this URL)
        url = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=300&fit=crop"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            print(f"✅ Downloaded test image: {image.size}")
            return image
        else:
            print(f"❌ Failed to download image: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error downloading image: {e}")
        return None

def test_face_detection_with_real_image():
    """Test face detection with a real image"""
    print("\n🔍 Testing Face Detection with Real Image...")
    
    # Create face detector
    detector = FaceDetector()
    if not detector.is_face_detection_available():
        print("❌ Face detection not available")
        return False
    
    # Get test image
    test_image = download_test_image()
    if test_image is None:
        print("❌ Could not get test image")
        return False
    
    # Test face detection
    try:
        faces = detector.detect_faces(test_image)
        print(f"✅ Face detection completed")
        print(f"   Faces detected: {len(faces)}")
        
        if faces:
            for i, face in enumerate(faces):
                bbox = face['box']
                confidence = face.get('confidence', 0)
                print(f"   Face {i+1}: bbox={bbox}, confidence={confidence:.2f}")
                
                # Test cropping
                face_image, bbox_coords = detector.crop_face(test_image, face)
                if face_image:
                    print(f"   Face {i+1} cropped successfully: {bbox_coords}")
                else:
                    print(f"   Face {i+1} cropping failed")
        else:
            print("   No faces detected in the test image")
            
    except Exception as e:
        print(f"❌ Face detection failed: {e}")
        return False
    
    return True

def test_backend_with_real_image():
    """Test backend face detection with a real image"""
    print("\n🌐 Testing Backend with Real Image...")
    
    # Get test image
    test_image = download_test_image()
    if test_image is None:
        print("❌ Could not get test image")
        return False
    
    try:
        import base64
        import io
        
        # Convert to base64
        buffer = io.BytesIO()
        test_image.save(buffer, format='JPEG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        # Test face detection endpoint
        response = requests.post(
            'http://localhost:5000/detect-faces',
            json={'image': f'data:image/jpeg;base64,{img_str}'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Backend face detection completed")
            print(f"   Success: {result.get('success', False)}")
            print(f"   Faces detected: {result.get('faces_detected', 0)}")
            
            if result.get('faces') and len(result['faces']) > 0:
                for i, face in enumerate(result['faces']):
                    bbox = face.get('bbox', [])
                    confidence = face.get('confidence', 0)
                    print(f"   Face {i+1}: bbox={bbox}, confidence={confidence:.2f}")
            else:
                print("   No faces detected by backend")
                
            return True
        else:
            print(f"❌ Backend request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Face Detection with Real Image...")
    print("=" * 60)
    
    # Test 1: Direct face detection
    direct_ok = test_face_detection_with_real_image()
    
    # Test 2: Backend face detection
    backend_ok = test_backend_with_real_image()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   Direct Face Detection: {'✅ PASS' if direct_ok else '❌ FAIL'}")
    print(f"   Backend Face Detection: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    
    if direct_ok and backend_ok:
        print("\n✅ Face detection is working properly!")
        print("   The issue might be in the frontend integration.")
    else:
        print("\n❌ Face detection still has issues") 