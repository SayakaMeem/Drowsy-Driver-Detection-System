# Drowsiness Detection Backend

## Structure

```
backend/
  app/
    __init__.py
    ml_server.py         # Main Flask app (API server)
    face_detector.py     # MTCNN-based face detection logic
    models/              # All .h5 model files
    utils/
      __init__.py
  tests/
    test_face_detection.py
    test_with_real_image.py
  requirements.txt
  run_server.py          # Unified run script (Python)
  setup.bat              # Windows setup script
  manual_setup.bat       # Alternate Windows setup script
  README.md
```

## Setup

### 1. Install dependencies and create virtual environment

#### Windows
Run in the `backend/` directory:
```
setup.bat
```
Or, for manual steps:
```
manual_setup.bat
```

#### Linux/Mac
Run in the `backend/` directory:
```
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Server

After setup, start the backend server:

```
python run_server.py
```

The server will be available at http://localhost:5000

## Main Endpoints
- `/health` — Health check
- `/load-model` — Load a model (POST)
- `/detect-drowsiness` — Drowsiness detection (POST)
- `/detect-faces` — Face detection (POST)
- `/models` — List available models

## Testing

Test scripts are in `backend/tests/`:
- `test_face_detection.py`
- `test_with_real_image.py`

Run with:
```
python tests/test_face_detection.py
python tests/test_with_real_image.py
```

## Notes
- Only the MTCNN-based face detection is used for simplicity and reliability.
- All models are stored in `app/models/`.
- All utility code should go in `app/utils/`.
