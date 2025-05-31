"""
Motion Tetris - Video Processing Module
======================================
This module handles all video-related operations for the Motion Tetris game including:
- Webcam setup and frame capture
- Video recording and output
- Tetris board rendering and visualization
- Frame combination and overlay effects
- Real-time video processing for gesture recognition

Provides functions for drawing the game board, combining webcam feed with game visuals,
and managing video recording functionality.

Author: Motion Tetris Team
Version: 1.0
"""

import cv2
import numpy as np
from config import BOARD_WIDTH, BOARD_HEIGHT, CELL_SIZE, SHAPE_COLORS, VIDEO_FOURCC, OUTPUT_VIDEO_FILENAME

# =============================================================================
# WEBCAM SETUP AND CAPTURE
# =============================================================================

def read_frame(cap):
    """
    Read a frame from the webcam and return it.
    
    Args:
        cap: OpenCV VideoCapture object
        
    Returns:
        numpy.ndarray or None: Captured frame (horizontally flipped) or None if failed
    """
    ret, frame = cap.read()
    if not ret:
        return None
    frame = cv2.flip(frame, 1)  # Horizontal flip for mirror effect
    return frame

def setup_webcam(device_id=0, width=640, height=480):
    """
    Set up and initialize the webcam with specified dimensions.
    
    Args:
        device_id (int): Camera device ID (default: 0)
        width (int): Desired frame width (default: 640)
        height (int): Desired frame height (default: 480)
        
    Returns:
        cv2.VideoCapture or None: Configured webcam object or None if failed
    """
    cap = cv2.VideoCapture(device_id)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return None
    
    # Set webcam properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, 60)
    
    # Verify actual settings
    actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Webcam opened successfully. Resolution: {actual_width}x{actual_height}, FPS: {actual_fps}")
    return cap

# =============================================================================
# VIDEO RECORDING
# =============================================================================

def setup_video_writer(output_filename, fourcc_str, fps, frame_size):
    """
    Setup VideoWriter object to save video.
    
    Args:
        output_filename (str): Path for the output video file
        fourcc_str (str): Video codec string (e.g., 'mp4v')
        fps (int): Frames per second for video recording
        frame_size (tuple): Video frame size as (width, height)
        
    Returns:
        cv2.VideoWriter or None: Configured video writer or None if failed
    """
    fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
    writer = cv2.VideoWriter(output_filename, fourcc, fps, frame_size)
    if not writer.isOpened():
        print(f"Error: Could not open video writer for {output_filename}")
        return None
    print(f"Video writer configured for {output_filename} at {fps} FPS, size {frame_size}")
    return writer

# =============================================================================
# TETRIS BOARD RENDERING
# =============================================================================

def draw_tetris_board(game_board):
    """
    Draw the Tetris board on a new canvas, including placed pieces.
    
    Args:
        game_board (numpy.ndarray): Current state of the game board
        
    Returns:
        numpy.ndarray: Rendered board canvas with grid and pieces
    """
    # Create canvas with dark gray background
    board_canvas = np.zeros((BOARD_HEIGHT * CELL_SIZE, BOARD_WIDTH * CELL_SIZE, 3), dtype=np.uint8)
    board_canvas[:] = (30, 30, 30)  # Dark gray background

    # Draw placed pieces
    for r in range(BOARD_HEIGHT):
        for c in range(BOARD_WIDTH):
            cell_value = game_board[r][c]
            if cell_value != 0:
                color = SHAPE_COLORS.get(cell_value, (128, 128, 128))
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = (c + 1) * CELL_SIZE, (r + 1) * CELL_SIZE
                cv2.rectangle(board_canvas, (x1, y1), (x2, y2), color, -1)
                cv2.rectangle(board_canvas, (x1, y1), (x2, y2), (180, 180, 180), 1)

    # Draw grid lines
    for i in range(BOARD_HEIGHT + 1):
        cv2.line(board_canvas, (0, i * CELL_SIZE), (BOARD_WIDTH * CELL_SIZE, i * CELL_SIZE), (50, 50, 50), 1)
    for j in range(BOARD_WIDTH + 1):
        cv2.line(board_canvas, (j * CELL_SIZE, 0), (j * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE), (50, 50, 50), 1)

    # Draw board border
    cv2.rectangle(board_canvas, (0, 0), (BOARD_WIDTH * CELL_SIZE - 1, BOARD_HEIGHT * CELL_SIZE - 1), (100, 100, 100), 2)
    return board_canvas

