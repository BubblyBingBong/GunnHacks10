import cv2
import threading
        

class FaceDetectionThread(threading.Thread):
    def __init__(self, camera_index=0, enable_camera_display=False):
        super(FaceDetectionThread, self).__init__()
        self.camera_index = camera_index
        self.initial_face_position = (0, 0)
        self.face_position = (0, 0)
        self.enable_camera_display = enable_camera_display
        self.lock = threading.Lock()
        self.stop_event = threading.Event()

    def run(self):
        # Create a VideoCapture object to capture video from the camera
        cap = cv2.VideoCapture(self.camera_index)

        # Load the pre-trained Haar Cascade classifier for upper body detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        while not self.stop_event.is_set():
            # Read a frame from the camera
            ret, frame = cap.read()

            # Convert the frame to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces in the frame
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

            # Find the largest face
            largest_face = max(faces, key=lambda rect: rect[2] * rect[3], default=None)

            # Update face position
            with self.lock:
                if largest_face is not None:
                    x, y, w, h = largest_face
                    frame_height, frame_width = frame.shape[:2]
                    normalized_x = (x + w / 2) / frame_width
                    normalized_y = (y + h / 2) / frame_height
                    self.face_position = (normalized_x, normalized_y)
                else:
                    self.face_position = (0, 0)

            # Display the resulting frame
            if self.enable_camera_display:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.imshow('Detection', frame)

            # Break the loop if the 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the VideoCapture
        cap.release()
        cv2.destroyAllWindows()

    def stop(self):
        self.stop_event.set()
        self.join()
        
    def get_face_position(self):
        with self.lock:
            return self.face_position
        
    def reset_initial_position(self):
        while self.initial_face_position == (0, 0):
            self.initial_face_position = self.face_position
        
    def get_face_x_offset(self):
        with self.lock:
            if self.face_position == (0, 0):
                return 0
            
            return self.initial_face_position[0] - self.face_position[0]


if __name__ == "__main__":
    # Set the camera index (0 by default for the default camera)
    camera_index = 0

    # Create an instance of DetectionThread
    face_detection_thread = FaceDetectionThread(camera_index, True)

    try:
        # Start the face detection thread
        face_detection_thread.start()
        face_detection_thread.reset_initial_position()

        while True:
            # Get the face position from the thread
            face_offset = face_detection_thread.get_face_x_offset()
            print(f"Offset: {int(face_offset * 100)}")

    except KeyboardInterrupt:
        # Stop the face detection thread on keyboard interrupt
        face_detection_thread.stop()
