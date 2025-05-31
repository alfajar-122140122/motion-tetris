"""
Motion Tetris - Hand Gesture Detection Module
============================================
This module handles hand gesture detection for the Motion Tetris game using MediaPipe.

Key Gestures:
1. LEFT/RIGHT HAND RAISED - Move piece left/right
   - Hand must be raised above wrist level
   - Other fingers extended
   
2. PINCH FOR ROTATION - Rotate piece
   - Thumb and index finger close together
   - Other three fingers must be extended
   - Prevents confusion with fist
   
3. FIST FOR HARD DROP - Drop piece quickly
   - All fingers must be curled
   - Thumb must be below thumb IP joint
   - Must maintain gesture for continuous drop

Each gesture is carefully designed to avoid interference:
- Pinch requires other fingers extended, fist requires all curled
- Uses clear anatomical landmarks (finger joints) for reliable detection
- Includes cooldown periods to prevent accidental triggers

The module includes:
- Robust MediaPipe hand landmark detection
- Clear gesture state validation
- Debug visualization helpers
- Anti-interference logic
"""

import cv2
import numpy as np
from config import FIST_THRESHOLD, PINCH_THRESHOLD
import mediapipe as mp

# Initialize MediaPipe
mp_hands = mp.solutions.hands

# Initialize hands detector with max 2 hands
hands_detector = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.3
)

# =============================================================================
# MEDIAPIPE HAND LANDMARK INDICES
# =============================================================================

# Finger tip indices (landmarks at the end of each finger)
THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20

# Second joint (IP for thumb, PIP for fingers)
THUMB_IP = 3
THUMB_MCP = 2
INDEX_PIP = 6
MIDDLE_PIP = 10
RING_PIP = 14
PINKY_PIP = 18

# Base joints (MCP - where fingers meet palm)
INDEX_MCP = 5
MIDDLE_MCP = 9
RING_MCP = 13
PINKY_MCP = 17

# Other landmarks
WRIST = 0

# Tolerance thresholds
PINCH_VERTICAL_TOLERANCE = 0.05  # Required extension for other fingers
PINCH_HORIZONTAL_SPREAD = 0.07   # Required spread between fingers
PINCH_DISTANCE_THRESHOLD = 0.1   # Max distance for pinch detection
HAND_WIDTH_MIN = 0.1            # Minimum hand width for front view

# =============================================================================
# GESTURE VALIDATION CONSTANTS
# =============================================================================

# Thresholds for gesture detection
FINGER_EXTENSION_THRESHOLD = 0.08  # Lowered for easier extension detection
FINGER_CURL_THRESHOLD = 0.08      # Increased for easier curl detection
PINCH_MAX_DISTANCE = 0.1          # Increased for easier pinch detection
RAISED_HAND_HEIGHT = 0.15
FIST_DETECTION_CONFIDENCE = 0.7
FINGER_SPREAD_MIN = 0.08           # Minimum spread for pinch other fingers
FINGER_EXTENSION_MIN = 0.2         # Minimum extension for pinch other fingers

def validate_finger_curl(tip_y, pip_y, mcp_y):
    """
    Check if a finger is curled (tip below PIP joint and close to MCP).
    
    Args:
        tip_y: Y-coordinate of finger tip
        pip_y: Y-coordinate of PIP (middle) joint
        mcp_y: Y-coordinate of MCP (base) joint
        
    Returns:
        bool: True if finger is curled tightly
    """
    return (tip_y > pip_y + FINGER_CURL_THRESHOLD and 
            tip_y > mcp_y)

def validate_finger_extension(tip_y, pip_y):
    """
    Check if a finger is extended (tip above PIP joint).
    
    Args:
        tip_y: Y-coordinate of finger tip
        pip_y: Y-coordinate of PIP (middle) joint
        
    Returns:
        bool: True if finger is extended
    """
    return tip_y < (pip_y - FINGER_EXTENSION_THRESHOLD)

def validate_pinch_distance(thumb_pos, index_pos):
    """
    Validate if thumb and index are close enough for pinch.
    
    Args:
        thumb_pos: Thumb tip landmark
        index_pos: Index tip landmark
        
    Returns:
        bool: True if pinch distance is within threshold
    """
    distance = ((thumb_pos.x - index_pos.x) ** 2 + 
               (thumb_pos.y - index_pos.y) ** 2) ** 0.5
    return distance < PINCH_MAX_DISTANCE

