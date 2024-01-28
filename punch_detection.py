import cv2
import mediapipe as mp
import time

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

webcam = cv2.VideoCapture(0)
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
previous_distance = 1
previous_time = time.time()

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
        for hand_landmark in res:
            distance = min(distance, hand_landmark.landmark[8].z)
            mp_drawing.draw_landmarks(img, hand_landmark, connections=mp_hands.HAND_CONNECTIONS)

        distance_ratio = distance / previous_distance  # distance is logarithmic or smth its weird

        current_time = time.time()
        dt = current_time - previous_time

        img = cv2.putText(img, 'distance: ' + str(int(1000 * distance) / 1000.0), (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                  1, (0, 0, 255), 2, cv2.LINE_AA)
        isPunching = distance_ratio > 2
        img = cv2.putText(img, 'Ratio: ' + str(distance_ratio), (50, 100), cv2.FONT_HERSHEY_SIMPLEX,
                                  1, (0, 0, 255), 2, cv2.LINE_AA)
        img = cv2.putText(img, 'Punching: ' + str(isPunching), (50, 150), cv2.FONT_HERSHEY_SIMPLEX,
                                  1, (0, 0, 255), 2, cv2.LINE_AA)

        previous_time = current_time
        previous_distance = distance

    cv2.imshow('Koolac', img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
webcam.release()
cv2.destroyAllWindows()
