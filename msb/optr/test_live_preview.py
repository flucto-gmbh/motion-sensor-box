import cv2
import picamera2

cam = picamera2.Picamera2()
cam.start()
cv2.startWindowThread()
cv2.namedWindow("preview")
while True:
    img = cam.capture_array()
    cv2.imshow("img", img)
