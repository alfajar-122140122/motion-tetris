"""
Motion Tetris - Hand Gesture Detection Module
============================================
This module handles hand gesture detection using MediaPipe for controlling the Tetris game.
Supported gestures:
- Left/Right hand raised: Move piece left/right
- Pinch (thumb + index finger): Rotate piece
- Fist: Hard drop piece
"""

import cv2
import mediapipe as mp
import numpy as np
import time
from config import PINCH_THRESHOLD, ROTATION_RECOGNITION_DELAY, FIST_THRESHOLD

# =============================================================================
# MEDIAPIPE INITIALIZATION
# =============================================================================

# Initialize MediaPipe Hand detection globally
mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.3
)

# =============================================================================
# GLOBAL VARIABLES FOR GESTURE TRACKING
# =============================================================================

last_rotation_time = 0              # Track last rotation time for delay
rotation_gesture_active = False     # Track if rotation gesture is active

# =============================================================================
# MAIN GESTURE DETECTION FUNCTION
# =============================================================================

def detect_hand_gesture(frame):
    """
    Detect hand gestures using MediaPipe and map to Tetris controls.
    
    Args:
        frame (numpy.ndarray): Input video frame
        
    Returns:
        tuple: (processed_frame, gesture_name)
            - processed_frame: Frame with gesture visualization
            - gesture_name: Detected gesture ("left", "right", "rotate", "hardDrop", "none")
    """
    global last_rotation_time, rotation_gesture_active
    
    # Convert BGR to RGB for MediaPipe processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands_detector.process(rgb_frame)
    gesture = "none"
    current_time = time.time()

    if results.multi_hand_landmarks:
        # Draw hand landmarks on frame
        for hand_landmarks in results.multi_hand_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp.solutions.drawing_utils.DrawingSpec(color=(255, 0, 0), thickness=2)
            )
        
        # Process gestures from detected hands
        if len(results.multi_hand_landmarks) >= 1:
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                if results.multi_handedness and len(results.multi_handedness) > i:
                    hand_label = results.multi_handedness[i].classification[0].label
                    
                    # Draw debug information (only for first hand to avoid clutter)
                    if i == 0:
                        draw_debug_info(frame, hand_landmarks, hand_label)
                    
                    # Check for pinch gesture (thumb tip touches index finger tip)
                    if detect_pinch_gesture(hand_landmarks, frame.shape):
                        if not rotation_gesture_active and (current_time - last_rotation_time) > ROTATION_RECOGNITION_DELAY:
                            gesture = "rotate"
                            rotation_gesture_active = True
                            last_rotation_time = current_time
                            break  # Only process one rotation gesture at a time
                    else:
                        rotation_gesture_active = False
                        
                        # Only check other gestures if no pinch detected
                        single_hand_gesture = detect_single_hand_gestures(hand_landmarks, frame.shape, hand_label)
                        if single_hand_gesture != "none":
                            gesture = single_hand_gesture
                            break  # Process only first detected gesture

    visualize_gesture(frame, gesture)
    return frame, gesture

def detect_pinch_gesture(landmarks, frame_shape):
    """
    Detect pinch gesture (thumb tip touching index finger tip) for rotation.
    
    Args:
        landmarks: MediaPipe hand landmarks
        frame_shape: Shape of the video frame (height, width)
        
    Returns:
        bool: True if pinch gesture is detected
    """
    height, width = frame_shape[:2]
    
    # Get thumb tip (landmark 4) and index finger tip (landmark 8) coordinates
    thumb_tip_x = landmarks.landmark[4].x * width
    thumb_tip_y = landmarks.landmark[4].y * height
    index_tip_x = landmarks.landmark[8].x * width
    index_tip_y = landmarks.landmark[8].y * height
    
    # Get thumb MCP and index MCP for additional validation
    thumb_mcp_x = landmarks.landmark[2].x * width
    thumb_mcp_y = landmarks.landmark[2].y * height
    index_mcp_x = landmarks.landmark[5].x * width
    index_mcp_y = landmarks.landmark[5].y * height
    
    # Calculate distance between thumb tip and index finger tip
    tip_distance = np.sqrt((thumb_tip_x - index_tip_x)**2 + (thumb_tip_y - index_tip_y)**2)
    
    # Calculate distance between thumb MCP and index MCP for scale reference
    mcp_distance = np.sqrt((thumb_mcp_x - index_mcp_x)**2 + (thumb_mcp_y - index_mcp_y)**2)
    
    # Normalize tip distance by hand size (using MCP distance as reference)
    if mcp_distance > 0:
        normalized_distance = tip_distance / mcp_distance
        # Pinch detected if normalized distance is small (fingers close together)
        # Increased threshold for better detection sensitivity
        return normalized_distance < 0.6  # More lenient threshold for easier detection
    
    # Fallback to absolute distance if normalization fails
    return tip_distance < PINCH_THRESHOLD

