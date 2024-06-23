import time

import cv2
import pyzbar.pyzbar as pyzbar


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Невозможно открыть камеру")

while True:
    ret, frame = cap.read()
    cv2.imshow("Камера", frame)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    decode_object = pyzbar.decode(gray)
    for obj in decode_object:
        data = obj.data.decode('utf-8')
        print("QR CODE Считан")
        print(data)
        points = obj.polygon
        if len(points) > 4:
            pt1 = (points[0].x, points[0].y)
            pt2 = (points[1].x, points[1].y)
            pt3 = (points[2].x, points[2].y)
            pt4 = (points[3].x, points[3].y)
            cv2.line(frame, pt1, pt2, (255, 0, 0), 3)
            cv2.line(frame, pt2, pt3, (255, 0, 0), 3)
            cv2.line(frame, pt3, pt4, (255, 0, 0), 3)
            cv2.line(frame, pt4, pt1, (255, 0, 0), 3)
        else:
            cv2.line(frame, (points[0].x, points[0].y),
                     (points[1].x, points[1].y),(255, 0, 0), 3)
            cv2.line(frame, (points[1].x, points[1].y),
                     (points[2].x, points[2].y), (255, 0, 0), 3)
            cv2.line(frame, (points[2].x, points[2].y),
                     (points[3].x, points[3].y), (255, 0, 0), 3)
            cv2.line(frame, (points[3].x, points[3].y),
                     (points[0].x, points[0].y), (255, 0, 0), 3)
            # cv2.imshow("QR обработан", frame)
            time.sleep(5)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
