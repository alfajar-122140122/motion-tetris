import numpy as np
from config import BOARD_WIDTH, BOARD_HEIGHT

def create_tetris_board():
    """Create an empty Tetris board using the defined dimensions"""
    board = np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=int)
    return board

def is_valid_position(board, shape_details, rotation_idx, piece_x, piece_y):
    """Check if the piece is in a valid position on the board."""
    shape_array = shape_details['shape'][rotation_idx]
    for r_shape in range(4):
        for c_shape in range(4):
            if shape_array[r_shape][c_shape] != 0:
                board_r, board_c = piece_y + r_shape, piece_x + c_shape
                if not (0 <= board_c < BOARD_WIDTH and 0 <= board_r < BOARD_HEIGHT):
                    return False
                if board[board_r][board_c] != 0:
                    return False
    return True

def add_piece_to_board(board, shape_details, rotation_idx, piece_x, piece_y):
    """Add the landed piece to the game board."""
    shape_array = shape_details['shape'][rotation_idx]
    for r_shape in range(4):
        for c_shape in range(4):
            if shape_array[r_shape][c_shape] != 0:
                board_r, board_c = piece_y + r_shape, piece_x + c_shape
                if 0 <= board_r < BOARD_HEIGHT and 0 <= board_c < BOARD_WIDTH:
                    board[board_r][board_c] = shape_array[r_shape][c_shape]

def clear_full_rows(board):
    """Clear full rows and return the number of lines cleared."""
    lines_cleared = 0
    row_idx = BOARD_HEIGHT - 1
    while row_idx >= 0:
        if np.all(board[row_idx] != 0):
            lines_cleared += 1
            for r in range(row_idx, 0, -1):
                board[r] = board[r-1].copy()
            board[0] = np.zeros(BOARD_WIDTH, dtype=int)
        else:
            row_idx -= 1
    return lines_cleared

def calculate_score(lines_cleared_this_turn):
    """Calculate score based on lines cleared."""
    if lines_cleared_this_turn == 1:
        return 100
    elif lines_cleared_this_turn == 2:
        return 300
    elif lines_cleared_this_turn == 3:
        return 500
    elif lines_cleared_this_turn >= 4:
        return 800
    return 0

def create_tetris_shapes():
    """Create all Tetris shapes (tetrominoes) and their rotations"""
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
    O_SHAPE = [
        np.array([[0, 4, 4, 0],
                 [0, 4, 4, 0],
                 [0, 0, 0, 0],
                 [0, 0, 0, 0]])
    ]
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
