import cv2
import mediapipe as mp
import numpy as np
import time

# Initialize MediaPipe Hand detection globally
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,  # Reduced from 0.7 for better performance
    min_tracking_confidence=0.5
)

def read_frame(cap):
    """Read a frame from the webcam and return it"""
    ret, frame = cap.read()
    if not ret:
        return None
    # Flip the frame horizontally to correct mirror effect
    frame = cv2.flip(frame, 1)
    return frame

def setup_webcam(device_id=0, width=640, height=480):
    """Set up and initialize the webcam with specified dimensions"""
    cap = cv2.VideoCapture(device_id)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return None
    
    # Set the frame width and height
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, 60)  # Request 60 FPS if supported
    
    # Verify the settings took effect
    actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Webcam opened successfully. Resolution: {actual_width}x{actual_height}, FPS: {actual_fps}")
    
    return cap

def detect_hand_gesture(frame):
    """Detect hand gestures using MediaPipe and map to Tetris controls"""
    # Convert the frame to RGB (required by MediaPipe)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame and detect hands
    results = hands.process(rgb_frame)
    
    gesture = "none"
    
    if results.multi_hand_landmarks:
        # Draw landmarks for all detected hands
        for hand_landmarks in results.multi_hand_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS,
                mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp.solutions.drawing_utils.DrawingSpec(color=(255, 0, 0), thickness=2)
            )
        
        # Detect clap with two hands
        if len(results.multi_hand_landmarks) == 2:
            # Check if hands are close to each other (clap)
            if detect_clap(results.multi_hand_landmarks[0], results.multi_hand_landmarks[1], frame.shape):
                gesture = "rotate"
        else:
            # Single hand gestures
            hand_landmarks = results.multi_hand_landmarks[0]
            gesture = detect_gestures(hand_landmarks, frame.shape, results.multi_handedness[0].classification[0].label)
    
    # Visualize the detected gesture
    frame = visualize_gesture(frame, gesture)
    
    return frame, gesture

def detect_clap(hand1_landmarks, hand2_landmarks, frame_shape):
    """Detect if two hands are close enough to be considered a clap"""
    height, width = frame_shape[:2]
    
    # Get the center point of each hand (palm)
    hand1_palm_x = hand1_landmarks.landmark[9].x * width
    hand1_palm_y = hand1_landmarks.landmark[9].y * height
    
    hand2_palm_x = hand2_landmarks.landmark[9].x * width
    hand2_palm_y = hand2_landmarks.landmark[9].y * height
    
    # Calculate distance between the two palms
    palm_distance = np.sqrt((hand1_palm_x - hand2_palm_x)**2 + 
                          (hand1_palm_y - hand2_palm_y)**2)
    
    # Threshold for clap detection - adjust based on testing
    CLAP_THRESHOLD = 150  # pixels
    
    return palm_distance < CLAP_THRESHOLD

def detect_gestures(landmarks, frame_shape, hand_label):
    """
    Detect hand gestures and map them to Tetris controls:
    - Angkat tangan kanan → right
    - Angkat tangan kiri → left
    - Tepuk tangan → rotate
    Returns: action (string): 'left', 'right', 'rotate', 'none'
    """
    if not landmarks:
        return "none"
    
    height, width = frame_shape[:2]
    
    # Get key landmarks for gesture detection
    wrist_y = landmarks.landmark[0].y
    index_tip_y = landmarks.landmark[8].y
    middle_tip_y = landmarks.landmark[12].y
    ring_tip_y = landmarks.landmark[16].y
    pinky_tip_y = landmarks.landmark[20].y
    
    # Calculate average height of fingertips relative to wrist
    avg_fingers_height = (index_tip_y + middle_tip_y + ring_tip_y + pinky_tip_y) / 4
    raised_hand = avg_fingers_height < wrist_y - 0.15  # Hand is raised if fingers are significantly above wrist
    
    if raised_hand:
        # Use MediaPipe's hand detection label instead of thumb position
        if hand_label == "Right":
            return "right"
        else:
            return "left"
    
    return "none"

def visualize_gesture(frame, gesture):
    """Add visual indication of detected gesture to the frame"""
    # Display the detected gesture
    gesture_text = f"Gesture: {gesture}"
    cv2.putText(frame, gesture_text, (10, 70), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    
    # Add visual cue based on the gesture
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
    
    return frame

def main():
    webcam = None
    prev_time = 0
    fps_values = []
    
    try:
        webcam = setup_webcam(width=640, height=480)
        
        if webcam is not None:
            print("Press 'q' to quit.")
            while True:
                # Calculate FPS
                current_time = time.time()
                fps = 1 / (current_time - prev_time)
                prev_time = current_time
                fps_values.append(fps)
                
                # Calculate average FPS over last 30 frames
                if len(fps_values) > 30:
                    fps_values.pop(0)
                avg_fps = sum(fps_values) / len(fps_values)
                
                frame = read_frame(webcam)
                if frame is None:
                    print("Error: Failed to capture image.")
                    break
                
                # Process the frame with hand gesture detection
                processed_frame, gesture = detect_hand_gesture(frame)
                
                # Respond to the gesture
                if gesture == "left":
                    # Code to move Tetris piece left
                    print("Moving left")
                elif gesture == "right":
                    # Code to move Tetris piece right
                    print("Moving right")
                elif gesture == "rotate":
                    # Code to rotate Tetris piece
                    print("Rotating piece")
                
                # Display FPS on frame
                cv2.putText(processed_frame, f"FPS: {avg_fps:.1f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Display the processed frame
                cv2.imshow('Motion Tetris', processed_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Cleaning up...")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if webcam is not None:
            webcam.release()
        cv2.destroyAllWindows()
        print(f"Final average FPS: {sum(fps_values) / len(fps_values):.1f}")
        print("Cleanup complete.")

if __name__ == "__main__":
    main()