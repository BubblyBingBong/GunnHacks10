from camera import FrameCapturer
from face_detection import FaceDetectionThread
from punch_detection import HandPunchDetector

frame_capturer = FrameCapturer(camera_index=0, debug=False)

face_detection_thread = FaceDetectionThread(frame_capturer=frame_capturer, enable_camera_display=False)
try:
    # Start the face detection thread
    face_detection_thread.start()
    face_detection_thread.reset_initial_position()
except KeyboardInterrupt:
    # Stop the face detection thread on keyboard interrupt
    face_detection_thread.stop()

hand_punch_detector = HandPunchDetector(frame_capturer=frame_capturer, debug=False)
try:
    hand_punch_detector.start()
except KeyboardInterrupt:
    hand_punch_detector.stop()
    frame_capturer.stop()