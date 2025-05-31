# Game constants
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_SIZE = 40

# Shape colors (BGR values)
SHAPE_COLORS = {
    0: (30, 30, 30),    # Background for empty cells
    1: (255, 255, 0),   # I - Cyan
    2: (255, 0, 0),     # J - Blue
    3: (255, 165, 0),   # L - Orange
    4: (0, 255, 255),   # O - Yellow
    5: (0, 255, 0),     # S - Green
    6: (128, 0, 128),   # T - Purple
    7: (0, 0, 255)      # Z - Red
}

# Gesture detection constants
CLAP_THRESHOLD = 150  # pixels
PINCH_THRESHOLD = 0.05  # Distance threshold for pinch gesture
ROTATION_RECOGNITION_DELAY = 0.6  # Delay between rotation gesture recognitions (increased for better control)
FIST_THRESHOLD = 0.6  # Threshold for fist gesture detection

# Game timing
DEFAULT_MOVE_DELAY = 0.5  # Delay between automatic downward movements
GESTURE_COOLDOWN = 0.3  # Delay between gesture recognitions
ROTATION_DELAY = 0.5  # Delay between rotation actions (increased for better positioning control)
HARD_DROP_SPEED_MULTIPLIER = 3.0  # Speed multiplier for hard drop (3x faster)
HARD_DROP_DELAY = DEFAULT_MOVE_DELAY / HARD_DROP_SPEED_MULTIPLIER  # Calculated delay for hard drop

# Sound file paths
BGM_PATH = "sfx/bgm.mp3"
CLEAR_ROW_SOUND_PATH = "sfx/clearRow.mp3"
DEFAULT_MUSIC_VOLUME = 0.3 # Default music volume (0.0 to 1.0)

# Video recording constants
VIDEO_OUTPUT_DIRECTORY = "game_recordings"
OUTPUT_VIDEO_FILENAME = "tetris_gameplay.avi"
VIDEO_FOURCC = "XVID" # Codec for AVI file, common and widely supported
