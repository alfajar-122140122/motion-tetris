import cv2
import time
import pygame
import os
import traceback

from config import (
    BOARD_WIDTH, DEFAULT_MOVE_DELAY, GESTURE_COOLDOWN,
    BGM_PATH, CLEAR_ROW_SOUND_PATH, DEFAULT_MUSIC_VOLUME,
    VIDEO_OUTPUT_DIRECTORY, OUTPUT_VIDEO_FILENAME, VIDEO_FOURCC,
    HARD_DROP_DELAY, ROTATION_DELAY, ROTATION_RECOGNITION_DELAY  # Added rotation delay constants
)
from gestures import detect_hand_gesture
from tetris_logic import (
    create_tetris_board,
    create_tetris_shapes,
    is_valid_position,
    add_piece_to_board,
    clear_full_rows,
    calculate_score
)
from video_processing import (
    read_frame,
    setup_webcam,
    draw_tetris_board,
    draw_tetris_shape,
    combine_board_and_webcam,
    overlay_tetris_on_webcam,
    setup_video_writer
)

def initialize_pygame_mixer():
    """Initializes Pygame mixer and loads sound effects."""
    pygame.mixer.init()
    try:
        pygame.mixer.music.load(BGM_PATH)
        pygame.mixer.music.set_volume(DEFAULT_MUSIC_VOLUME)
        pygame.mixer.music.play(-1)  # Play indefinitely
        print(f"BGM loaded and playing at volume: {DEFAULT_MUSIC_VOLUME}")
    except pygame.error as e:
        print(f"Warning: Could not load/play BGM '{BGM_PATH}': {e}")

    try:
        clear_sound = pygame.mixer.Sound(CLEAR_ROW_SOUND_PATH)
        print("Clear row sound loaded.")
        return clear_sound
    except pygame.error as e:
        print(f"Warning: Could not load clear row sound '{CLEAR_ROW_SOUND_PATH}': {e}")
        return None

def reset_game_state(tetris_shapes_data):
    """Resets the game state to start a new game."""
    tetris_board = create_tetris_board()
    score = 0
    lines_cleared_total = 0
    game_over = False
    shape_keys = list(tetris_shapes_data.keys())
    shape_index = 0
    current_shape_key = shape_keys[shape_index]
    current_rotation = 0
    pos_x = BOARD_WIDTH // 2 - 2
    pos_y = 0
    last_move_time = time.time()
    last_gesture_time = time.time()
    last_rotation_time = time.time()  # Added rotation delay tracking
    hard_drop_active = False  # Added hard drop state tracking
    print("Game Restarted!")
    return (
        tetris_board, score, lines_cleared_total, game_over,
        shape_keys, shape_index, current_shape_key, current_rotation,
        pos_x, pos_y, last_move_time, last_gesture_time, last_rotation_time, hard_drop_active
    )