def draw_tetris_shape(board_canvas, shape, rotation_idx, pos_x, pos_y):
    """
    Draw a Tetris shape on the board canvas.
    
    Args:
        board_canvas (numpy.ndarray): Canvas to draw the shape on
        shape (dict): Shape dictionary containing shape arrays and color
        rotation_idx (int): Current rotation index of the shape
        pos_x (int): X position of the shape on the board
        pos_y (int): Y position of the shape on the board
    """
    shape_array = shape['shape'][rotation_idx]
    color = shape['color']

    # Draw each cell of the shape
    for i in range(4):
        for j in range(4):
            if shape_array[i][j] != 0:
                x1 = (pos_x + j) * CELL_SIZE
                y1 = (pos_y + i) * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                cv2.rectangle(board_canvas, (x1, y1), (x2, y2), color, -1)
                cv2.rectangle(board_canvas, (x1, y1), (x2, y2), (180, 180, 180), 1)

# =============================================================================
# FRAME COMBINATION AND EFFECTS
# =============================================================================

def combine_board_and_webcam(board_canvas, webcam_frame):
    """
    Combine the Tetris board and webcam feed side by side.
    
    Args:
        board_canvas (numpy.ndarray): Rendered Tetris board canvas
        webcam_frame (numpy.ndarray): Current webcam frame
        
    Returns:
        numpy.ndarray: Combined frame with board and webcam side by side
    """
    # Scale webcam frame to match board height
    board_height = board_canvas.shape[0]
    webcam_height = webcam_frame.shape[0]
    scale = board_height / webcam_height
    new_width = int(webcam_frame.shape[1] * scale)
    webcam_resized = cv2.resize(webcam_frame, (new_width, board_height))
    
    # Combine horizontally
    combined = np.hstack((board_canvas, webcam_resized))
    return combined

def overlay_tetris_on_webcam(webcam_frame, board_canvas, alpha=0.7):
    """
    Overlay Tetris board on the webcam feed with transparency.
    
    Args:
        webcam_frame (numpy.ndarray): Current webcam frame
        board_canvas (numpy.ndarray): Rendered Tetris board canvas
        alpha (float): Transparency level for the overlay (0.0 to 1.0)
        
    Returns:
        numpy.ndarray: Webcam frame with Tetris board overlaid
    """
    webcam_height, webcam_width = webcam_frame.shape[:2]
    board_height, board_width = board_canvas.shape[:2]
    
    # Calculate scaling to fit board on webcam (80% of webcam height)
    scale_factor = (webcam_height * 0.8) / board_height
    target_width = int(board_width * scale_factor)
    target_height = int(board_height * scale_factor)
    board_resized = cv2.resize(board_canvas, (target_width, target_height))

    # Center the board on the webcam frame
    x_offset = (webcam_width - target_width) // 2
    y_offset = (webcam_height - target_height) // 2

    # Create overlay mask
    result = webcam_frame.copy()
    gray_board = cv2.cvtColor(board_resized, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray_board, 30, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)

    # Apply overlay with transparency
    roi = result[y_offset:y_offset+target_height, x_offset:x_offset+target_width]
    board_fg = cv2.bitwise_and(board_resized, board_resized, mask=mask)
    webcam_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
    combined_roi = cv2.addWeighted(board_fg, alpha, webcam_bg, 1.0, 0)

    # Place the combined ROI back into the result frame
    result[y_offset:y_offset+target_height, x_offset:x_offset+target_width] = combined_roi
    
    # Draw border around the game area
    cv2.rectangle(result,
                 (x_offset, y_offset),
                 (x_offset + target_width, y_offset + target_height),
                 (255, 255, 255), 2)
    return result
