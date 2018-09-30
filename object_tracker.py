from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
 
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

# greenLower = (21, 88, 127)
# greenUpper = (167, 177, 255)
greenLower = (0, 0, 0)
greenUpper = (20, 20, 20)
# greenLower = (10, 1, 151)
# greenUpper = (41, 66, 199)
pts = deque(maxlen=args["buffer"])
 
if not args.get("video", False):
	vs = VideoStream(src=0).start()
else:
	vs = cv2.VideoCapture(args["video"])

time.sleep(2.0)
# fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
# fgbg = cv2.createBackgroundSubtractorMOG2(500, 16, True)
fgbg = cv2.createBackgroundSubtractorKNN(500, 400, True)
while True:
	frame = vs.read()
	frame = frame[1] if args.get("video", False) else frame
	if frame is None:
		break
 
	# resize image for higher fps
	frame = imutils.resize(frame, width=600)
	# blur the frame to reduce high frequency noise
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	# apply background subtractor
	mask = fgbg.apply(blurred)
	# filter gray shadow
	mask = cv2.inRange(mask, 200, 255)
	# mask = cv2.erode(mask, None, iterations=2)
	# mask = cv2.dilate(mask, None, iterations=2)

	# contour
	contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	contours = contours[0] if imutils.is_cv2() else contours[1]
	center = None
	if len(contours) > 0:
		c = max(contours, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		if radius > 10 and radius < 20:
			if M["m00"] > 0:
				center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
			center = (int(x), int(y))
			cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)
	pts.appendleft(center)

	# Draw trails
	# for i in range(1, len(pts)):
	# 	if pts[i - 1] is None or pts[i] is None:
	# 		continue
	# 	thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
	# 	cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	if key == ord("q"):
		break

if not args.get("video", False):
	vs.stop()
else:
	vs.release()
 
cv2.destroyAllWindows()