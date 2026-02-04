"""
Video Analyzer Module
Analyzes facial expressions, emotions, and visual cues during interview
"""
import sys
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
import time
from collections import deque

# Trick MediaPipe into not looking for TensorFlow to avoid Protobuf crashes
sys.modules['tensorflow'] = None 
import mediapipe as mp

class VideoAnalyzer:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        
        # 1. Initialize MediaPipe Solutions
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        
        # 2. Initialize Detectors (Fixes the 'face_detection' attribute error)
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0, 
            min_detection_confidence=0.5
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # 3. Initialize History Trackers (Required for get_session_summary)
        self.emotion_history = deque(maxlen=100)
        self.eye_contact_history = deque(maxlen=100)
        self.posture_history = deque(maxlen=100)
        
        self.session_data = {
            'total_frames': 0,
            'face_detected_frames': 0
        }

    def start_camera(self) -> bool:
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                print("Error: Could not open camera")
                return False
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            return True
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False

    def stop_camera(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        cv2.destroyAllWindows()

    def capture_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        if self.cap is None or not self.cap.isOpened():
            return False, None
        return self.cap.read()

    def analyze_frame(self, frame: np.ndarray) -> Dict:
        analysis = {
            'face_detected': False,
            'emotion': 'neutral',
            'confidence': 0.0,
            'eye_contact': False,
            'head_pose': 'neutral',
            'facial_landmarks': None
        }

        if frame is None: return analysis

        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect face
        detection_results = self.face_detection.process(rgb_frame)
        
        if detection_results.detections:
            analysis['face_detected'] = True
            self.session_data['face_detected_frames'] += 1
            
            mesh_results = self.face_mesh.process(rgb_frame)
            
            if mesh_results.multi_face_landmarks:
                face_landmarks = mesh_results.multi_face_landmarks[0]
                analysis['facial_landmarks'] = face_landmarks
                
                # Analyze facial features
                emotion, confidence = self._analyze_emotion(face_landmarks, frame.shape)
                analysis['emotion'] = emotion
                analysis['confidence'] = confidence
                
                eye_contact = self._check_eye_contact(face_landmarks, frame.shape)
                analysis['eye_contact'] = eye_contact
                
                head_pose = self._analyze_head_pose(face_landmarks, frame.shape)
                analysis['head_pose'] = head_pose
                
                # Update history
                self.emotion_history.append(emotion)
                self.eye_contact_history.append(eye_contact)
                self.posture_history.append(head_pose)
        
        self.session_data['total_frames'] += 1
        return analysis

    def _analyze_emotion(self, landmarks, frame_shape) -> Tuple[str, float]:
        h, w = frame_shape[:2]
        mouth_top = landmarks.landmark[13]
        mouth_bottom = landmarks.landmark[14]
        left_eye_top = landmarks.landmark[159]
        left_eye_bottom = landmarks.landmark[145]
        
        mouth_open = abs(mouth_top.y - mouth_bottom.y) * h
        left_eye_open = abs(left_eye_top.y - left_eye_bottom.y) * h
        
        if mouth_open > 15: return 'happy', 0.75
        elif mouth_open > 8: return 'happy', 0.65
        elif left_eye_open < 5: return 'focused', 0.60
        else: return 'neutral', 0.80

    def _check_eye_contact(self, landmarks, frame_shape) -> bool:
        nose_tip = landmarks.landmark[1]
        left_eye = landmarks.landmark[33]
        right_eye = landmarks.landmark[263]
        eye_center_x = (left_eye.x + right_eye.x) / 2
        return abs(nose_tip.x - eye_center_x) < 0.03

    def _analyze_head_pose(self, landmarks, frame_shape) -> str:
        nose_tip = landmarks.landmark[1]
        chin = landmarks.landmark[152]
        forehead = landmarks.landmark[10]
        face_height = abs(forehead.y - chin.y)
        nose_position = (nose_tip.y - forehead.y) / face_height if face_height > 0 else 0.5
        
        if nose_position < 0.4: return 'looking_up'
        elif nose_position > 0.6: return 'looking_down'
        else: return 'centered'

    def get_session_summary(self) -> Dict:
        total = self.session_data['total_frames']
        face_rate = (self.session_data['face_detected_frames'] / total) if total > 0 else 0
        eye_pct = (sum(self.eye_contact_history) / len(self.eye_contact_history)) if self.eye_contact_history else 0
        
        return {
            'total_frames_analyzed': total,
            'face_detection_rate': face_rate * 100,
            'eye_contact_percentage': eye_pct * 100,
            'dominant_emotion': max(set(self.emotion_history), default='neutral') if self.emotion_history else 'neutral',
            'dominant_posture': max(set(self.posture_history), default='centered') if self.posture_history else 'centered',
            'engagement_score': self._calculate_engagement_score()
        }

    def _calculate_engagement_score(self) -> float:
        score = 50
        if self.eye_contact_history:
            score += (sum(self.eye_contact_history) / len(self.eye_contact_history)) * 25
        return min(100, max(0, score))

    def visualize_frame(self, frame: np.ndarray, analysis: Dict) -> np.ndarray:
        vis_frame = frame.copy()
        if analysis['face_detected'] and analysis['facial_landmarks']:
            self.mp_drawing.draw_landmarks(
                image=vis_frame,
                landmark_list=analysis['facial_landmarks'],
                connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
            )
        return vis_frame

# --- MAIN BLOCK FOR TESTING ---
if __name__ == "__main__":
    analyzer = VideoAnalyzer()
    if analyzer.start_camera():
        print("Camera started. Press 'q' to stop.")
        while True:
            ret, frame = analyzer.capture_frame()
            if not ret: break
            res = analyzer.analyze_frame(frame)
            cv2.imshow('Test', analyzer.visualize_frame(frame, res))
            if cv2.waitKey(1) & 0xFF == ord('q'): break
        analyzer.stop_camera()