def handle_input(key, game_state, tetris_board, tetris_shapes_data, current_time):
    """Handles keyboard input for controlling the game."""
    (pos_x, current_rotation, current_shape_key, shape_keys, shape_index,
     last_move_time, overlay_mode, pos_y, hard_drop_active, last_rotation_time) = game_state
    
    new_pos_x = pos_x
    new_current_rotation = current_rotation
    new_current_shape_key = current_shape_key
    new_shape_index = shape_index
    new_pos_y = pos_y
    new_hard_drop_active = hard_drop_active
    new_last_rotation_time = last_rotation_time

    if key == ord('a'):  # Move left
        if is_valid_position(tetris_board, tetris_shapes_data[current_shape_key], current_rotation, pos_x - 1, pos_y):
            new_pos_x = pos_x - 1
    elif key == ord('d'):  # Move right
        if is_valid_position(tetris_board, tetris_shapes_data[current_shape_key], current_rotation, pos_x + 1, pos_y):
            new_pos_x = pos_x + 1
    elif key == ord('w'):  # Rotate
        # Apply rotation delay
        if current_time - last_rotation_time > ROTATION_DELAY:
            next_rotation = (current_rotation + 1) % len(tetris_shapes_data[current_shape_key]['shape'])
            if is_valid_position(tetris_board, tetris_shapes_data[current_shape_key], next_rotation, pos_x, pos_y):
                new_current_rotation = next_rotation
                new_last_rotation_time = current_time
    elif key == ord('s'):  # Soft drop
        if is_valid_position(tetris_board, tetris_shapes_data[current_shape_key], current_rotation, pos_x, pos_y + 1):
            new_pos_y = pos_y + 1
    elif key == ord(' '):  # Hard drop (instant)
        new_pos_y = perform_instant_hard_drop(tetris_board, tetris_shapes_data, current_shape_key, current_rotation, pos_x, pos_y)
    elif key == ord('n'):  # Change shape
        new_shape_index = (shape_index + 1) % len(shape_keys)
        potential_new_shape_key = shape_keys[new_shape_index]
        if is_valid_position(tetris_board, tetris_shapes_data[potential_new_shape_key], 0, pos_x, pos_y):
            new_current_shape_key = potential_new_shape_key
            new_current_rotation = 0
        else:
            new_shape_index = shape_index
    elif key == ord('o'):
        overlay_mode = not overlay_mode

    return new_pos_x, new_current_rotation, new_current_shape_key, new_shape_index, new_pos_y, overlay_mode, new_hard_drop_active, new_last_rotation_time

