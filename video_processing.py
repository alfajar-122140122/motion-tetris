import cv2
import numpy as np
from config import BOARD_WIDTH, BOARD_HEIGHT, CELL_SIZE, SHAPE_COLORS

def read_frame(cap):
    """Read a frame from the webcam and return it"""
    ret, frame = cap.read()
    if not ret:
        return None
    frame = cv2.flip(frame, 1)
    return frame

def setup_webcam(device_id=0, width=640, height=480):
    """Set up and initialize the webcam with specified dimensions"""
    cap = cv2.VideoCapture(device_id)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return None
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, 60)
    actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Webcam opened successfully. Resolution: {actual_width}x{actual_height}, FPS: {actual_fps}")
    return cap

def draw_tetris_board(game_board):
    """Draw the Tetris board on a new canvas, including placed pieces"""
    board_canvas = np.zeros((BOARD_HEIGHT * CELL_SIZE, BOARD_WIDTH * CELL_SIZE, 3), dtype=np.uint8)
    board_canvas[:] = (30, 30, 30)  # Dark gray background

    for r in range(BOARD_HEIGHT):
        for c in range(BOARD_WIDTH):
            cell_value = game_board[r][c]
            if cell_value != 0:
                color = SHAPE_COLORS.get(cell_value, (128, 128, 128))
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = (c + 1) * CELL_SIZE, (r + 1) * CELL_SIZE
                cv2.rectangle(board_canvas, (x1, y1), (x2, y2), color, -1)
                cv2.rectangle(board_canvas, (x1, y1), (x2, y2), (180, 180, 180), 1)

    for i in range(BOARD_HEIGHT + 1):
        cv2.line(board_canvas, (0, i * CELL_SIZE), (BOARD_WIDTH * CELL_SIZE, i * CELL_SIZE), (50, 50, 50), 1)
    for j in range(BOARD_WIDTH + 1):
        cv2.line(board_canvas, (j * CELL_SIZE, 0), (j * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE), (50, 50, 50), 1)

    cv2.rectangle(board_canvas, (0, 0), (BOARD_WIDTH * CELL_SIZE - 1, BOARD_HEIGHT * CELL_SIZE - 1), (100, 100, 100), 2)
    return board_canvas

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
                cv2.rectangle(board_canvas, (x1, y1), (x2, y2), color, -1)
                cv2.rectangle(board_canvas, (x1, y1), (x2, y2), (180, 180, 180), 1)

def combine_board_and_webcam(board_canvas, webcam_frame):
    """Combine the Tetris board and webcam feed side by side"""
    board_height = board_canvas.shape[0]
    webcam_height = webcam_frame.shape[0]
    scale = board_height / webcam_height
    new_width = int(webcam_frame.shape[1] * scale)
    webcam_resized = cv2.resize(webcam_frame, (new_width, board_height))
    combined = np.hstack((board_canvas, webcam_resized))
    return combined

def overlay_tetris_on_webcam(webcam_frame, board_canvas, alpha=0.7):
    """Overlay Tetris board on the webcam feed with transparency"""
    webcam_height, webcam_width = webcam_frame.shape[:2]
    board_height, board_width = board_canvas.shape[:2]
    scale_factor = (webcam_height * 0.8) / board_height
    target_width = int(board_width * scale_factor)
    target_height = int(board_height * scale_factor)
    board_resized = cv2.resize(board_canvas, (target_width, target_height))

    x_offset = (webcam_width - target_width) // 2
    y_offset = (webcam_height - target_height) // 2

    result = webcam_frame.copy()
    gray_board = cv2.cvtColor(board_resized, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray_board, 30, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)

    roi = result[y_offset:y_offset+target_height, x_offset:x_offset+target_width]
    board_fg = cv2.bitwise_and(board_resized, board_resized, mask=mask)
    webcam_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
    combined_roi = cv2.addWeighted(board_fg, alpha, webcam_bg, 1.0, 0)

    result[y_offset:y_offset+target_height, x_offset:x_offset+target_width] = combined_roi
    cv2.rectangle(result,
                 (x_offset, y_offset),
                 (x_offset + target_width, y_offset + target_height),
                 (255, 255, 255), 2)
    return result
