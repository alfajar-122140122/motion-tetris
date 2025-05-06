import cv2

def main():
    # Open the default webcam (usually 0)
    cap = cv2.VideoCapture(0)
    
    # Check if the webcam was successfully opened
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    
    print("Webcam opened successfully. Press 'q' to quit.")
    
    # Loop to continuously capture frames
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        # If frame is not properly captured, break
        if not ret:
            print("Error: Failed to capture image.")
            break
        
        # Display the frame
        cv2.imshow('Webcam', frame)
        
        # Check for user input to exit (press 'q')
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()