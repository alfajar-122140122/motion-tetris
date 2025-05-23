import cv2
import mediapipe as mp
import numpy as np
import time

# Game constants
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_SIZE = 40

# Add SHAPE_COLORS map (ensure BGR values match those in create_tetris_shapes)
SHAPE_COLORS = {
    0: (30, 30, 30),    # Background for empty cells
    1: (255, 255, 0),   # I - Cyan
    2: (255, 0, 0),     # J - Blue
    3: (255, 165, 0),   # L - Orange (using the BGR value from create_tetris_shapes)
    4: (0, 255, 255),   # O - Yellow
    5: (0, 255, 0),     # S - Green
    6: (128, 0, 128),   # T - Purple
    7: (0, 0, 255)      # Z - Red
}

# Initialize MediaPipe Hand detection globally
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,  # Reduced from 0.7 for better performance
    min_tracking_confidence=0.3
)

BOARD_WIDTH = 10  # Width of the Tetris board
BOARD_HEIGHT = 20  # Height of the Tetris board

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

def is_valid_position(board, shape_details, rotation_idx, piece_x, piece_y):
    """Check if the piece is in a valid position on the board."""
    shape_array = shape_details['shape'][rotation_idx]
    for r_shape in range(4):
        for c_shape in range(4):
            if shape_array[r_shape][c_shape] != 0:  # If this is part of the piece
                board_r, board_c = piece_y + r_shape, piece_x + c_shape
                
                # Check bounds
                if not (0 <= board_c < BOARD_WIDTH and 0 <= board_r < BOARD_HEIGHT):
                    return False  # Out of bounds
                
                # Check collision with existing pieces on the board
                # (Ensure board_r is within board height before accessing board[board_r])
                if board[board_r][board_c] != 0:  # Collision with another piece
                    return False
    return True

def add_piece_to_board(board, shape_details, rotation_idx, piece_x, piece_y):
    """Add the landed piece to the game board."""
    shape_array = shape_details['shape'][rotation_idx]
    for r_shape in range(4):
        for c_shape in range(4):
            if shape_array[r_shape][c_shape] != 0:
                board_r, board_c = piece_y + r_shape, piece_x + c_shape
                # Check bounds before writing, though is_valid_position should prevent issues
                if 0 <= board_r < BOARD_HEIGHT and 0 <= board_c < BOARD_WIDTH:
                    board[board_r][board_c] = shape_array[r_shape][c_shape]

def clear_full_rows(board):
    """Clear full rows and return the number of lines cleared."""
    lines_cleared = 0
    row_idx = BOARD_HEIGHT - 1
    while row_idx >= 0:
        if np.all(board[row_idx] != 0):  # If all cells in the row are non-zero
            lines_cleared += 1
            # Shift rows above down
            for r in range(row_idx, 0, -1):
                board[r] = board[r-1].copy()
            board[0] = np.zeros(BOARD_WIDTH, dtype=int)  # New empty row at top
            # Don't decrement row_idx, check the same index again as content shifted
        else:
            row_idx -= 1  # Move to the row above
    return lines_cleared

def calculate_score(lines_cleared_this_turn):
    """Calculate score based on lines cleared."""
    if lines_cleared_this_turn == 1:
        return 100
    elif lines_cleared_this_turn == 2:
        return 300
    elif lines_cleared_this_turn == 3:
        return 500
    elif lines_cleared_this_turn >= 4:  # Tetris
        return 800
    return 0

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
    """Create an empty Tetris board using the defined dimensions"""
    board = np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=int)
    return board

