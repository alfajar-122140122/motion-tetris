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
    min_tracking_confidence=0.3
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

def create_tetris_board():
    """Create an empty Tetris board as a 20x10 grid using numpy"""
    board = np.zeros((20, 10), dtype=int)
    return board

def draw_tetris_board(board, cell_size=30):
    """Draw the Tetris board on a new canvas"""
    # Create a black canvas for the board
    height, width = board.shape
    board_canvas = np.zeros((height * cell_size, width * cell_size, 3), dtype=np.uint8)
    
    # Draw grid lines
    for i in range(height + 1):
        cv2.line(board_canvas, (0, i * cell_size), (width * cell_size, i * cell_size), (50, 50, 50), 1)
    for j in range(width + 1):
        cv2.line(board_canvas, (j * cell_size, 0), (j * cell_size, height * cell_size), (50, 50, 50), 1)
    
    return board_canvas

def combine_board_and_webcam(board_canvas, webcam_frame):
    """Combine the Tetris board and webcam feed side by side"""
    # Resize webcam frame to match board height
    board_height = board_canvas.shape[0]
    webcam_height = webcam_frame.shape[0]
    scale = board_height / webcam_height
    new_width = int(webcam_frame.shape[1] * scale)
    webcam_resized = cv2.resize(webcam_frame, (new_width, board_height))
    
    # Combine the two images horizontally
    combined = np.hstack((board_canvas, webcam_resized))
    return combined

def create_tetris_shapes():
    """Create all Tetris shapes (tetrominoes) and their rotations"""
    # Shape format: Each shape is a list of rotations
    # Each rotation is a 4x4 array where:
    # 0 = empty, 1-7 = shape ID (for different colors)
    
    # I Shape - Cyan (1)
    I_SHAPE = [
        np.array([[0, 0, 0, 0],
                 [1, 1, 1, 1],
                 [0, 0, 0, 0],
                 [0, 0, 0, 0]]),
        np.array([[0, 0, 1, 0],
                 [0, 0, 1, 0],
                 [0, 0, 1, 0],
                 [0, 0, 1, 0]])
    ]

    # J Shape - Blue (2)
    J_SHAPE = [
        np.array([[2, 0, 0, 0],
                 [2, 2, 2, 0],
                 [0, 0, 0, 0],
                 [0, 0, 0, 0]]),
        np.array([[0, 2, 2, 0],
                 [0, 2, 0, 0],
                 [0, 2, 0, 0],
                 [0, 0, 0, 0]]),
        np.array([[0, 0, 0, 0],
                 [2, 2, 2, 0],
                 [0, 0, 2, 0],
                 [0, 0, 0, 0]]),
        np.array([[0, 2, 0, 0],
                 [0, 2, 0, 0],
                 [2, 2, 0, 0],
                 [0, 0, 0, 0]])
    ]

    # L Shape - Orange (3)
    L_SHAPE = [
        np.array([[0, 0, 3, 0],
                 [3, 3, 3, 0],
                 [0, 0, 0, 0],
                 [0, 0, 0, 0]]),
        np.array([[0, 3, 0, 0],
                 [0, 3, 0, 0],
                 [0, 3, 3, 0],
                 [0, 0, 0, 0]]),
        np.array([[0, 0, 0, 0],
                 [3, 3, 3, 0],
                 [3, 0, 0, 0],
                 [0, 0, 0, 0]]),
        np.array([[3, 3, 0, 0],
                 [0, 3, 0, 0],
                 [0, 3, 0, 0],
                 [0, 0, 0, 0]])
    ]

    # O Shape - Yellow (4)
    O_SHAPE = [
        np.array([[0, 4, 4, 0],
                 [0, 4, 4, 0],
                 [0, 0, 0, 0],
                 [0, 0, 0, 0]])
    ]

    # S Shape - Green (5)
    S_SHAPE = [
        np.array([[0, 5, 5, 0],
                 [5, 5, 0, 0],
                 [0, 0, 0, 0],
                 [0, 0, 0, 0]]),
        np.array([[0, 5, 0, 0],
                 [0, 5, 5, 0],
                 [0, 0, 5, 0],
                 [0, 0, 0, 0]])
    ]

    # T Shape - Purple (6)
    T_SHAPE = [
        np.array([[0, 6, 0, 0],
                 [6, 6, 6, 0],
                 [0, 0, 0, 0],
                 [0, 0, 0, 0]]),
        np.array([[0, 6, 0, 0],
                 [0, 6, 6, 0],
                 [0, 6, 0, 0],
                 [0, 0, 0, 0]]),
        np.array([[0, 0, 0, 0],
                 [6, 6, 6, 0],
                 [0, 6, 0, 0],
                 [0, 0, 0, 0]]),
        np.array([[0, 6, 0, 0],
                 [6, 6, 0, 0],
                 [0, 6, 0, 0],
                 [0, 0, 0, 0]])
    ]

    # Z Shape - Red (7)
    Z_SHAPE = [
        np.array([[7, 7, 0, 0],
                 [0, 7, 7, 0],
                 [0, 0, 0, 0],
                 [0, 0, 0, 0]]),
        np.array([[0, 0, 7, 0],
                 [0, 7, 7, 0],
                 [0, 7, 0, 0],
                 [0, 0, 0, 0]])
    ]

    return {
        'I': {'shape': I_SHAPE, 'color': (255, 255, 0)},   # Cyan
        'J': {'shape': J_SHAPE, 'color': (255, 0, 0)},     # Blue
        'L': {'shape': L_SHAPE, 'color': (255, 165, 0)},   # Orange
        'O': {'shape': O_SHAPE, 'color': (0, 255, 255)},   # Yellow
        'S': {'shape': S_SHAPE, 'color': (0, 255, 0)},     # Green
        'T': {'shape': T_SHAPE, 'color': (128, 0, 128)},   # Purple
        'Z': {'shape': Z_SHAPE, 'color': (0, 0, 255)}      # Red
    }

