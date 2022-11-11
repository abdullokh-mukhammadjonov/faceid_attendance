import cv2 as cv
import numpy as np
import face_recognition as face_id
import os
import pkg.helpers as helper


PURPLE_COLOR = (255, 0, 255)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "data/test/actual")
TEST_IMAGE_DIR = os.path.join(BASE_DIR, "data/test/mock")
COLOR_WHITE = (255, 255, 255)
COLOR_LIGHT_GREEN = (0, 255, 0)
COLOR_RED = (0, 0, 255)
RECTANELE_STROKE = 2

imageBill = face_id.load_image_file(IMAGE_DIR + '/jack.png')
imageBill = cv.cvtColor(imageBill, cv.COLOR_BGR2RGB)

knownPeople, labels = helper.get_images_and_labels(IMAGE_DIR)
encodings = helper.get_encodings(knownPeople)
print(" --  Encoding complete -- ")


cap = cv.VideoCapture(0)
while True:
    success, frame = cap.read() # capture each frame
    frame = cv.flip(frame, 180) # flip 180 degrees
    camera_picture = cv.resize(frame, (0, 0), None, 0.8, 0.8)
    colored_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB) # get greyscale copy of frame image
    colored_frame = cv.resize(colored_frame, (0, 0), None, 0.25, 0.25)
    
    frame_faces = face_id.face_locations(colored_frame) # get all faces in the current frame
    frame_face_encodings = face_id.face_encodings(colored_frame, frame_faces) # get face encodings
    
    for face_encode, face_location in zip(frame_face_encodings, frame_faces):
        matches = face_id.compare_faces(encodings, face_encode)
        distance = face_id.face_distance(encodings, face_encode)
        best_match_index = np.argmin(distance)
        y1, x2, y2, x1 = face_location
        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
        print(y1, x2, y2, x1)
        if matches[best_match_index]:
            match_name = labels[best_match_index]
            
            cv.rectangle(frame, (x1, y1), (x2, y2), COLOR_LIGHT_GREEN, RECTANELE_STROKE)
            cv.rectangle(frame, (x1, y2-40), (x2, y2), COLOR_LIGHT_GREEN, cv.FILLED)
            cv.putText(frame,  f'{match_name} {round(distance[best_match_index], 2)}', (x1+6, y2-6), cv.FONT_HERSHEY_COMPLEX, 1, COLOR_WHITE, 2)
        else:
            cv.rectangle(frame, (x1, y1), (x2, y2), COLOR_RED, RECTANELE_STROKE)
            
        scaled_img = cv.resize(frame, (x1, y1), interpolation=cv.INTER_CUBIC)
        cv.imwrite("picture.jpg", scaled_img)

    cv.imshow('frame1', camera_picture) # image show
    if cv.waitKey(20) & 0xFF == ord('q'):
        break
    if cv.waitKey(20) & 0xFF == ord('t'):
        cv.imwrite("picture11.jpg", camera_picture[50, 50])
    
cap.release()
cv.destroyAllWindows()

# print(labels)            


    # faces = face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5)
    
    # for (x, y, w, h) in faces:
    #     # print(x, y, w, h)
    #     roigray = gray[y:y+h, x:x+w]
    #     # roicolor = frame[y:y+h, x:x+w]
    #     image_path = "that.png"
    #     image_path_2 = "that_color.png"
    #     print(roigray)
    #     cv2.imwrite(image_path, roigray)
    #     # cv2.imwrite(image_path_2, roicolor)
        
    #     color = (255, 0, 0)
    #     stroke = 3
        
    #     width = x + w
    #     height = y + h
    #     cv2.rectangle(frame, (x, y), (width, height), color, stroke)

    # cv2.imshow('frame1', frame) # image show
    # cv2.imshow('frame2', gray) # image show
    # if cv2.waitKey(20) & 0xFF == ord('q'):
    #     break