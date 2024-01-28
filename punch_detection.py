import math
import cv2
import mediapipe as mp
import threading
from camera import FrameCapturer

class HandPunchDetector:
    def __init__(self, frame_capturer:FrameCapturer, debug=False):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.frame_capturer = frame_capturer
        self.hands = self.mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.previous_diag = 1
        self.is_punching = False
        self.running = False
        self.debug = debug

    def start(self):
        self.running = True
        threading.Thread(target=self._run).start()

    def stop(self):
        self.running = False
        cv2.destroyAllWindows()

    def _run(self):
        while self.running:
            print(self.is_punching)
            frame = self.frame_capturer.get_frame()

            # hand tracking
            try:
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (640, 400))
            except:
                continue

            results = self.hands.process(img)

            # draw annotations (only if debug is True)
            if self.debug:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                res = results.multi_hand_landmarks
                if res:
                    distance = 99999
                    diag = -1
                    for hand_landmark in res:
                        distance = min(distance, hand_landmark.landmark[8].z)
                        min_x = 999999
                        min_y = 999999
                        max_x = -999999
                        max_y = -999999
                        for lm in hand_landmark.landmark:
                            min_x = min(min_x, lm.x)
                            max_x = max(max_x, lm.x)
                            min_y = min(min_y, lm.y)
                            max_y = max(max_y, lm.y)
                        diag = max(diag, math.sqrt((max_x - min_x) * (max_y - min_y)))
                        self.mp_drawing.draw_landmarks(img, hand_landmark, connections=self.mp_hands.HAND_CONNECTIONS)

                    diag_ratio = diag / self.previous_diag

                    img = cv2.putText(img, 'diag: ' + str(int(1000 * diag) / 1000.0), (50, 50),
                                      cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                    img = cv2.putText(img, 'ratio: ' + str(diag_ratio), (50, 100),
                                      cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                    self.is_punching = diag_ratio > 1.3
                    img = cv2.putText(img, 'Punching: ' + str(self.is_punching), (50, 150),
                                      cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                    self.previous_diag = diag

                cv2.imshow('stream', img)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.stop()

if __name__ == "__main__":
    try:
        frame_capturer = FrameCapturer()
        hand_detector = HandPunchDetector(frame_capturer=frame_capturer, debug=True)
        hand_detector.start()
        while True:
            print(hand_detector.is_punching)
            
    except KeyboardInterrupt:
        hand_detector.stop()
        frame_capturer.stop()