# =============================================================================
# GESTURE DETECTION FUNCTIONS
# =============================================================================

def detect_single_hand_gestures(landmarks, frame_shape, hand_label):
    """
    Detect single hand gestures (left/right movement and fist for hard drop).
    
    Args:
        landmarks: MediaPipe hand landmarks
        frame_shape: Shape of the video frame
        hand_label: "Left" or "Right" hand label
        
    Returns:
        str: Detected gesture ("left", "right", "hardDrop", "none")
    """
    if not landmarks:
        return "none"

    # Get landmark positions
    wrist_y = landmarks.landmark[0].y
    
    # Fingertip positions (landmarks 4, 8, 12, 16, 20)
    thumb_tip_y = landmarks.landmark[4].y
    index_tip_y = landmarks.landmark[8].y
    middle_tip_y = landmarks.landmark[12].y
    ring_tip_y = landmarks.landmark[16].y
    pinky_tip_y = landmarks.landmark[20].y
    
    # Finger MCP (knuckle) positions for fist detection
    index_mcp_y = landmarks.landmark[5].y
    middle_mcp_y = landmarks.landmark[9].y
    ring_mcp_y = landmarks.landmark[13].y
    pinky_mcp_y = landmarks.landmark[17].y
    
    # PIP joint positions for better fist detection
    index_pip_y = landmarks.landmark[6].y
    middle_pip_y = landmarks.landmark[10].y
    ring_pip_y = landmarks.landmark[14].y
    pinky_pip_y = landmarks.landmark[18].y
    
    # Improved fist detection: check if fingertips are curled below PIPs
    # This is more reliable than checking against MCPs
    fist_fingers = 0
    total_fingers = 4
    
    # Check each finger individually (excluding thumb for now)
    if index_tip_y > index_pip_y + FIST_THRESHOLD:
        fist_fingers += 1
    if middle_tip_y > middle_pip_y + FIST_THRESHOLD:
        fist_fingers += 1
    if ring_tip_y > ring_pip_y + FIST_THRESHOLD:
        fist_fingers += 1
    if pinky_tip_y > pinky_pip_y + FIST_THRESHOLD:
        fist_fingers += 1
    
    # Additional check: ensure thumb is also curled (thumb tip below thumb MCP)
    thumb_mcp_y = landmarks.landmark[2].y
    thumb_curled = thumb_tip_y > thumb_mcp_y
    
    # Fist detected if most fingers are curled (at least 3 out of 4) and thumb is curled
    fist_detected = (fist_fingers >= 3) and thumb_curled
    
    # Check for raised hand (open palm facing camera)
    avg_fingers_height = (index_tip_y + middle_tip_y + ring_tip_y + pinky_tip_y) / 4
    raised_hand = avg_fingers_height < wrist_y - 0.1  # Reduced threshold for better detection
    
    # Priority: fist detection first, then raised hand
    if fist_detected:
        return "hardDrop"
    elif raised_hand and not fist_detected:
        if hand_label == "Right":
            return "right"
        else:
            return "left"
    return "none"

# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def visualize_gesture(frame, gesture):
    """
    Add visual indication of the detected gesture to the frame.
    
    Args:
        frame: Video frame to draw on
        gesture: Detected gesture string
    """
    gesture_text = f"Gesture: {gesture.capitalize()}"
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
        cv2.putText(frame, "Gesture Pinch", (50, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(frame, "Rotasi Aktif!", (50, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        cv2.putText(frame, "Tangan: Kiri/Kanan", (50, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    elif gesture == "hardDrop":
        cv2.arrowedLine(frame, (100, 100), (100, 150), (0, 0, 255), 5)
        cv2.putText(frame, "Genggam Tangan", (50, 170),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(frame, "Hard Drop Aktif!", (50, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    
    # Add instruction text
    cv2.putText(frame, "Instructions:", (10, frame.shape[0] - 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(frame, "- Angkat tangan: Gerak kiri/kanan", (10, frame.shape[0] - 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    cv2.putText(frame, "- Pinch (jempol+telunjuk): Rotasi", (10, frame.shape[0] - 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    cv2.putText(frame, "- Genggam tangan: Hard Drop", (10, frame.shape[0] - 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

def draw_debug_info(frame, landmarks, hand_label):
    """
    Draw debug information for gesture detection on the frame.
    
    Args:
        frame: Video frame to draw on
        landmarks: MediaPipe hand landmarks
        hand_label: "Left" or "Right" hand label
    """
    if not landmarks:
        return
    
    height, width = frame.shape[:2]
    
    # Get key landmarks
    thumb_tip = landmarks.landmark[4]
    index_tip = landmarks.landmark[8]
    thumb_mcp = landmarks.landmark[2]
    index_mcp = landmarks.landmark[5]
    
    # Calculate distances for pinch detection
    thumb_tip_x, thumb_tip_y = int(thumb_tip.x * width), int(thumb_tip.y * height)
    index_tip_x, index_tip_y = int(index_tip.x * width), int(index_tip.y * height)
    thumb_mcp_x, thumb_mcp_y = int(thumb_mcp.x * width), int(thumb_mcp.y * height)
    index_mcp_x, index_mcp_y = int(index_mcp.x * width), int(index_mcp.y * height)
    
    tip_distance = np.sqrt((thumb_tip_x - index_tip_x)**2 + (thumb_tip_y - index_tip_y)**2)
    mcp_distance = np.sqrt((thumb_mcp_x - index_mcp_x)**2 + (thumb_mcp_y - index_mcp_y)**2)
    
    if mcp_distance > 0:
        normalized_distance = tip_distance / mcp_distance
    else:
        normalized_distance = 999
    
    # Draw circles on thumb and index finger tips
    cv2.circle(frame, (thumb_tip_x, thumb_tip_y), 8, (255, 0, 255), -1)  # Magenta for thumb
    cv2.circle(frame, (index_tip_x, index_tip_y), 8, (0, 255, 255), -1)  # Cyan for index
    
    # Draw line between thumb and index finger
    cv2.line(frame, (thumb_tip_x, thumb_tip_y), (index_tip_x, index_tip_y), (255, 255, 0), 2)
    
    # Check pinch status for visual feedback
    pinch_detected = normalized_distance < 0.6 if mcp_distance > 0 else tip_distance < PINCH_THRESHOLD
    pinch_status = "PINCH DETECTED!" if pinch_detected else "Not Pinching"
    pinch_color = (0, 255, 0) if pinch_detected else (255, 255, 255)
    
    # Display debug text
    debug_y_start = 400
    cv2.putText(frame, f"Hand: {hand_label}", (10, debug_y_start),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(frame, f"Tip Distance: {tip_distance:.1f}", (10, debug_y_start + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(frame, f"Normalized: {normalized_distance:.2f}", (10, debug_y_start + 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(frame, f"Pinch Threshold: 0.6", (10, debug_y_start + 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(frame, pinch_status, (10, debug_y_start + 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, pinch_color, 2)
    
    # Check fist status for additional debug info
    index_tip_y_norm = landmarks.landmark[8].y
    index_pip_y_norm = landmarks.landmark[6].y
    
    fist_status = "Open" if index_tip_y_norm <= index_pip_y_norm else "Curled"
    cv2.putText(frame, f"Fist Status: {fist_status}", (10, debug_y_start + 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
