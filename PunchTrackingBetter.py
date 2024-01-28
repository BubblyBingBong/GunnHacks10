import math
import cv2
import mediapipe as mp
import time
import numpy as np


def hypot(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

webcam = cv2.VideoCapture(0)
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

previous_diag = 1
previous_disL = 1
previous_disR = 1
previous_time = time.time()
PUNCH_DETECTION_INTERVAL = 0.45  # seconds

hand_interval = 0
elbow_interval = 0

while webcam.isOpened():
    current_time = time.time()
    dt = current_time - previous_time
    success, img = webcam.read()

    hand_interval = max(0, hand_interval - dt)
    elbow_interval = max(0, elbow_interval - dt)

    # hand/arm tracking
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (640, 400))

    results_hand = hands.process(img)
    results_pose = pose.process(img)

    # draw stuff
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    res_hands = results_hand.multi_hand_landmarks
    res_pose = results_pose.pose_landmarks

    hand_condition = False
    elbow_condition = False

    if res_hands:
        distance = 99999
        diag = -1
        for hand_landmark in res_hands:
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
            diag = max(diag, math.sqrt((max_x - min_x) * (max_y - min_y)))  # use the largest fist
            mp_drawing.draw_landmarks(img, hand_landmark, connections=mp_hands.HAND_CONNECTIONS)

        diag_ratio = diag / previous_diag
        hand_condition = diag_ratio > 1.2  # IMPORTANT THING
        if hand_condition:
            hand_interval = PUNCH_DETECTION_INTERVAL

        previous_diag = diag

    if res_pose:
        pose_landmark = results_pose.pose_landmarks.landmark
        mp_drawing.draw_landmarks(img, results_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # get coords
        elbowL = [pose_landmark[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                  pose_landmark[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        wristL = [pose_landmark[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                  pose_landmark[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        shoulderL = [pose_landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                     pose_landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]

        elbowR = [pose_landmark[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                  pose_landmark[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        wristR = [pose_landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                  pose_landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
        shoulderR = [pose_landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                     pose_landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]

        # Calculate distances
        disL = hypot(elbowL, wristL) + hypot(shoulderL, elbowL)
        disR = hypot(elbowR, wristR) + hypot(shoulderR, elbowR)

        # arm velocity
        disL_vel = (disL - previous_disL) / dt
        disR_vel = (disR - previous_disR) / dt
        elbow_condition = disL_vel < -0.7 or disR_vel < -0.7
        if elbow_condition:
            elbow_interval = PUNCH_DETECTION_INTERVAL

        previous_disL = disL
        previous_disR = disR

    isPunching = hand_interval > 0 and elbow_interval > 0
    img = cv2.putText(img, 'Punching: ' + str(isPunching), (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                      1, (0, 0, 255), 2, cv2.LINE_AA)

    previous_time = current_time

    cv2.imshow('stream', img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
webcam.release()
cv2.destroyAllWindows()
