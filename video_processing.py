"""
Motion Tetris - Video Processing Module
======================================
This module handles video-related operations for Motion Tetris including:
- Webcam setup and frame capture 
- Video recording 
- Tetris board rendering and visualization
- Frame combination and overlay effects
"""

import cv2
import numpy as np
from config import (
    BOARD_WIDTH, BOARD_HEIGHT, CELL_SIZE, SHAPE_COLORS,
    VIDEO_FOURCC, OUTPUT_VIDEO_FILENAME, OVERLAY_ALPHA
)

def read_frame(cap):
    """Read and flip a frame from the webcam."""
    ret, frame = cap.read()
    if not ret:
        return None
    return cv2.flip(frame, 1)  # Horizontal flip for mirror effect

def setup_webcam(device_id=0, width=640, height=480):
    """Set up webcam with specified dimensions."""
    cap = cv2.VideoCapture(device_id)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return None
    
    # Set properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, 60)
    
    # Verify settings
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    print(f"Webcam: {actual_width}x{actual_height} @ {actual_fps}fps")
    return cap

def setup_video_writer(output_filename, fourcc_str, fps, frame_size):
    """Setup VideoWriter for game recording."""
    fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
    writer = cv2.VideoWriter(output_filename, fourcc, fps, frame_size)
    
    if not writer.isOpened():
        print(f"Error: Could not create video writer for {output_filename}")
        return None
        
    print(f"Recording to {output_filename}")
    return writer

def draw_tetris_board(game_board):
    """Draw the Tetris board with pieces and grid."""
    # Create dark gray canvas
    board_height = BOARD_HEIGHT * CELL_SIZE
    board_width = BOARD_WIDTH * CELL_SIZE
    canvas = np.zeros((board_height, board_width, 3), dtype=np.uint8)
    canvas[:] = (30, 30, 30)  # Dark gray background

    # Draw placed pieces
    for r in range(BOARD_HEIGHT):
        for c in range(BOARD_WIDTH):
            cell_value = game_board[r][c]
            if cell_value != 0:
                color = SHAPE_COLORS.get(cell_value, (128, 128, 128))
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                
                # Draw filled rectangle with border
                cv2.rectangle(canvas, (x1, y1), (x2, y2), color, -1)
                cv2.rectangle(canvas, (x1, y1), (x2, y2), (180, 180, 180), 1)

    # Draw grid
    for i in range(BOARD_HEIGHT + 1):
        y = i * CELL_SIZE
        cv2.line(canvas, (0, y), (board_width, y), (50, 50, 50), 1)
    
    for j in range(BOARD_WIDTH + 1):
        x = j * CELL_SIZE
        cv2.line(canvas, (x, 0), (x, board_height), (50, 50, 50), 1)

    # Draw border
    cv2.rectangle(canvas, (0, 0), 
                 (board_width - 1, board_height - 1),
                 (100, 100, 100), 2)
    return canvas

def draw_tetris_shape(board_canvas, shape, rotation_idx, pos_x, pos_y):
    """Draw a Tetris shape on the board canvas."""
    shape_array = shape['shape'][rotation_idx]
    color = shape['color']

    # Draw each cell
    for i in range(4):
        for j in range(4):
            if shape_array[i][j] != 0:
                x1 = (pos_x + j) * CELL_SIZE
                y1 = (pos_y + i) * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                
                # Draw filled shape cell with border
                cv2.rectangle(board_canvas, (x1, y1), (x2, y2), color, -1)
                cv2.rectangle(board_canvas, (x1, y1), (x2, y2), (180, 180, 180), 1)

def combine_board_and_webcam(board_canvas, webcam_frame):
    """Combine board and webcam feed side by side."""
    # Scale webcam to match board height
    board_height = board_canvas.shape[0]
    webcam_height = webcam_frame.shape[0]
    scale = board_height / webcam_height
    new_width = int(webcam_frame.shape[1] * scale)
    
    # Resize webcam frame
    webcam_resized = cv2.resize(webcam_frame, (new_width, board_height))
    
    # Stack horizontally
    return np.hstack((board_canvas, webcam_resized))

def overlay_tetris_on_webcam(webcam_frame, board_canvas, alpha=OVERLAY_ALPHA):
    """Overlay Tetris board on webcam feed with alpha blending."""
    webcam_height, webcam_width = webcam_frame.shape[:2]
    board_height, board_width = board_canvas.shape[:2]
    
    # Scale board to 80% of webcam height
    scale = (webcam_height * 0.8) / board_height
    target_width = int(board_width * scale)
    target_height = int(board_height * scale)
    board_resized = cv2.resize(board_canvas, (target_width, target_height))

    # Center the board
    x_offset = (webcam_width - target_width) // 2
    y_offset = (webcam_height - target_height) // 2

    # Create overlay mask
    result = webcam_frame.copy()
    gray_board = cv2.cvtColor(board_resized, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray_board, 30, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)

    # Apply overlay
    roi = result[y_offset:y_offset+target_height, 
                x_offset:x_offset+target_width]
    board_fg = cv2.bitwise_and(board_resized, board_resized, mask=mask)
    webcam_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
    combined_roi = cv2.addWeighted(board_fg, alpha, webcam_bg, 1.0, 0)
    
    # Place combined ROI and draw border
    result[y_offset:y_offset+target_height,
          x_offset:x_offset+target_width] = combined_roi
    cv2.rectangle(result,
                 (x_offset, y_offset),
                 (x_offset + target_width, y_offset + target_height),
                 (255, 255, 255), 2)
    return result