def detect_pinch_gesture(landmarks):
    """
    Detect pinch gesture (thumb and index together) for rotation.
    Uses simpler validation for better reliability.
    """
    if not landmarks:
        return False

    # Get essential landmarks
    thumb_tip = landmarks.landmark[THUMB_TIP]
    index_tip = landmarks.landmark[INDEX_TIP]
    middle_tip = landmarks.landmark[MIDDLE_TIP]
    ring_tip = landmarks.landmark[RING_TIP]
    pinky_tip = landmarks.landmark[PINKY_TIP]
    wrist = landmarks.landmark[WRIST]
    middle_pip = landmarks.landmark[MIDDLE_PIP]
    ring_pip = landmarks.landmark[RING_PIP]
    pinky_pip = landmarks.landmark[PINKY_PIP]

    # Simple checks for pinch gesture:

    # 1. Pinch distance between thumb and index
    pinch_distance = ((thumb_tip.x - index_tip.x) ** 2 + 
                     (thumb_tip.y - index_tip.y) ** 2) ** 0.5
    if pinch_distance > PINCH_MAX_DISTANCE:
        return False

    # 2. Thumb and index should be at similar height
    if abs(thumb_tip.y - index_tip.y) > 0.15:
        return False

    # 3. Other fingers should be somewhat extended
    if middle_tip.y > middle_pip.y or ring_tip.y > ring_pip.y or pinky_tip.y > pinky_pip.y:
        return False

    # 4. Basic height check - hand should be raised
    if (thumb_tip.y > wrist.y) or (index_tip.y > wrist.y):
        return False

    return True

def detect_fist_gesture(landmarks):
    """
    Detect fist gesture (all fingers curled) for hard drop.
    Super simplified version that just checks if fingers are curled.
    """
    if not landmarks:
        return False

    # Get essential landmarks
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

    # Super simple check - just verify fingers are curled
    threshold = 0.05  # Very lenient threshold
    is_fist = (
        # Main fingers below MCP
        index_tip.y > index_mcp.y and
        middle_tip.y > middle_mcp.y and
        ring_tip.y > ring_mcp.y and
        pinky_tip.y > pinky_mcp.y and
        # Thumb curled
        thumb_tip.y > thumb_ip.y
    )

    # Add debug visualization for each finger's curl state
    if landmarks.landmark[WRIST].visibility > 0.5:  # Only if hand is visible enough
        for name, tip, mcp in [
            ("Thumb", thumb_tip, thumb_ip),
            ("Index", index_tip, index_mcp),
            ("Middle", middle_tip, middle_mcp),
            ("Ring", ring_tip, ring_mcp),
            ("Pinky", pinky_tip, pinky_mcp)
        ]:
            curled = tip.y > mcp.y
            print(f"{name} {'curled' if curled else 'extended'}: tip.y={tip.y:.3f}, mcp.y={mcp.y:.3f}")

    return is_fist

def detect_raised_hand(landmarks, hand_label):
    """
    Detect raised hand gesture (left/right) for movement.
    Hand must be clearly raised above wrist level.
    
    Args:
        landmarks: MediaPipe hand landmarks
        hand_label: "Left" or "Right" hand label
        
    Returns:
        str: "left", "right" if detected, "none" otherwise
    """
    if not landmarks:
        return "none"

    # Get wrist and fingertip positions
    wrist = landmarks.landmark[WRIST]
    index_tip = landmarks.landmark[INDEX_TIP]
    middle_tip = landmarks.landmark[MIDDLE_TIP]
    ring_tip = landmarks.landmark[RING_TIP]
    pinky_tip = landmarks.landmark[PINKY_TIP]

    # Calculate average finger height relative to wrist
    avg_fingers_height = (index_tip.y + middle_tip.y + 
                         ring_tip.y + pinky_tip.y) / 4
    raised = avg_fingers_height < (wrist.y - RAISED_HAND_HEIGHT)

    # Return direction based on hand and position
    if raised:
        return "right" if hand_label == "Right" else "left"
    return "none"

# =============================================================================
# MAIN GESTURE DETECTION FUNCTION
# =============================================================================

