# 
# 
# LATEST PUNCH DETECTION CODE AS OF 2:48 AM
#
# the isPunching variable is true when punching and false when resting
#
# 

import math
import cv2
import mediapipe as mp
import time

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

webcam = cv2.VideoCapture(0)
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
previous_diag = 1

while webcam.isOpened():
    success, img = webcam.read()

    # hand tracking
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (640, 400))

    results = hands.process(img)

    # draw annotations
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
            diag = max(diag, math.sqrt((max_x - min_x) * (max_y - min_y))) # use the largest fist
            mp_drawing.draw_landmarks(img, hand_landmark, connections=mp_hands.HAND_CONNECTIONS)

        diag_ratio = diag / previous_diag # distance is logarithmic or smth its weird

        img = cv2.putText(img, 'diag: ' + str(int(1000 * diag) / 1000.0), (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                          1, (0, 0, 255), 2, cv2.LINE_AA)
        img = cv2.putText(img, 'ratio: ' + str(diag_ratio), (50, 100), cv2.FONT_HERSHEY_SIMPLEX,
                          1, (0, 0, 255), 2, cv2.LINE_AA)
        isPunching = diag_ratio > 1.3 # setting larger values will require punches with more force to register
        img = cv2.putText(img, 'Punching: ' + str(isPunching), (50, 150), cv2.FONT_HERSHEY_SIMPLEX,
                          1, (0, 0, 255), 2, cv2.LINE_AA)

        previous_diag = diag

    cv2.imshow('stream', img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
webcam.release()
cv2.destroyAllWindows()