from camera import FrameCapturer
from face_detection import FaceDetectionThread
from punch_detection import HandPunchDetector

frame_capturer = FrameCapturer(camera_index=0)

hand_punch_detector = HandPunchDetector(frame_capturer=frame_capturer)
try:
    # Start the face detection thread
    hand_punch_detector.start()

except KeyboardInterrupt:
    # Stop the face detection thread on keyboard interrupt
    hand_punch_detector.stop()
    frame_capturer.stop()