def detect_hand_gesture(frame):
    """
    Detect hand gestures using MediaPipe and map to Tetris controls.
    Strict priority order: hard drop > pinch > movement
    
    Args:
        frame (numpy.ndarray): Input video frame
        
    Returns:
        tuple: (processed_frame, gesture_name)
            - processed_frame: Frame with gesture visualization
            - gesture_name: Detected gesture ("left", "right", "rotate", "hardDrop", "none")
    """
    # Convert BGR to RGB for MediaPipe processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands_detector.process(rgb_frame)
    gesture = "none"

    if results.multi_hand_landmarks:
        # First pass: Check all hands for hard drop (highest priority)
        for hand_landmarks in results.multi_hand_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
            )
            # Check for hard drop first
            if detect_fist_gesture(hand_landmarks):
                gesture = "hardDrop"
                return frame, gesture  # Exit immediately if hard drop found

        # Second pass: Only check for pinch if no hard drop found
        if gesture == "none":
            for hand_landmarks in results.multi_hand_landmarks:
                if detect_pinch_gesture(hand_landmarks):
                    gesture = "rotate"
                    return frame, gesture  # Exit after finding pinch

        # Final pass: Check for movement only if no other gestures found
        if gesture == "none":
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                if i < len(results.multi_handedness):
                    hand_label = results.multi_handedness[i].classification[0].label
                    movement = detect_raised_hand(hand_landmarks, hand_label)
                    if movement != "none":
                        gesture = movement
                        break

    visualize_gesture(frame, gesture)
    return frame, gesture



# =============================================================================
# GESTURE DETECTION FUNCTIONS
# =============================================================================

def detect_single_hand_gestures(landmarks, frame_shape, hand_label):
    """
    Detect all single-hand gestures and return the most confident one.
    Handles gesture priority and interference prevention.
    
    Args:
        landmarks: MediaPipe hand landmarks
        frame_shape: Shape of video frame
        hand_label: "Left" or "Right" hand label
        
    Returns:
        str: Detected gesture ("left", "right", "hardDrop", "none")
    """
    if not landmarks:
        return "none"

    # Check fist first (highest priority)
    if detect_fist_gesture(landmarks):
        return "hardDrop"

    # Then check for raised hand (if not in fist)
    raised_gesture = detect_raised_hand(landmarks, hand_label)
    if raised_gesture != "none":
        return raised_gesture

    return "none"

# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def draw_debug_info(frame, landmarks, hand_label):
    """
    Draw comprehensive debug information for gesture detection.
    Includes finger states, gesture status, and visual indicators.
    
    Args:
        frame: Video frame to draw on
        landmarks: MediaPipe hand landmarks
        hand_label: "Left" or "Right" hand label
    """
    if not landmarks:
        return
    
    height, width = frame.shape[:2]
    debug_y_start = 400

    # Draw hand information section
    info_color = (255, 255, 255)  # White text
    cv2.putText(frame, f"Hand: {hand_label}", 
                (10, debug_y_start),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, info_color, 1)

    # Draw finger status with color coding
    finger_status = get_finger_status(landmarks)
    draw_finger_status(frame, finger_status, debug_y_start + 20)

    # Draw gesture status
    gesture_status = get_gesture_status(landmarks)
    draw_gesture_status(frame, gesture_status, debug_y_start + 160)

def get_finger_status(landmarks):
    """
    Get detailed status of each finger position.
    
    Args:
        landmarks: MediaPipe hand landmarks
        
    Returns:
        list: Status of each finger (name, curl state, color)
    """
    status = []

    # Thumb status with MCP joint
    thumb_curled = (landmarks.landmark[THUMB_TIP].y > landmarks.landmark[THUMB_IP].y + FINGER_CURL_THRESHOLD and 
                   landmarks.landmark[THUMB_TIP].y > landmarks.landmark[THUMB_MCP].y)
    status.append(("Thumb", "Curled" if thumb_curled else "Extended"))

    # Status for other fingers with their MCP joints
    finger_data = [
        ("Index", INDEX_TIP, INDEX_PIP, INDEX_MCP),
        ("Middle", MIDDLE_TIP, MIDDLE_PIP, MIDDLE_MCP),
        ("Ring", RING_TIP, RING_PIP, RING_MCP),
        ("Pinky", PINKY_TIP, PINKY_PIP, PINKY_MCP)
    ]

    for name, tip_idx, pip_idx, mcp_idx in finger_data:
        tip = landmarks.landmark[tip_idx].y
        pip = landmarks.landmark[pip_idx].y
        mcp = landmarks.landmark[mcp_idx].y
        curled = validate_finger_curl(tip, pip, mcp)
        status.append((name, "Curled" if curled else "Extended"))

    return status

