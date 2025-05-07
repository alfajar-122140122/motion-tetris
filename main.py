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
    """Detect hand gestures using MediaPipe and draw landmark points"""
    # Convert the frame to RGB (required by MediaPipe)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame and detect hands
    results = hands.process(rgb_frame)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Get frame dimensions
            height, width, _ = frame.shape
            
            # Convert normalized coordinates to pixel coordinates
            landmark_points = []
            for landmark in hand_landmarks.landmark:
                # Convert normalized coordinates to pixel coordinates
                x = int(landmark.x * width)
                y = int(landmark.y * height)
                landmark_points.append((x, y))
                
                # Draw circle at each landmark point
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
            
            # Draw connections between landmarks
            mp.solutions.drawing_utils.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS,
                mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp.solutions.drawing_utils.DrawingSpec(color=(255, 0, 0), thickness=2)
            )
            
            # Optionally, you can label specific landmarks
            # Example: Label thumb tip (landmark 4)
            if len(landmark_points) > 4:
                thumb_tip = landmark_points[4]
                cv2.putText(frame, "Thumb", 
                           (thumb_tip[0], thumb_tip[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

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
                processed_frame = detect_hand_gesture(frame)
                
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