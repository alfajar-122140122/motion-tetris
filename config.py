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

# Game timing
DEFAULT_MOVE_DELAY = 0.5  # Delay between automatic downward movements
GESTURE_COOLDOWN = 0.3  # Delay between gesture recognitions

# Sound file paths
BGM_PATH = "sfx/bgm.mp3"
CLEAR_ROW_SOUND_PATH = "sfx/clearRow.mp3"
