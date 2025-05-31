"""
Motion Tetris - Game Logic Module
=================================
This module handles the core Tetris game mechanics including:
- Board creation and management
- Tetromino shapes and rotations
- Collision detection and validation
- Line clearing and scoring system
- Piece placement logic

Contains all the classic Tetris tetrominoes (I, J, L, O, S, T, Z) with proper
rotation matrices and collision detection algorithms.

Author: Motion Tetris Team
Version: 1.0
"""

import numpy as np
from config import BOARD_WIDTH, BOARD_HEIGHT

# =============================================================================
# BOARD MANAGEMENT
# =============================================================================

def create_tetris_board():
    """
    Create an empty Tetris board using the defined dimensions.
    
    Returns:
        numpy.ndarray: Empty board matrix with zeros
    """
    board = np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=int)
    return board

# =============================================================================
# COLLISION DETECTION AND VALIDATION
# =============================================================================

def is_valid_position(board, shape_details, rotation_idx, piece_x, piece_y):
    """
    Check if the piece is in a valid position on the board.
    
    Args:
        board: Current game board state
        shape_details: Dictionary containing shape data
        rotation_idx: Current rotation index
        piece_x: X position of the piece
        piece_y: Y position of the piece
        
    Returns:
        bool: True if position is valid, False otherwise
    """
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

# =============================================================================
# PIECE PLACEMENT AND BOARD OPERATIONS
# =============================================================================

def add_piece_to_board(board, shape_details, rotation_idx, piece_x, piece_y):
    """
    Add the landed piece to the game board.
    
    Args:
        board: Current game board state
        shape_details: Dictionary containing shape data
        rotation_idx: Current rotation index
        piece_x: X position of the piece
        piece_y: Y position of the piece
    """
    shape_array = shape_details['shape'][rotation_idx]
    for r_shape in range(4):
        for c_shape in range(4):
            if shape_array[r_shape][c_shape] != 0:
                board_r, board_c = piece_y + r_shape, piece_x + c_shape
                if 0 <= board_r < BOARD_HEIGHT and 0 <= board_c < BOARD_WIDTH:
                    board[board_r][board_c] = shape_array[r_shape][c_shape]

def clear_full_rows(board):
    """
    Clear full rows and return the number of lines cleared.
    
    Args:
        board: Current game board state
        
    Returns:
        int: Number of lines cleared
    """
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

# =============================================================================
# SCORING SYSTEM
# =============================================================================

def calculate_score(lines_cleared_this_turn):
    """
    Calculate score based on lines cleared.
    
    Args:
        lines_cleared_this_turn: Number of lines cleared in current turn
        
    Returns:
        int: Score points awarded
    """
    
    if lines_cleared_this_turn == 1:
        return 100
    elif lines_cleared_this_turn == 2:
        return 300
    elif lines_cleared_this_turn == 3:
        return 500
    elif lines_cleared_this_turn >= 4:
        return 800
    return 0

# =============================================================================
# TETROMINO SHAPES AND ROTATIONS
# =============================================================================

def create_tetris_shapes():
    """
    Create all Tetris shapes (tetrominoes) and their rotations.
    
    Returns:
        dict: Dictionary containing all tetromino shapes with their rotations and colors
              Each shape includes:
              - 'shape': List of rotation matrices (4x4 numpy arrays)
              - 'color': RGB color tuple for visualization
    """
    # I-Shape (Line piece) - 2 rotations
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
    
    # J-Shape (J piece) - 4 rotations
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
    
    # L-Shape (L piece) - 4 rotations
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
    
    # O-Shape (Square piece) - 1 rotation (same in all orientations)
    O_SHAPE = [
        np.array([[0, 4, 4, 0],
                 [0, 4, 4, 0],
                 [0, 0, 0, 0],
                 [0, 0, 0, 0]])
    ]
    
    # S-Shape (S piece) - 2 rotations
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
    
    # T-Shape (T piece) - 4 rotations
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
    
    # Z-Shape (Z piece) - 2 rotations
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
    
    # Return dictionary with all shapes and their associated colors
    return {
        'I': {'shape': I_SHAPE, 'color': (255, 255, 0)},   # Cyan
        'J': {'shape': J_SHAPE, 'color': (255, 0, 0)},     # Blue
        'L': {'shape': L_SHAPE, 'color': (255, 165, 0)},   # Orange
        'O': {'shape': O_SHAPE, 'color': (0, 255, 255)},   # Yellow
        'S': {'shape': S_SHAPE, 'color': (0, 255, 0)},     # Green
        'T': {'shape': T_SHAPE, 'color': (128, 0, 128)},   # Purple
        'Z': {'shape': Z_SHAPE, 'color': (0, 0, 255)}      # Red
    }
