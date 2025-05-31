"""
Motion Tetris Game Configuration
==============================
Configuration file containing all constants and settings for the Motion Tetris game.
Organized by functional area for better maintainability.
"""

# =============================================================================
# GAME BOARD CONSTANTS
# =============================================================================

BOARD_WIDTH = 10                    # Width of the Tetris game board (in cells)
BOARD_HEIGHT = 20                   # Height of the Tetris game board (in cells)
CELL_SIZE = 40                      # Size of each cell in pixels

# =============================================================================
# TETRIS SHAPE COLORS (BGR FORMAT)
# =============================================================================

SHAPE_COLORS = {
    0: (30, 30, 30),                # Background (dark gray)
    1: (255, 255, 0),               # I-piece (cyan)
    2: (255, 0, 0),                 # J-piece (blue) 
    3: (255, 165, 0),               # L-piece (orange)
    4: (0, 255, 255),               # O-piece (yellow)
    5: (0, 255, 0),                 # S-piece (green)
    6: (128, 0, 128),               # T-piece (purple)
    7: (0, 0, 255)                  # Z-piece (red)
}

# =============================================================================
# GESTURE DETECTION THRESHOLDS
# =============================================================================

# Basic Detection
FIST_THRESHOLD = 0.6                # Threshold for fist detection curl
PINCH_THRESHOLD = 0.05              # Distance threshold for pinch  
PINCH_DISTANCE_THRESHOLD = 0.1      # Max thumb-index distance for pinch
HAND_WIDTH_MIN = 0.1                # Minimum hand width for front view

# Raised Hand
RAISED_HAND_HEIGHT = 0.15           # Required height above wrist for raise
HEIGHT_DIFF_THRESHOLD = 0.15        # Max height difference for pinch
FINGER_CURL_MIN = 0.05              # Min finger curl for fist

# Gesture Timing
CLAP_COOLDOWN = 0.5                 # Cooldown between clap detections (seconds)
ROTATION_RECOGNITION_DELAY = 0.6    # Delay between rotations (seconds)
GESTURE_COOLDOWN = 0.3              # General gesture cooldown (seconds)

# =============================================================================
# GAME TIMING PARAMETERS  
# =============================================================================

DEFAULT_MOVE_DELAY = 0.5            # Auto-drop delay (seconds)
ROTATION_DELAY = 0.5                # Delay between rotations
HARD_DROP_SPEED_MULTIPLIER = 3.0    # Speed multiplier for hard drop
HARD_DROP_DELAY = DEFAULT_MOVE_DELAY / HARD_DROP_SPEED_MULTIPLIER

# =============================================================================
# AUDIO SETTINGS
# =============================================================================

BGM_PATH = "sfx/bgm.mp3"            # Background music file
CLEAR_ROW_SOUND_PATH = "sfx/clearRow.mp3"  # Line clear sound
DEFAULT_MUSIC_VOLUME = 0.3          # Music volume (0.0 to 1.0)

# =============================================================================
# VIDEO RECORDING SETTINGS
# =============================================================================

VIDEO_OUTPUT_DIRECTORY = "game_recordings"     
OUTPUT_VIDEO_FILENAME = "tetris_gameplay.avi"  
VIDEO_FOURCC = "XVID"                         # Video codec for AVI

# =============================================================================
# DISPLAY SETTINGS
# =============================================================================

OVERLAY_ALPHA = 0.6                 # Transparency for board overlay
DEBUG_INFO_FONT_SIZE = 0.5          # Font size for debug info
INSTRUCTION_FONT_SIZE = 0.4         # Font size for instructions
SCORE_FONT_SIZE = 0.7              # Font size for score display