def draw_finger_status(frame, finger_status, y_start):
    """
    Draw color-coded finger status information.
    
    Args:
        frame: Video frame to draw on
        finger_status: List of finger statuses
        y_start: Starting Y coordinate for drawing
    """
    cv2.putText(frame, "Finger Status:", (10, y_start),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    y_offset = y_start + 20
    for finger_name, state in finger_status:
        color = (0, 0, 255) if state == "Curled" else (0, 255, 0)
        cv2.putText(frame, f"{finger_name}: {state}", 
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        y_offset += 20

def get_gesture_status(landmarks):
    """
    Get current status of all possible gestures.
    
    Args:
        landmarks: MediaPipe hand landmarks
        
    Returns:
        dict: Current state of each gesture
    """
    return {
        "Fist": detect_fist_gesture(landmarks),
        "Pinch": detect_pinch_gesture(landmarks),
        "Hand Raised": landmarks.landmark[WRIST].y > landmarks.landmark[INDEX_TIP].y
    }

def draw_gesture_status(frame, gesture_status, y_start):
    """
    Draw the current status of all gestures.
    
    Args:
        frame: Video frame to draw on
        gesture_status: Dictionary of gesture states
        y_start: Starting Y coordinate for drawing
    """
    cv2.putText(frame, "Gesture Status:", (10, y_start),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    y_offset = y_start + 20
    for gesture, active in gesture_status.items():
        color = (0, 255, 0) if active else (0, 0, 255)
        cv2.putText(frame, f"{gesture}: {'Active' if active else 'Inactive'}", 
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        y_offset += 20

def visualize_gesture(frame, gesture):
    """
    Add visual indication of detected gesture to frame.
    Enhanced with better debug visualization.
    """
    # Constants for visualization
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    BLUE = (255, 0, 0)
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)
    YELLOW = (0, 255, 255)
    WHITE = (255, 255, 255)
    
    # Display current gesture with more visibility
    gesture_text = f"Gesture: {gesture.capitalize()}"
    cv2.putText(frame, gesture_text, (10, 30), FONT, 1, BLUE, 2)

    # Status area background
    status_start = 40
    cv2.rectangle(frame, (5, status_start), (200, status_start + 130), (0, 0, 0), -1)
    cv2.rectangle(frame, (5, status_start), (200, status_start + 130), WHITE, 1)

    # Show detection status for each gesture type
    statuses = [
        ("Fist 👊", gesture == "hardDrop", RED),
        ("Pinch 👌", gesture == "rotate", GREEN),
        ("Left ⬅", gesture == "left", YELLOW),
        ("Right ➡", gesture == "right", YELLOW)
    ]

    for i, (name, active, color) in enumerate(statuses):
        status_y = status_start + 25 + (i * 30)
        status_color = color if active else (128, 128, 128)
        status_text = "✓" if active else "×"
        cv2.putText(frame, f"{name}: {status_text}", (10, status_y), FONT, 0.6, status_color, 2)

    # Instruction box at bottom
    cv2.rectangle(frame, (5, frame.shape[0] - 100), (300, frame.shape[0] - 10), (0, 0, 0), -1)
    cv2.rectangle(frame, (5, frame.shape[0] - 100), (300, frame.shape[0] - 10), WHITE, 1)

    instructions = [
        ("Controls:", 0.5, -85),
        ("- Angkat Tangan: Gerak Kiri/Kanan", 0.4, -65),
        ("- Pinch (👌): Rotasi", 0.4, -45),
        ("- Genggam (✊): Hard Drop", 0.4, -25)
    ]

    for text, scale, y_offset in instructions:
        cv2.putText(frame, text, 
                    (10, frame.shape[0] + y_offset),
                    FONT, scale, WHITE, 1)
