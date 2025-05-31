"""
Motion Tetris - Game Logic Module
==============================
Core Tetris game mechanics including:
- Board management and piece placement
- Collision detection and validation  
- Line clearing and scoring
- Tetromino shapes and rotations
"""

import numpy as np
from config import BOARD_WIDTH, BOARD_HEIGHT

def create_tetris_board():
    """Create an empty Tetris board."""
    return np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=int)

def is_valid_position(board, shape_details, rotation_idx, piece_x, piece_y):
    """
    Validate if piece can be placed at given position.
    
    Args:
        board: Current game board
        shape_details: Dictionary with shape data
        rotation_idx: Current rotation index
        piece_x, piece_y: Position to check
        
    Returns:
        bool: True if position is valid
    """
    shape_array = shape_details['shape'][rotation_idx]
    
    # Quick boundary check first
    if (piece_x < -2 or 
        piece_x > BOARD_WIDTH - 2 or
        piece_y > BOARD_HEIGHT - 2):
        return False

    # Check each cell of the piece
    for r, c in np.ndindex(4, 4):
        if shape_array[r][c] != 0:
            board_r = piece_y + r
            board_c = piece_x + c
            
            # Check board boundaries
            if not (0 <= board_c < BOARD_WIDTH and 
                   0 <= board_r < BOARD_HEIGHT):
                return False
                
            # Check collision with placed pieces
            if board[board_r][board_c] != 0:
                return False
    
    return True

def add_piece_to_board(board, shape_details, rotation_idx, piece_x, piece_y):
    """Add landed piece to the board."""
    shape_array = shape_details['shape'][rotation_idx]
    
    # Add only non-empty cells
    for r, c in np.ndindex(4, 4):
        if shape_array[r][c] != 0:
            board_r = piece_y + r
            board_c = piece_x + c
            if (0 <= board_r < BOARD_HEIGHT and 
                0 <= board_c < BOARD_WIDTH):
                board[board_r][board_c] = shape_array[r][c]

def clear_full_rows(board):
    """
    Clear completed rows and return count.
    Uses efficient numpy operations.
    """
    lines_cleared = 0
    row = BOARD_HEIGHT - 1
    
    while row >= 0:
        if np.all(board[row] != 0):  # Row is full
            lines_cleared += 1
            # Shift rows down
            board[1:row + 1] = board[0:row]
            board[0] = 0
        else:
            row -= 1
            
    return lines_cleared

def calculate_score(lines_cleared):
    """Calculate score for cleared lines."""
    score_map = {
        1: 100,   # Single
        2: 300,   # Double
        3: 500,   # Triple
        4: 800    # Tetris
    }
    return score_map.get(lines_cleared, 0)

def create_tetris_shapes():
    """
    Create Tetris shapes with rotations.
    Using numpy arrays for better memory layout.
    """
    # I-Shape (Cyan)
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
    
    # J-Shape (Blue) 
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
    
    # L-Shape (Orange)
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
    
    # O-Shape (Yellow)
    O_SHAPE = [
        np.array([[0, 4, 4, 0],
                 [0, 4, 4, 0],
                 [0, 0, 0, 0],
                 [0, 0, 0, 0]])
    ]
    
    # S-Shape (Green)
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
    
    # T-Shape (Purple)
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
    
    # Z-Shape (Red)
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
    
    # Return shape dictionary with colors
    return {
        'I': {'shape': I_SHAPE, 'color': (255, 255, 0)},    # Cyan
        'J': {'shape': J_SHAPE, 'color': (255, 0, 0)},      # Blue
        'L': {'shape': L_SHAPE, 'color': (255, 165, 0)},    # Orange
        'O': {'shape': O_SHAPE, 'color': (0, 255, 255)},    # Yellow
        'S': {'shape': S_SHAPE, 'color': (0, 255, 0)},      # Green
        'T': {'shape': T_SHAPE, 'color': (128, 0, 128)},    # Purple
        'Z': {'shape': Z_SHAPE, 'color': (0, 0, 255)}       # Red
    }
