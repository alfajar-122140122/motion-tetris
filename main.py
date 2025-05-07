import cv2

def read_frame(cap):
    """Read a frame from the webcam and return it"""
    ret, frame = cap.read()
    if not ret:
        return None
    return frame

def setup_webcam(device_id=0, width=640, height=480):
    """Set up and initialize the webcam with specified dimensions"""
    cap = cv2.VideoCapture(device_id)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return None
    
    # Set the frame width and height
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    # Verify the settings took effect
    actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"Webcam opened successfully. Resolution: {actual_width}x{actual_height}")
    
    return cap

def main():
    # A 640x480 resolution works well for most webcam-based games
    webcam = setup_webcam(width=640, height=480)
    
    if webcam is not None:
        print("Press 'q' to quit.")
        while True:
            frame = read_frame(webcam)
            if frame is None:
                print("Error: Failed to capture image.")
                break
                
            # Display the frame
            cv2.imshow('Motion Tetris', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Release resources
        webcam.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()