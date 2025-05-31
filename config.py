"""
Motion Tetris Game Configuration
==============================
Configuration file containing all constants and settings for the Motion Tetris game.
This includes board dimensions, colors, gesture detection thresholds, timing parameters,
sound settings, and video recording configurations.
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
    0: (30, 30, 30),                # Background for empty cells (dark gray)
    1: (255, 255, 0),               # I-piece - Cyan
    2: (255, 0, 0),                 # J-piece - Blue
    3: (255, 165, 0),               # L-piece - Orange
    4: (0, 255, 255),               # O-piece - Yellow
    5: (0, 255, 0),                 # S-piece - Green
    6: (128, 0, 128),               # T-piece - Purple
    7: (0, 0, 255)                  # Z-piece - Red
}

# =============================================================================
# GESTURE DETECTION CONSTANTS
# =============================================================================

CLAP_THRESHOLD = 150                # Distance threshold for clap detection (pixels)
PINCH_THRESHOLD = 0.05              # Distance threshold for pinch gesture
FIST_THRESHOLD = 0.6                # Threshold for fist gesture detection
ROTATION_RECOGNITION_DELAY = 0.6    # Delay between rotation gesture recognitions (seconds)
CLAP_DISTANCE_THRESHOLD = 0.2       # Threshold for hands being close together (normalized)
CLAP_COOLDOWN = 0.5                # Minimum seconds between clap detections
CLAP_MIN_VELOCITY = 0.3            # Minimum velocity for clap motion detection

# =============================================================================
# GAME TIMING PARAMETERS
# =============================================================================

DEFAULT_MOVE_DELAY = 0.5            # Delay between automatic downward movements (seconds)
GESTURE_COOLDOWN = 0.3              # Delay between gesture recognitions (seconds)
ROTATION_DELAY = 0.5                # Delay between rotation actions (seconds)
HARD_DROP_SPEED_MULTIPLIER = 3.0    # Speed multiplier for hard drop (3x faster)
HARD_DROP_DELAY = DEFAULT_MOVE_DELAY / HARD_DROP_SPEED_MULTIPLIER  # Calculated delay for hard drop

# =============================================================================
# AUDIO SETTINGS
# =============================================================================

BGM_PATH = "sfx/bgm.mp3"            # Path to background music file
CLEAR_ROW_SOUND_PATH = "sfx/clearRow.mp3"  # Path to line clear sound effect
DEFAULT_MUSIC_VOLUME = 0.3          # Default music volume (0.0 to 1.0)

# =============================================================================
# VIDEO RECORDING SETTINGS
# =============================================================================

VIDEO_OUTPUT_DIRECTORY = "game_recordings"     # Directory for saving game recordings
OUTPUT_VIDEO_FILENAME = "tetris_gameplay.avi"  # Default filename for video output
VIDEO_FOURCC = "XVID"                          # Video codec (XVID for AVI format)