def draw_tetris_board(game_board, shape_colors_map): # Modified
    """Draw the Tetris board on a new canvas, including placed pieces"""
    board_canvas = np.zeros((BOARD_HEIGHT * CELL_SIZE, BOARD_WIDTH * CELL_SIZE, 3), dtype=np.uint8)
    board_canvas[:] = (30, 30, 30)  # Dark gray background
    
    # Draw placed pieces from the game_board
    for r in range(BOARD_HEIGHT):
        for c in range(BOARD_WIDTH):
            cell_value = game_board[r][c]
            if cell_value != 0:  # If the cell is not empty
                color = shape_colors_map.get(cell_value, (128, 128, 128)) # Default gray
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = (c + 1) * CELL_SIZE, (r + 1) * CELL_SIZE
                cv2.rectangle(board_canvas, (x1, y1), (x2, y2), color, -1)
                cv2.rectangle(board_canvas, (x1, y1), (x2, y2), (180, 180, 180), 1) # Cell border

    # Draw grid lines
    for i in range(BOARD_HEIGHT + 1):
        cv2.line(board_canvas, (0, i * CELL_SIZE), (BOARD_WIDTH * CELL_SIZE, i * CELL_SIZE), (50, 50, 50), 1)
    for j in range(BOARD_WIDTH + 1):
        cv2.line(board_canvas, (j * CELL_SIZE, 0), (j * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE), (50, 50, 50), 1)
    
    cv2.rectangle(board_canvas, (0, 0), (BOARD_WIDTH * CELL_SIZE - 1, BOARD_HEIGHT * CELL_SIZE - 1), (100, 100, 100), 2)
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

def draw_tetris_shape(board_canvas, shape, rotation_idx, pos_x, pos_y):
    """Draw a Tetris shape on the board canvas"""
    shape_array = shape['shape'][rotation_idx]
    color = shape['color']
    
    for i in range(4):
        for j in range(4):
            if shape_array[i][j] != 0:
                x1 = (pos_x + j) * CELL_SIZE
                y1 = (pos_y + i) * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                
                # Draw filled rectangle with shape color
                cv2.rectangle(board_canvas, (x1, y1), (x2, y2), color, -1)
                # Draw border
                cv2.rectangle(board_canvas, (x1, y1), (x2, y2), (180, 180, 180), 1)

def overlay_tetris_on_webcam(webcam_frame, board_canvas, alpha=0.7):
    """Overlay Tetris board on the webcam feed with transparency"""
    # Calculate the target size while maintaining aspect ratio
    webcam_height, webcam_width = webcam_frame.shape[:2]
    board_height, board_width = board_canvas.shape[:2]
    
    # Calculate scaling to make board height 80% of webcam height
    scale_factor = (webcam_height * 0.8) / board_height
    target_width = int(board_width * scale_factor)
    target_height = int(board_height * scale_factor)
    
    # Resize board canvas to target size
    board_resized = cv2.resize(board_canvas, (target_width, target_height))
    
    # Calculate position to center the board
    x_offset = (webcam_width - target_width) // 2
    y_offset = (webcam_height - target_height) // 2
    
    # Create an output frame starting with the webcam frame
    result = webcam_frame.copy()
    
    # Create a mask for non-black parts of the board
    gray_board = cv2.cvtColor(board_resized, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray_board, 30, 255, cv2.THRESH_BINARY)
    
    # Create inverted mask for the webcam background
    mask_inv = cv2.bitwise_not(mask)
    
    # Extract the ROI from the webcam frame
    roi = result[y_offset:y_offset+target_height, x_offset:x_offset+target_width]
    
    # Create the foreground and background
    board_fg = cv2.bitwise_and(board_resized, board_resized, mask=mask)
    webcam_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
    
    # Combine foreground and background
    combined_roi = cv2.addWeighted(board_fg, alpha, webcam_bg, 1.0, 0)
    
    # Copy the combined ROI back to the result frame
    result[y_offset:y_offset+target_height, x_offset:x_offset+target_width] = combined_roi
    
    # Draw a border around the board
    cv2.rectangle(result, 
                 (x_offset, y_offset), 
                 (x_offset + target_width, y_offset + target_height),
                 (255, 255, 255), 2)
    
    return result

# The get_shape_width function is no longer needed if using is_valid_position
# def get_shape_width(shape, rotation_idx):
#     """Calculate the actual width of a shape in its current rotation"""
#     shape_array = shape['shape'][rotation_idx]
#     width = 0
#     for col in range(4):
#         if any(shape_array[row][col] != 0 for row in range(4)):
#             width += 1
#     return width

