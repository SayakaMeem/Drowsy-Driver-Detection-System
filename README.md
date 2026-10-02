# 🚗 Drowsy Driver Detection System

> An AI-powered real-time safety system that detects driver drowsiness using Computer Vision & Deep Learning and alerts instantly to prevent accidents.

![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat&logo=next.js)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat&logo=python)
![TensorFlow](https://img.shields.io/badge/TensorFlow-CNN-FF6F00?style=flat&logo=tensorflow)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-5C3EE8?style=flat&logo=opencv)

**Live Demo:** [Add your Vercel link here]
**GitHub:** https://github.com/SayakaMeem/Drowsy-Driver-Detection-System

---

### ✨ Features

- 👁️ **Real-time Eye Tracking** — Detects Eye Aspect Ratio (EAR) via webcam
- 🧠 **CNN Model (.h5)** — Deep learning model trained for open/closed eye classification
- 🚨 **Instant Alerts** — Audio alarm + visual warning when drowsiness detected
- 📊 **Smart Dashboard** — Next.js 14 dashboard with live camera feed
- 🕘 **Session History** — SQLite DB (`drowsiness_data.db`) logs all events with timestamps
- 📈 **Analytics** — Drowsiness frequency, duration, alert stats
- 📱 **Responsive UI** — Tailwind CSS, works on desktop & mobile
- 🔌 **Full-Stack** — Python FastAPI/Flask backend + Next.js frontend

### 🧠 How It Works
Webcam Feed → Face Detection (OpenCV / MediaPipe)
→ Eye Region Extraction
→ EAR Calculation: EAR = (|p2-p6| + |p3-p5|) / (2*|p1-p4|)
→ CNN Model Prediction (.h5) → Open/Closed

1.  **Face & Eye Detection:** Uses Haar Cascades / Dlib 68 landmarks
2.  **CNN Classification:** Custom trained model `drowsiness_new.h5`
3.  **Logic:** PERCLOS + consecutive frame count to avoid false positives
4.  **Alert System:** Buzzer sound + dashboard alert

### 🛠️ Tech Stack

**Frontend:**
- Next.js 14 (App Router)
- Tailwind CSS
- JavaScript / TypeScript
- Webcam API

**Backend:**
- Python 3.9+
- FastAPI / Flask
- OpenCV, Dlib, TensorFlow / Keras
- SQLite (`drowsiness_data.db`)

**ML:**
- CNN for eye state classification
- Trained on MRL Eye + DDD Dataset
- Model files: `.h5` (stored in `backend/app/models/`)

### 📁 Project Structure
Drowsy-Driver-Detection-System/
├── backend/
│ ├── app/
│ │ ├── models/ # .h5 model files (download separately)
│ │ ├── routes/ # API endpoints
│ │ └── main.py # FastAPI entry
│ └── requirements.txt
├── src/app/ # Next.js 14 frontend
│ ├── components/ # Dashboard, Camera, Alerts
│ ├── dashboard/
│ └── page.js
├── public/
├── DASHBOARD_README.md
├── ML_INTEGRATION_GUIDE.md
├── drowsiness_data.db # SQLite history
├── start_backend.py # One-click backend starter
└── package.json

### 🚀 Quick Start

#### 1. Clone Repo

git clone https://github.com/SayakaMeem/Drowsy-Driver-Detection-System.git
cd Drowsy-Driver-Detection-System


### 🚀 Quick Start

#### 1. Clone Repo

git clone https://github.com/SayakaMeem/Drowsy-Driver-Detection-System.git
cd Drowsy-Driver-Detection-System

2. Backend Setup (Python)
   # Create virtual env
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r backend/requirements.txt
# or
pip install opencv-python tensorflow numpy fastapi uvicorn dlib

# Download model files
# Place .h5 files in backend/app/models/
# Link: [Add your Google Drive link]

# Run backend
python start_backend.py
# or
uvicorn backend.app.main:app --reload --port 8000

3. Frontend Setup (Next.js)
npm install
npm run dev
# Open http://localhost:3000

📦 Models
The trained model files (.h5) are not included due to size limits.

Download from: [Add your Google Drive / HuggingFace link]
Place them in: backend/app/models/

Expected files:

drowsiness_model.h5
eye_state_classifier.h5

🔮 Future Improvements
 Yawning detection via mouth aspect ratio (MAR)
 Head pose estimation for distraction detection
 Mobile app (React Native)
 Cloud sync + driver profile
 SMS alert to emergency contact (Twilio integration)
👩‍💻 Author
Sayaka Meem
GitHub: @SayakaMeem
→ If EAR < Threshold for > N frames → DROWSY
→ Trigger Alarm + Log to DB + Update Dashboard
