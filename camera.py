import cv2
import threading

class FrameCapturer:
    def __init__(self, camera_index=0, debug=False):
        self.webcam = cv2.VideoCapture(camera_index)
        self.frame = None
        self.running = True
        self.debug = debug
        threading.Thread(target=self._capture_frames).start()

    def _capture_frames(self):
        while self.running:
            success, frame = self.webcam.read()
            if success:
                self.frame = frame
                if self.debug:
                    cv2.imshow('Camera Feed', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            else:
                print("Failed to capture frame.")

    def get_frame(self):
        return self.frame

    def stop(self):
        self.running = False
        self.webcam.release()
        if self.debug:
            cv2.destroyAllWindows()

if __name__ == "__main__":
    # Create an instance of FrameCapturer with debug set to True
    frame_capturer = FrameCapturer(debug=True)

    # Test capturing frames for a few seconds
    import time
    time.sleep(5)  # Capture frames for 5 seconds

    frame_capturer.stop()