def main():
    webcam = None
    prev_time = 0
    fps_values = []
    tetris_board = create_tetris_board()
    tetris_shapes_data = create_tetris_shapes() # Renamed for clarity
    
    # Game state variables
    score = 0
    lines_cleared_total = 0
    game_over = False

    shape_keys = list(tetris_shapes_data.keys())
    shape_index = 0 # Or import random; shape_index = random.randrange(len(shape_keys))
    current_shape_key = shape_keys[shape_index]
    current_rotation = 0
    pos_x, pos_y = BOARD_WIDTH // 2 - 2, 0 # Start piece in middle-ish top
    
    # Game timing variables
    last_move_time = time.time()
    move_delay = 0.5  # Delay between automatic downward movements
    gesture_delay = 0.3  # Delay between gesture recognition
    last_gesture_time = time.time()
    
    overlay_mode = False
    
    try:
        webcam = setup_webcam(width=640, height=480)
        
        if webcam is not None:
            print("Press 'q' to quit, 'r' to restart. Gestures or a/d/w for controls.")
            while True: # Main loop, game_over state will be checked inside
                current_time = time.time()
                fps = 1 / (current_time - prev_time) if (current_time - prev_time) > 0 else 0
                prev_time = current_time
                fps_values.append(fps)
                
                if len(fps_values) > 30:
                    fps_values.pop(0)
                avg_fps = sum(fps_values) / len(fps_values) if fps_values else 0
                
                frame = read_frame(webcam)
                if frame is None:
                    print("Error: Failed to capture image.")
                    break
                
                processed_frame, gesture = detect_hand_gesture(frame)
                board_canvas = draw_tetris_board(tetris_board, SHAPE_COLORS)
                
                if not game_over:
                    # Handle gestures with delay
                    if current_time - last_gesture_time > gesture_delay:
                        next_pos_x, next_rotation = pos_x, current_rotation
                        if gesture == "left":
                            next_pos_x = pos_x - 1
                        elif gesture == "right":
                            next_pos_x = pos_x + 1
                        elif gesture == "rotate":
                            next_rotation = (current_rotation + 1) % len(tetris_shapes_data[current_shape_key]['shape'])
                        
                        if (gesture == "left" or gesture == "right") and is_valid_position(tetris_board, tetris_shapes_data[current_shape_key], current_rotation, next_pos_x, pos_y):
                            pos_x = next_pos_x
                            last_gesture_time = current_time
                        elif gesture == "rotate" and is_valid_position(tetris_board, tetris_shapes_data[current_shape_key], next_rotation, pos_x, pos_y):
                            current_rotation = next_rotation
                            last_gesture_time = current_time
                
                    # Automatic downward movement
                    if current_time - last_move_time > move_delay:
                        if is_valid_position(tetris_board, tetris_shapes_data[current_shape_key], current_rotation, pos_x, pos_y + 1):
                            pos_y += 1
                        else: # Piece lands
                            add_piece_to_board(tetris_board, tetris_shapes_data[current_shape_key], current_rotation, pos_x, pos_y)
                            lines_cleared_now = clear_full_rows(tetris_board)
                            if lines_cleared_now > 0:
                                lines_cleared_total += lines_cleared_now
                                score += calculate_score(lines_cleared_now)
                            
                            # Spawn new piece
                            # import random # if you want random pieces
                            # shape_index = random.randrange(len(shape_keys))
                            shape_index = (shape_index + 1) % len(shape_keys)
                            current_shape_key = shape_keys[shape_index]
                            current_rotation = 0
                            pos_x = BOARD_WIDTH // 2 - 2
                            pos_y = 0
                            
                            if not is_valid_position(tetris_board, tetris_shapes_data[current_shape_key], current_rotation, pos_x, pos_y):
                                game_over = True
                                print("Game Over!")
                        last_move_time = current_time
                    
                    # Draw current tetris shape (falling piece)
                    draw_tetris_shape(board_canvas, tetris_shapes_data[current_shape_key], current_rotation, pos_x, pos_y)

                # Combine and display
                if overlay_mode:
                    display_frame = overlay_tetris_on_webcam(processed_frame, board_canvas, alpha=0.6)
                else:
                    display_frame = combine_board_and_webcam(board_canvas, processed_frame)
                
                cv2.putText(display_frame, f"Score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(display_frame, f"Lines: {lines_cleared_total}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(display_frame, f"FPS: {avg_fps:.1f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                mode_text = "Mode: Overlay" if overlay_mode else "Mode: Side-by-side"
                cv2.putText(display_frame, mode_text, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                if game_over:
                    text_size, _ = cv2.getTextSize("Game Over!", cv2.FONT_HERSHEY_SIMPLEX, 2, 3)
                    text_x = (display_frame.shape[1] - text_size[0]) // 2
                    text_y = (display_frame.shape[0] + text_size[1]) // 2
                    cv2.putText(display_frame, "Game Over!", (text_x, text_y - 30), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)
                    cv2.putText(display_frame, f"Final Score: {score}", (text_x, text_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                    cv2.putText(display_frame, "Press 'R' to Restart or 'Q' to Quit", (text_x - 100, text_y + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2, cv2.LINE_AA)

                cv2.imshow('Motion Tetris', display_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                
                if game_over:
                    if key == ord('r'): # Restart game
                        tetris_board = create_tetris_board()
                        score = 0
                        lines_cleared_total = 0
                        game_over = False
                        shape_index = 0 
                        current_shape_key = shape_keys[shape_index]
                        current_rotation = 0
                        pos_x = BOARD_WIDTH // 2 - 2
                        pos_y = 0
                        last_move_time = time.time()
                        last_gesture_time = time.time()
                        print("Game Restarted!")
                    continue # Skip normal controls if game over

                # Keyboard input (only if not game over)
                if key == ord('a'): # Move left
                    if is_valid_position(tetris_board, tetris_shapes_data[current_shape_key], current_rotation, pos_x - 1, pos_y):
                        pos_x -= 1                
                elif key == ord('d'): # Move right
                    if is_valid_position(tetris_board, tetris_shapes_data[current_shape_key], current_rotation, pos_x + 1, pos_y):
                        pos_x += 1
                elif key == ord('w'): # Rotate
                    next_rotation = (current_rotation + 1) % len(tetris_shapes_data[current_shape_key]['shape'])
                    if is_valid_position(tetris_board, tetris_shapes_data[current_shape_key], next_rotation, pos_x, pos_y):
                        current_rotation = next_rotation
                elif key == ord('s'): # Soft drop (move down faster)
                    if is_valid_position(tetris_board, tetris_shapes_data[current_shape_key], current_rotation, pos_x, pos_y + 1):
                        pos_y += 1
                        last_move_time = current_time # Reset auto-drop timer as well
                    # else: it will land on next cycle if it can't move
                elif key == ord(' '):  # Change shape (as per original, or could be hard drop)
                    shape_index = (shape_index + 1) % len(shape_keys)
                    new_shape_key = shape_keys[shape_index]
                    # Check if the new shape can be placed at current pos_x, pos_y
                    if is_valid_position(tetris_board, tetris_shapes_data[new_shape_key], 0, pos_x, pos_y):
                        current_shape_key = new_shape_key
                        current_rotation = 0
                    # else: keep current shape or handle collision (e.g., try to adjust pos_x)
                elif key == ord('o'):
                    overlay_mode = not overlay_mode
                
                time.sleep(0.01) # Small delay
                
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Cleaning up...")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if webcam is not None:
            webcam.release()
        cv2.destroyAllWindows()
        if fps_values: # Ensure fps_values is not empty
            print(f"Final average FPS: {sum(fps_values) / len(fps_values):.1f}")
        print("Cleanup complete.")

if __name__ == "__main__":
    main()