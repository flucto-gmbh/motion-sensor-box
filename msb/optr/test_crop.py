import cv2
import picamera2

cam = picamera2.Picamera2()
cam.configure(
    cam.create_video_configuration(main={"size": (1000, 500)})
)

cam.start()

(xmin, xmax, ymin, ymax) = (200,500,400,660)

img = cam.capture_array()
img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
img_cropped = img[xmin:xmax, ymin:ymax]
img = cv2.rectangle(img, (ymin, xmin), (ymax, xmax), (255,0,0), 2)
cv2.imshow("img", img)
cv2.imshow("img_cropped", img_cropped)
cv2.waitKey(0)