def draw_game_info(display_frame, score, lines_cleared_total, avg_fps, overlay_mode, hard_drop_active):
    """Draws game information (score, lines, FPS, mode, hard drop status) on the display frame."""
    cv2.putText(display_frame, f"Score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(display_frame, f"Lines: {lines_cleared_total}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(display_frame, f"FPS: {avg_fps:.1f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    mode_text = "Mode: Overlay" if overlay_mode else "Mode: Side-by-side"
    cv2.putText(display_frame, mode_text, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Show hard drop status
    if hard_drop_active:
        cv2.putText(display_frame, "HARD DROP ACTIVE!", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

def draw_game_over_screen(display_frame, score):
    """Draws the game over screen."""
    text_size, _ = cv2.getTextSize("Game Over!", cv2.FONT_HERSHEY_SIMPLEX, 2, 3)
    text_x = (display_frame.shape[1] - text_size[0]) // 2
    text_y = (display_frame.shape[0] + text_size[1]) // 2
    cv2.putText(display_frame, "Game Over!", (text_x, text_y - 30), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)
    cv2.putText(display_frame, f"Final Score: {score}", (text_x, text_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    cv2.putText(display_frame, "Press 'R' to Restart or 'Q' to Quit", (text_x - 100, text_y + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2, cv2.LINE_AA)
    cv2.putText(display_frame, "Gesture: Fist (Genggam) = Hard Drop", (text_x - 100, text_y + 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1, cv2.LINE_AA)

def perform_instant_hard_drop(tetris_board, tetris_shapes_data, current_shape_key, current_rotation, pos_x, pos_y):
    """Drops the piece all the way down instantly until it collides with something."""
    drop_y = pos_y
    
    # Keep dropping until collision
    while is_valid_position(tetris_board, tetris_shapes_data[current_shape_key], current_rotation, pos_x, drop_y + 1):
        drop_y += 1
    
    return drop_y

def main():
    webcam = None
    video_writer = None
    prev_time = time.time()
    fps_values = []
    tetris_shapes_data = create_tetris_shapes()
    clear_row_sound = initialize_pygame_mixer()

    # Create video output directory if it doesn't exist
    if not os.path.exists(VIDEO_OUTPUT_DIRECTORY):
        os.makedirs(VIDEO_OUTPUT_DIRECTORY)
        print(f"Created directory: {VIDEO_OUTPUT_DIRECTORY}")
    
    video_file_path = os.path.join(VIDEO_OUTPUT_DIRECTORY, OUTPUT_VIDEO_FILENAME)
    
    # Initialize game state
    (
        tetris_board, score, lines_cleared_total, game_over,
        shape_keys, shape_index, current_shape_key, current_rotation,
        pos_x, pos_y, last_move_time, last_gesture_time, last_rotation_time, hard_drop_active
    ) = reset_game_state(tetris_shapes_data)

    move_delay = DEFAULT_MOVE_DELAY
    gesture_cooldown = GESTURE_COOLDOWN
    overlay_mode = False

    try:
        webcam = setup_webcam(width=640, height=480)
        if webcam is None:
            print("Failed to setup webcam. Exiting.")
            return

        print("Press 'q' to quit, 'r' to restart.")
        print("Controls: a/d/w/s for movement, space for instant hard drop, n to change shape")
        print("Gestures: left/right hand for movement, clap for rotation, fist (genggam tangan) for controlled hard drop")

        while True:
            current_time = time.time()
            delta_time = current_time - prev_time
            if delta_time > 0:
                fps = 1 / delta_time
                fps_values.append(fps)
                if len(fps_values) > 30:
                    fps_values.pop(0)
            prev_time = current_time
            avg_fps = sum(fps_values) / len(fps_values) if fps_values else 0

            frame = read_frame(webcam)
            if frame is None:
                print("Error: Failed to capture image.")
                break

            processed_frame, gesture = detect_hand_gesture(frame.copy())
            board_canvas = draw_tetris_board(tetris_board)

            if not game_over:                # Handle gesture input
                if current_time - last_gesture_time > gesture_cooldown:
                    next_pos_x_gesture, next_rotation_gesture = pos_x, current_rotation
                    gesture_moved = False
                    
                    if gesture == "left":
                        next_pos_x_gesture = pos_x - 1
                        gesture_moved = True
                        hard_drop_active = False  # Deactivate hard drop on other gestures
                    elif gesture == "right":
                        next_pos_x_gesture = pos_x + 1
                        gesture_moved = True
                        hard_drop_active = False  # Deactivate hard drop on other gestures
                    elif gesture == "rotate":
                        # Apply rotation delay for gesture too
                        if current_time - last_rotation_time > ROTATION_DELAY:
                            next_rotation_gesture = (current_rotation + 1) % len(tetris_shapes_data[current_shape_key]['shape'])
                            gesture_moved = True
                            hard_drop_active = False  # Deactivate hard drop on other gestures
                    elif gesture == "hardDrop":
                        hard_drop_active = True  # Activate controlled hard drop
                        gesture_moved = True
                    elif gesture == "none":
                        hard_drop_active = False  # Deactivate hard drop when no gesture

                    if gesture_moved:
                        if gesture == "rotate":
                            if is_valid_position(tetris_board, tetris_shapes_data[current_shape_key], next_rotation_gesture, pos_x, pos_y):
                                current_rotation = next_rotation_gesture
                                last_gesture_time = current_time
                                last_rotation_time = current_time  # Update rotation time for gesture
                        elif gesture == "hardDrop":
                            last_gesture_time = current_time
                        else:  # Left or Right
                            if is_valid_position(tetris_board, tetris_shapes_data[current_shape_key], current_rotation, next_pos_x_gesture, pos_y):
                                pos_x = next_pos_x_gesture
                                last_gesture_time = current_time

                # Determine current move delay based on hard drop state
                current_move_delay = HARD_DROP_DELAY if hard_drop_active else move_delay

                # Automatic downward movement
                if current_time - last_move_time > current_move_delay:
                    if is_valid_position(tetris_board, tetris_shapes_data[current_shape_key], current_rotation, pos_x, pos_y + 1):
                        pos_y += 1
                    else:  # Piece lands
                        add_piece_to_board(tetris_board, tetris_shapes_data[current_shape_key], current_rotation, pos_x, pos_y)
                        lines_cleared_now = clear_full_rows(tetris_board)
                        if lines_cleared_now > 0:
                            lines_cleared_total += lines_cleared_now
                            score += calculate_score(lines_cleared_now)
                            if clear_row_sound:
                                clear_row_sound.play()

                        shape_index = (shape_index + 1) % len(shape_keys)
                        current_shape_key = shape_keys[shape_index]
                        current_rotation = 0
                        pos_x = BOARD_WIDTH // 2 - 2
                        pos_y = 0
                        hard_drop_active = False  # Reset hard drop state for new piece

                        if not is_valid_position(tetris_board, tetris_shapes_data[current_shape_key], current_rotation, pos_x, pos_y):
                            game_over = True
                            print("Game Over!")
                    last_move_time = current_time

                draw_tetris_shape(board_canvas, tetris_shapes_data[current_shape_key], current_rotation, pos_x, pos_y)

            # Display logic
            if overlay_mode:
                display_frame = overlay_tetris_on_webcam(processed_frame, board_canvas, alpha=0.6)
            else:
                display_frame = combine_board_and_webcam(board_canvas, processed_frame)

            draw_game_info(display_frame, score, lines_cleared_total, avg_fps, overlay_mode, hard_drop_active)

            if game_over:
                draw_game_over_screen(display_frame, score)

            cv2.imshow('Motion Tetris', display_frame)

            # Initialize video_writer with the first display_frame's dimensions
            if video_writer is None and display_frame is not None:
                output_fps = webcam.get(cv2.CAP_PROP_FPS)
                if output_fps == 0 or output_fps > 60:
                    output_fps = 30.0
                display_frame_size = (display_frame.shape[1], display_frame.shape[0])
                video_writer = setup_video_writer(video_file_path, VIDEO_FOURCC, output_fps, display_frame_size)
                if video_writer is None:
                    print("Warning: Video recording will not be available.")

            # Write frame to video
            if video_writer is not None and display_frame is not None:
                video_writer.write(display_frame)

            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
                
            if game_over:
                if key == ord('r'):
                    (
                        tetris_board, score, lines_cleared_total, game_over,
                        shape_keys, shape_index, current_shape_key, current_rotation,
                        pos_x, pos_y, last_move_time, last_gesture_time, last_rotation_time, hard_drop_active
                    ) = reset_game_state(tetris_shapes_data)
                    if video_writer is not None:
                        video_writer.release()
                        print(f"Video segment saved to {video_file_path}. New recording will start.")
                        video_writer = None
                continue
            
            # Keyboard input (only if not game over)
            game_state_tuple = (pos_x, current_rotation, current_shape_key, shape_keys, shape_index, last_move_time, overlay_mode, pos_y, hard_drop_active, last_rotation_time)
            new_pos_x, new_current_rotation, new_current_shape_key, new_shape_index, new_pos_y, new_overlay_mode, new_hard_drop_active, new_last_rotation_time = handle_input(
                key, game_state_tuple, tetris_board, tetris_shapes_data, current_time
            )
              # Update game state based on input if changed
            if pos_x != new_pos_x or current_rotation != new_current_rotation or \
               current_shape_key != new_current_shape_key or shape_index != new_shape_index or \
               pos_y != new_pos_y or overlay_mode != new_overlay_mode or hard_drop_active != new_hard_drop_active or \
               last_rotation_time != new_last_rotation_time:

                pos_x = new_pos_x
                current_rotation = new_current_rotation
                current_shape_key = new_current_shape_key
                shape_index = new_shape_index
                overlay_mode = new_overlay_mode
                hard_drop_active = new_hard_drop_active
                last_rotation_time = new_last_rotation_time
                
                # If soft drop (s key) was pressed, update pos_y and last_move_time
                if key == ord('s') and pos_y != new_pos_y:
                    pos_y = new_pos_y
                    last_move_time = current_time
                # If instant hard drop (spacebar) was pressed, update pos_y and force landing
                elif key == ord(' ') and pos_y != new_pos_y:
                    pos_y = new_pos_y
                    last_move_time = current_time - move_delay  # Force immediate landing check

            time.sleep(0.01)  # Small delay to prevent high CPU usage

    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Cleaning up...")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        traceback.print_exc()
    finally:
        if webcam is not None:
            webcam.release()
        if video_writer is not None:
            video_writer.release()
            print(f"Video saved to {video_file_path}")
        cv2.destroyAllWindows()
        if fps_values:
            print(f"Final average FPS: {sum(fps_values) / len(fps_values):.1f}")
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.quit()
        print("Cleanup complete.")

if __name__ == "__main__":
    main()
