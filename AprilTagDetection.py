import cv2
import apriltag
import numpy as np


img = cv2.imread('AprilTag2x2.jpg', cv2.IMREAD_GRAYSCALE)
detector = apriltag.Detector()
result = detector.detect(img)
print(result)

cv2.imshow('AprilTag2x2.jpg', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
