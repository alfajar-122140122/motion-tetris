import cv2
import mediapipe as mp
import numpy as np
from config import CLAP_THRESHOLD

# Initialize MediaPipe Hand detection globally
mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands( # Renamed for clarity
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.3
)

def detect_hand_gesture(frame):
    """Detect hand gestures using MediaPipe and map to Tetris controls."""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands_detector.process(rgb_frame) # Use renamed detector
    gesture = "none"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp.solutions.drawing_utils.DrawingSpec(color=(255, 0, 0), thickness=2)
            )

        if len(results.multi_hand_landmarks) == 2:
            # Check for clap only if two hands are detected
            if detect_clap(results.multi_hand_landmarks[0], results.multi_hand_landmarks[1], frame.shape):
                gesture = "rotate"
        elif len(results.multi_hand_landmarks) == 1: # Process single hand gestures only if one hand is present
            hand_landmarks = results.multi_hand_landmarks[0]
            if results.multi_handedness and results.multi_handedness[0].classification:
                hand_label = results.multi_handedness[0].classification[0].label
                gesture = detect_single_hand_gestures(hand_landmarks, frame.shape, hand_label)
            # else: gesture remains "none" if handedness info is missing

    visualize_gesture(frame, gesture) # visualize_gesture is called once after processing all hands
    return frame, gesture

def detect_clap(hand1_landmarks, hand2_landmarks, frame_shape):
    """Detect if two hands are close enough to be considered a clap."""
    height, width = frame_shape[:2]
    hand1_palm_x = hand1_landmarks.landmark[9].x * width
    hand1_palm_y = hand1_landmarks.landmark[9].y * height
    hand2_palm_x = hand2_landmarks.landmark[9].x * width
    hand2_palm_y = hand2_landmarks.landmark[9].y * height

    palm_distance = np.sqrt((hand1_palm_x - hand2_palm_x)**2 +
                          (hand1_palm_y - hand2_palm_y)**2)

    return palm_distance < CLAP_THRESHOLD

def detect_single_hand_gestures(landmarks, frame_shape, hand_label):
    """
    Detect single hand gestures (raised left/right hand) and map them to Tetris controls.
    Returns: action (str): 'left', 'right', 'hardDrop', or 'none'
    """
    if not landmarks:
        return "none"

    wrist_y = landmarks.landmark[0].y
    index_tip_y = landmarks.landmark[8].y
    middle_tip_y = landmarks.landmark[12].y
    ring_tip_y = landmarks.landmark[16].y
    pinky_tip_y = landmarks.landmark[20].y
    
    # Get finger MCP (knuckle) positions for fist detection
    index_mcp_y = landmarks.landmark[5].y
    middle_mcp_y = landmarks.landmark[9].y
    ring_mcp_y = landmarks.landmark[13].y
    pinky_mcp_y = landmarks.landmark[17].y
    
    # Fingertips height average
    avg_fingers_height = (index_tip_y + middle_tip_y + ring_tip_y + pinky_tip_y) / 4
    raised_hand = avg_fingers_height < wrist_y - 0.15
    
    # Detect fist: when fingertips are below knuckles (fingers curled)
    fist_detected = (index_tip_y > index_mcp_y and 
                    middle_tip_y > middle_mcp_y and 
                    ring_tip_y > ring_mcp_y and 
                    pinky_tip_y > pinky_mcp_y)
    
    if fist_detected:
        return "hardDrop"
    elif raised_hand:
        if hand_label == "Right":
            return "right"
        else:
            return "left"
    return "none"

def visualize_gesture(frame, gesture):
    """Add visual indication of the detected gesture to the frame."""
    gesture_text = f"Gesture: {gesture.capitalize()}" # Capitalize for better display
    cv2.putText(frame, gesture_text, (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    if gesture == "left":
        cv2.arrowedLine(frame, (100, 120), (50, 120), (0, 0, 255), 5)
        cv2.putText(frame, "Tangan Kiri", (50, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    elif gesture == "right":
        cv2.arrowedLine(frame, (100, 120), (150, 120), (0, 0, 255), 5)
        cv2.putText(frame, "Tangan Kanan", (50, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    elif gesture == "rotate":
        cv2.circle(frame, (100, 120), 25, (0, 0, 255), -1)
        cv2.putText(frame, "Tepuk Tangan", (50, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    elif gesture == "hardDrop":
        cv2.arrowedLine(frame, (100, 100), (100, 150), (0, 0, 255), 5)
        cv2.putText(frame, "Genggam Tangan", (50, 170),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
