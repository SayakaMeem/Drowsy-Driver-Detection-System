# 🤖 ML Model Integration Guide

This guide shows exactly how your trained `.keras` models are integrated into the drowsiness detection system.

## 📁 **Model Files Location**

Your trained models are located in the project root:
```
System_Project/
├── drowsiness_model_final.keras      # 18MB - Final trained model
├── drowsiness_model_improved.keras   # 58MB - Improved version
├── drowsiness_model_finetuned.keras  # 140MB - Fine-tuned version
├── drowsiness_model.keras            # 86MB - Base model
└── drowsiness_model.h5               # 86MB - H5 format
```

## 🔧 **Integration Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Next.js API    │    │  Python ML      │
│   (React)       │───▶│   (Fallback)     │───▶│   Backend       │
│                 │    │                  │    │   (Flask)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
   Camera Feed           Simulation Mode         Real ML Inference
   Real-time UI          (No backend)            (Your .keras models)
```

## 🚀 **How to Run with Real ML Models**

### **Step 1: Install Python Dependencies**
```bash
cd my-project
pip install -r backend/requirements.txt
```

### **Step 2: Start the Python ML Backend**
```bash
# Option 1: Use the startup script
python start_backend.py

# Option 2: Direct execution
python backend/ml_server.py
```

### **Step 3: Start the Frontend**
```bash
npm run dev
```

## 🔍 **Integration Details**

### **1. Model Loading Process**
```python
# backend/ml_server.py - Lines 25-50
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
        return True
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False
```

### **2. Image Preprocessing**
```python
# backend/ml_server.py - Lines 52-85
def preprocess_image(self, image_data):
    """Preprocess image for model inference"""
    try:
        # Decode base64 image
        if isinstance(image_data, str):
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to model input shape
        image = image.resize((self.input_shape[0], self.input_shape[1]))
        
        # Convert to numpy array and normalize
        image_array = np.array(image)
        image_array = image_array.astype('float32') / 255.0
        
        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array
        
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        raise
```

### **3. Real ML Inference**
```python
# backend/ml_server.py - Lines 87-115
def predict(self, image_data):
    """Run inference on the preprocessed image"""
    try:
        if not self.is_loaded:
            raise ValueError("Model not loaded")
        
        # Preprocess image
        preprocessed_image = self.preprocess_image(image_data)
        
        # Run inference
        predictions = self.model.predict(preprocessed_image, verbose=0)
        
        # Process predictions based on your model's output format
        if len(predictions.shape) == 2:
            # Binary classification (drowsy/not drowsy)
            confidence = float(predictions[0][0]) * 100
        else:
            # Multi-class classification
            confidence = float(np.max(predictions[0])) * 100
        
        # Ensure confidence is in valid range
        confidence = max(0, min(100, confidence))
        
        return {
            'confidence': confidence,
            'raw_predictions': predictions.tolist(),
            'model_used': os.path.basename(self.model_path)
        }
        
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        raise
```

### **4. Frontend Integration**
```javascript
// src/app/services/mlService.js - Lines 60-95
async callBackendAPI(imageData) {
    // Convert image data to base64
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = imageData.width;
    canvas.height = imageData.height;
    ctx.putImageData(imageData, 0, 0);
    
    const base64Image = canvas.toDataURL('image/jpeg', 0.8);
    
    // Try Python backend first
    try {
        const pythonResponse = await fetch(`${this.pythonBackendUrl}/detect-drowsiness`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image: base64Image,
                timestamp: Date.now()
            })
        });

        if (pythonResponse.ok) {
            const result = await pythonResponse.json();
            return {
                confidence: result.confidence,
                alertness: result.alertness,
                metrics: result.metrics || {}
            };
        }
    } catch (pythonError) {
        console.warn('Python backend failed, trying Next.js API:', pythonError.message);
    }
    
    // Fallback to Next.js API
    const response = await fetch(this.modelEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image: base64Image,
            timestamp: Date.now()
        })
    });

    if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
    }

    const result = await response.json();
    return {
        confidence: result.confidence,
        alertness: this.getAlertnessLevel(result.confidence),
        metrics: result.metrics || {}
    };
}
```

## 🔄 **API Endpoints**

### **Python Backend (Port 5000)**
- `GET /health` - Health check and model status
- `POST /detect-drowsiness` - Main detection endpoint
- `GET /models` - List available models
- `POST /load-model` - Load a specific model

### **Next.js API (Port 3000)**
- `GET /api/health` - Health check
- `POST /api/detect-drowsiness` - Fallback detection endpoint

## 📊 **Data Flow**

1. **Camera Capture**: Video frame captured from webcam
2. **Image Processing**: Frame converted to base64 and sent to backend
3. **ML Inference**: Python backend loads your `.keras` model and runs inference
4. **Results**: Confidence score and metrics returned to frontend
5. **UI Update**: Real-time display of drowsiness detection results

## 🛠 **Customization Options**

### **Change Model Input Shape**
```python
# backend/ml_server.py - Line 20
self.input_shape = (224, 224, 3)  # Adjust based on your model
```

### **Use Different Model**
```python
# backend/ml_server.py - Lines 200-205
default_model_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
    'drowsiness_model_improved.keras'  # Change model name here
)
```

### **Adjust Confidence Thresholds**
```python
# backend/ml_server.py - Lines 180-190
def get_alertness_level(confidence):
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
```

## 🔍 **Troubleshooting**

### **Model Not Loading**
- Check if model file exists in project root
- Verify TensorFlow version compatibility
- Check console logs for specific errors

### **Backend Connection Issues**
- Ensure Python backend is running on port 5000
- Check CORS settings if needed
- Verify all dependencies are installed

### **Performance Issues**
- Adjust inference frequency in `mlService.js`
- Consider model optimization techniques
- Monitor memory usage with large models

## 🎯 **Next Steps**

1. **Start the backend**: `python start_backend.py`
2. **Start the frontend**: `npm run dev`
3. **Test with camera**: Allow camera permissions and click "Start Detecting"
4. **Monitor logs**: Check console for real ML inference results
5. **Customize**: Adjust thresholds and metrics as needed

Your trained models are now fully integrated and ready for real-time drowsiness detection! 🚀 