import cv2 as cv
import numpy as np
import face_recognition as face_id
import os


purple_color = (255, 0, 255)

imageBill = face_id.load_image_file('data/test/me/11.png')
imageBill = cv.cvtColor(imageBill, cv.COLOR_BGR2RGB)

BASE_DIR = os.path.basename(os.path.dirname(os.path.__file__))

print(BASE_DIR)
# imageBillTest = face_id.load_image_file('data/test/mock/real.jpeg')
# imageBillTest = face_id.load_image_file('data/test/mock/gates_cut.png')
# imageBillTest = face_id.load_image_file('data/test/mock/gates.jpg')
# imageBillTest = face_id.load_image_file('data/test/mock/young_gates.jpg')
# imageBillTest = face_id.load_image_file('data/test/mock/young_gates2.jpg')

# imageBillTest = face_id.load_image_file('data/test/me/10.jpg')
# imageBillTest = face_id.load_image_file('data/test/me/11.png')
imageBillTest = face_id.load_image_file('data/test/me/12.png')
imageBillTest = cv.cvtColor(imageBillTest, cv.COLOR_BGR2RGB)

faceLoc = face_id.face_locations(imageBill)[0]
faceEncode = face_id.face_encodings(imageBill)[0]
cv.rectangle(imageBill, (faceLoc[3], faceLoc[0], faceLoc[2], faceLoc[1]), purple_color, 2)

faceLocTest = face_id.face_locations(imageBillTest)[0]
faceEncodeTest = face_id.face_encodings(imageBillTest)[0]
cv.rectangle(imageBillTest, (faceLocTest[3], faceLocTest[0], faceLocTest[2], faceLocTest[1]), purple_color, 2)


results = face_id.compare_faces([faceEncode], faceEncodeTest)
distance = face_id.face_distance([faceEncode], faceEncodeTest)
print(results, "  distance :  ", distance)

cv.imshow('frame', imageBill)
cv.imshow('frame_2', imageBillTest)
cv.waitKey(0)
# camera = cv2.videocaptureAll(0)

