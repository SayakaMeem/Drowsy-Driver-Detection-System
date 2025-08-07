class DrowsinessAnalyzer:
    def __init__(self,
                 open_eye_threshold=0.5,
                 blink_min_closed_duration_sec=0.08,
                 blink_max_closed_duration_sec=0.4,
                 blink_refractory_period_sec=0.2,
                 blink_rate_window_sec=60,
                 drowsiness_increment_per_closed_sec=5,
                 drowsiness_decrement_per_open_sec=1,
                 max_drowsiness_score=100):
        self.open_eye_threshold = open_eye_threshold
        self.blink_min_closed_duration_sec = blink_min_closed_duration_sec
        self.blink_max_closed_duration_sec = blink_max_closed_duration_sec
        self.blink_refractory_period_sec = blink_refractory_period_sec
        self.blink_rate_window_sec = blink_rate_window_sec
        self.drowsiness_increment_per_closed_sec = drowsiness_increment_per_closed_sec
        self.drowsiness_decrement_per_open_sec = drowsiness_decrement_per_open_sec
        self.max_drowsiness_score = max_drowsiness_score
        self.drowsiness_score = 0
        self.last_blink_time = None
        self.blink_count = 0
        self.last_eye_state = True  # True=open, False=closed

    def analyze_frame(self, confidence_open_eye):
        # Simple logic: if confidence below threshold, increment drowsiness
        if confidence_open_eye < self.open_eye_threshold * 100:
            self.drowsiness_score = min(self.max_drowsiness_score, self.drowsiness_score + self.drowsiness_increment_per_closed_sec)
            eye_closure = 'Detected'
        else:
            self.drowsiness_score = max(0, self.drowsiness_score - self.drowsiness_decrement_per_open_sec)
            eye_closure = 'Normal'
        # Simulate blink rate and other metrics
        metrics = {
            'eyeClosure': eye_closure,
            'blinkRate': self.blink_count,  # Not actually tracked in this simple version
            'drowsinessScore': self.drowsiness_score,
            'headPosition': 'Upright',
            'yawnCount': 0,
            'eyeAspectRatio': 0.3 if confidence_open_eye > 50 else 0.2,
            'mouthAspectRatio': 0.2,
            'pupilDiameter': 4.0,
            'eyeMovement': 'Active' if confidence_open_eye > 60 else 'Reduced'
        }
        return metrics

    def get_alertness_level(self, confidence_open_eye):
        if confidence_open_eye >= 80:
            return 'Very Alert'
        elif confidence_open_eye >= 60:
            return 'Alert'
        elif confidence_open_eye >= 40:
            return 'Slightly Drowsy'
        elif confidence_open_eye >= 20:
            return 'Drowsy'
        else:
            return 'Very Drowsy'