def draw_tetris_shape(board_canvas, shape, rotation_idx, pos_x, pos_y, cell_size=30):
    """Draw a Tetris shape on the board canvas"""
    shape_array = shape['shape'][rotation_idx]
    color = shape['color']
    
    for i in range(4):
        for j in range(4):
            if shape_array[i][j] != 0:
                x1 = (pos_x + j) * cell_size
                y1 = (pos_y + i) * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                # Draw filled rectangle with shape color
                cv2.rectangle(board_canvas, (x1, y1), (x2, y2), color, -1)
                # Draw border
                cv2.rectangle(board_canvas, (x1, y1), (x2, y2), (180, 180, 180), 1)

def main():
    webcam = None
    prev_time = 0
    fps_values = []
    tetris_board = create_tetris_board()
    tetris_shapes = create_tetris_shapes()
    
    # Game state variables
    current_shape_key = 'T'  # Start with T-shape
    current_rotation = 0
    pos_x, pos_y = 3, 0
    shape_keys = list(tetris_shapes.keys())
    shape_index = 0
    
    # Game timing variables
    last_move_time = time.time()
    move_delay = 0.5  # Delay between automatic downward movements (in seconds)
    gesture_delay = 0.3  # Delay between gesture recognition (in seconds)
    last_gesture_time = time.time()
    
    try:
        webcam = setup_webcam(width=640, height=480)
        
        if webcam is not None:
            print("Press 'q' to quit, 'a'/'d' for left/right, 'w' to rotate, space to change shape")
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
                
                # Draw Tetris board
                board_canvas = draw_tetris_board(tetris_board)
                
                # Handle gestures with delay to prevent rapid movement
                if current_time - last_gesture_time > gesture_delay:
                    if gesture == "left" and pos_x > 0:
                        pos_x -= 1
                        last_gesture_time = current_time
                    elif gesture == "right" and pos_x < 6:  # 6 = 10-4 (board width - max shape width)
                        pos_x += 1
                        last_gesture_time = current_time
                    elif gesture == "rotate":
                        current_rotation = (current_rotation + 1) % len(tetris_shapes[current_shape_key]['shape'])
                        last_gesture_time = current_time
                
                # Automatic downward movement with delay
                if current_time - last_move_time > move_delay:
                    pos_y += 1
                    last_move_time = current_time
                    
                    # Reset position if reached bottom
                    if pos_y > 16:  # 16 = 20-4 (board height - max shape height)
                        pos_y = 0
                        pos_x = 3
                
                # Draw current tetris shape
                draw_tetris_shape(board_canvas, tetris_shapes[current_shape_key], current_rotation, pos_x, pos_y)
                
                # Combine board and webcam feed
                combined_frame = combine_board_and_webcam(board_canvas, processed_frame)
                
                # Display information
                cv2.putText(combined_frame, f"Shape: {current_shape_key}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(combined_frame, f"FPS: {avg_fps:.1f}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Display the combined frame
                cv2.imshow('Motion Tetris', combined_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('a') and pos_x > 0:
                    pos_x -= 1
                elif key == ord('d') and pos_x < 6:
                    pos_x += 1
                elif key == ord('w'):
                    current_rotation = (current_rotation + 1) % len(tetris_shapes[current_shape_key]['shape'])
                elif key == ord(' '):  # Space bar to change shape
                    shape_index = (shape_index + 1) % len(shape_keys)
                    current_shape_key = shape_keys[shape_index]
                    current_rotation = 0
                
                # Add small delay to control frame rate and CPU usage
                time.sleep(0.01)
                
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