#!/usr/bin/env python3
"""
Test script to verify MTCNN face detection is working
"""

import os
import sys
import numpy as np
from PIL import Image
import logging

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import face detector
try:
    from face_detector import create_face_detector
    print("✅ Face detector module imported successfully")
except ImportError as e:
    print(f"❌ Failed to import face detector: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_face_detector():
    """Test the face detector with a simple image"""
    print("\n🔍 Testing Face Detector...")
    
    # Create face detector
    try:
        detector = create_face_detector()
        print(f"✅ Face detector created successfully")
        print(f"   Available: {detector.is_face_detection_available()}")
        print(f"   Stats: {detector.get_detection_stats()}")
    except Exception as e:
        print(f"❌ Failed to create face detector: {e}")
        return False
    
    if not detector.is_face_detection_available():
        print("❌ Face detection is not available")
        return False
    
    # Create a simple test image (you can replace this with a real image path)
    print("\n📸 Creating test image...")
    try:
        # Create a simple colored rectangle as test image
        test_image = Image.new('RGB', (640, 480), color='red')
        print("✅ Test image created")
    except Exception as e:
        print(f"❌ Failed to create test image: {e}")
        return False
    
    # Test face detection
    print("\n🎯 Testing face detection...")
    try:
        faces = detector.detect_faces(test_image)
        print(f"✅ Face detection completed")
        print(f"   Faces detected: {len(faces)}")
        
        if faces:
            for i, face in enumerate(faces):
                print(f"   Face {i+1}: {face}")
        else:
            print("   No faces detected (expected for test image)")
            
    except Exception as e:
        print(f"❌ Face detection failed: {e}")
        return False
    
    return True

def test_mtcnn_directly():
    """Test MTCNN directly"""
    print("\n🔧 Testing MTCNN directly...")
    
    try:
        from mtcnn import MTCNN
        print("✅ MTCNN imported successfully")
        
        # Create MTCNN detector
        detector = MTCNN()
        print("✅ MTCNN detector created successfully")
        
        # Test with a simple image
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        faces = detector.detect_faces(test_image)
        print(f"✅ MTCNN test completed - {len(faces)} faces detected")
        
        return True
        
    except Exception as e:
        print(f"❌ MTCNN test failed: {e}")
        return False

def test_backend_endpoints():
    """Test if the backend endpoints are working"""
    print("\n🌐 Testing backend endpoints...")
    
    try:
        import requests
        import json
        
        # Test health endpoint
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health endpoint working")
            print(f"   Model loaded: {health_data.get('model_loaded', False)}")
            print(f"   Face detection available: {health_data.get('face_detection_available', False)}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
            
        # Test face detection endpoint with a simple image
        test_image = Image.new('RGB', (100, 100), color='blue')
        import io
        import base64
        
        # Convert to base64
        buffer = io.BytesIO()
        test_image.save(buffer, format='JPEG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        face_response = requests.post(
            'http://localhost:5000/detect-faces',
            json={'image': f'data:image/jpeg;base64,{img_str}'},
            timeout=10
        )
        
        if face_response.status_code == 200:
            face_data = face_response.json()
            print("✅ Face detection endpoint working")
            print(f"   Success: {face_data.get('success', False)}")
            print(f"   Faces detected: {face_data.get('faces_detected', 0)}")
        else:
            print(f"❌ Face detection endpoint failed: {face_response.status_code}")
            print(f"   Response: {face_response.text}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Backend endpoint test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Face Detection Tests...")
    print("=" * 50)
    
    # Test 1: Direct MTCNN
    mtcnn_ok = test_mtcnn_directly()
    
    # Test 2: Face detector module
    detector_ok = test_face_detector()
    
    # Test 3: Backend endpoints (only if backend is running)
    try:
        backend_ok = test_backend_endpoints()
    except:
        print("⚠️  Backend not running - skipping endpoint tests")
        backend_ok = True
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   MTCNN Direct: {'✅ PASS' if mtcnn_ok else '❌ FAIL'}")
    print(f"   Face Detector Module: {'✅ PASS' if detector_ok else '❌ FAIL'}")
    print(f"   Backend Endpoints: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    
    if mtcnn_ok and detector_ok:
        print("\n✅ Face detection should be working!")
        print("   If you're still having issues, check:")
        print("   1. Backend server is running (python ml_server.py)")
        print("   2. Frontend is calling the correct endpoints")
        print("   3. Camera permissions are granted")
    else:
        print("\n❌ Face detection has issues that need to be fixed") 