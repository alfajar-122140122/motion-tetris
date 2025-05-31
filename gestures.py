"""
Motion Tetris - Hand Gesture Detection Module
============================================
This module handles hand gesture detection for the Motion Tetris game using MediaPipe.

Key Gestures:
1. LEFT/RIGHT HAND RAISED - Move piece left/right
2. PINCH - Rotate piece  
3. FIST - Drop piece quickly

Each gesture is carefully designed to avoid interference and includes cooldown periods.
"""

import cv2
import mediapipe as mp
from config import (
    FIST_THRESHOLD, PINCH_THRESHOLD, HAND_WIDTH_MIN,
    PINCH_DISTANCE_THRESHOLD, RAISED_HAND_HEIGHT
)

# Initialize MediaPipe hands detector
mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2, 
    min_detection_confidence=0.5,
    min_tracking_confidence=0.3
)

# MediaPipe hand landmark indices
WRIST = 0
THUMB_TIP = 4
THUMB_IP = 3
THUMB_MCP = 2
INDEX_TIP = 8
INDEX_MCP = 5
MIDDLE_TIP = 12
MIDDLE_PIP = 10
MIDDLE_MCP = 9
RING_TIP = 16
RING_PIP = 14
RING_MCP = 13
PINKY_TIP = 20
PINKY_PIP = 18
PINKY_MCP = 17

def detect_pinch_gesture(landmarks):
    """Detect pinch gesture (thumb and index together) for rotation."""
    if not landmarks:
        return False

    # Get landmarks
    thumb_tip = landmarks.landmark[THUMB_TIP]
    index_tip = landmarks.landmark[INDEX_TIP]
    middle_tip = landmarks.landmark[MIDDLE_TIP] 
    ring_tip = landmarks.landmark[RING_TIP]
    pinky_tip = landmarks.landmark[PINKY_TIP]
    wrist = landmarks.landmark[WRIST]
    middle_pip = landmarks.landmark[MIDDLE_PIP]
    ring_pip = landmarks.landmark[RING_PIP]
    pinky_pip = landmarks.landmark[PINKY_PIP]

    # Validate pinch gesture
    pinch_distance = ((thumb_tip.x - index_tip.x) ** 2 + 
                     (thumb_tip.y - index_tip.y) ** 2) ** 0.5
    
    # Quick fail conditions
    if (pinch_distance > PINCH_DISTANCE_THRESHOLD or  # Thumb and index too far
        abs(thumb_tip.y - index_tip.y) > 0.15 or     # Height mismatch
        middle_tip.y > middle_pip.y or               # Other fingers not extended
        ring_tip.y > ring_pip.y or
        pinky_tip.y > pinky_pip.y or
        thumb_tip.y > wrist.y or                     # Hand not raised
        index_tip.y > wrist.y):
        return False

    return True

def detect_fist_gesture(landmarks): 
    """Detect fist gesture (all fingers curled) for hard drop."""
    if not landmarks:
        return False

    # Get landmarks
    thumb_tip = landmarks.landmark[THUMB_TIP]
    index_tip = landmarks.landmark[INDEX_TIP]
    middle_tip = landmarks.landmark[MIDDLE_TIP]
    ring_tip = landmarks.landmark[RING_TIP]
    pinky_tip = landmarks.landmark[PINKY_TIP]
    
    index_mcp = landmarks.landmark[INDEX_MCP]
    middle_mcp = landmarks.landmark[MIDDLE_MCP] 
    ring_mcp = landmarks.landmark[RING_MCP]
    pinky_mcp = landmarks.landmark[PINKY_MCP]
    thumb_ip = landmarks.landmark[THUMB_IP]

    # Check all fingers are curled
    return (
        index_tip.y > index_mcp.y and      # Main fingers below MCP joints
        middle_tip.y > middle_mcp.y and
        ring_tip.y > ring_mcp.y and
        pinky_tip.y > pinky_mcp.y and
        thumb_tip.y > thumb_ip.y           # Thumb curled
    )

def detect_raised_hand(landmarks, hand_label):
    """Detect raised hand gesture (left/right) for movement."""
    if not landmarks:
        return "none"

    # Get landmarks
    wrist = landmarks.landmark[WRIST]
    index_tip = landmarks.landmark[INDEX_TIP]
    middle_tip = landmarks.landmark[MIDDLE_TIP]
    ring_tip = landmarks.landmark[RING_TIP]
    pinky_tip = landmarks.landmark[PINKY_TIP]

    # Average finger height relative to wrist
    avg_fingers_height = (
        index_tip.y + middle_tip.y + 
        ring_tip.y + pinky_tip.y
    ) / 4
    
    if avg_fingers_height < (wrist.y - RAISED_HAND_HEIGHT):
        return "right" if hand_label == "Right" else "left"
    return "none"

def detect_hand_gesture(frame):
    """
    Detect hand gestures and map to Tetris controls.
    Priority: hard drop > pinch > movement
    
    Returns:
        tuple: (processed_frame, gesture_name)
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands_detector.process(rgb_frame)
    gesture = "none"

    if results.multi_hand_landmarks:
        # Draw hand landmarks
        for hand_landmarks in results.multi_hand_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
            )

        # First check for hard drop (highest priority)
        for hand_landmarks in results.multi_hand_landmarks:
            if detect_fist_gesture(hand_landmarks):
                gesture = "hardDrop"
                break

        # Then check for pinch if no hard drop
        if gesture == "none":
            for hand_landmarks in results.multi_hand_landmarks:
                if detect_pinch_gesture(hand_landmarks):
                    gesture = "rotate"
                    break

        # Finally check for movement if no other gesture
        if gesture == "none":
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                if i < len(results.multi_handedness):
                    hand_label = results.multi_handedness[i].classification[0].label
                    movement = detect_raised_hand(hand_landmarks, hand_label)
                    if movement != "none":
                        gesture = movement
                        break

    # Add gesture visualization
    visualize_gesture(frame, gesture)
    return frame, gesture

def visualize_gesture(frame, gesture):
    """Add visual indication of detected gesture."""
    # Font settings
    font = cv2.FONT_HERSHEY_SIMPLEX
    white = (255, 255, 255)
    
    # Control instructions
    instructions = [
        ("Controls:", 0.5, -85),
        ("- Angkat Tangan: Gerak Kiri/Kanan", 0.4, -65),
        ("- Pinch: Rotasi", 0.4, -45),
        ("- Genggam: Hard Drop", 0.4, -25)
    ]

    # Draw instructions at bottom of frame
    for text, scale, y_offset in instructions:
        cv2.putText(frame, text,
                   (10, frame.shape[0] + y_offset),
                   font, scale, white, 1)
