import os
import datetime
import time
import cv2 as cv
import face_recognition as face_id
import numpy as np


def get_images_and_labels(dirname):
    images = []
    labels = []
    for root, _, files in os.walk(dirname):
        for file in files:
            if file.endswith("jpg") or file.endswith("png") or file.endswith("jpeg"):
                path = os.path.join(root, file)
                label = os.path.basename(os.path.splitext(path)[0]).replace(" ", "-").lower() 
                # label = os.path.basename(os.path.dirname(path)).replace(" ", "-").lower() # for folder based approach
                
                image = cv.imread(path)
                images.append(image)
                labels.append(label)
    return images, labels
            
def get_encodings(images):
    encodings = []
    for image in images:
        face_encode = face_id.face_encodings(image)[0]
        encodings.append(face_encode)
    return encodings


def resize_and_pad(img, size, padColor=0):

    h, w = img.shape[:2]
    sh, sw = size

    # interpolation method
    if h > sh or w > sw: # shrinking image
        interp = cv.INTER_AREA
    else: # stretching image
        interp = cv.INTER_CUBIC

    # aspect ratio of image
    aspect = w/h  # if on Python 2, you might need to cast as a float: float(w)/h

    # compute scaling and pad sizing
    if aspect > 1: # horizontal image
        new_w = sw
        new_h = np.round(new_w/aspect).astype(int)
        pad_vert = (sh-new_h)/2
        pad_top, pad_bot = np.floor(pad_vert).astype(int), np.ceil(pad_vert).astype(int)
        pad_left, pad_right = 0, 0
    elif aspect < 1: # vertical image
        new_h = sh
        new_w = np.round(new_h*aspect).astype(int)
        pad_horz = (sw-new_w)/2
        pad_left, pad_right = np.floor(pad_horz).astype(int), np.ceil(pad_horz).astype(int)
        pad_top, pad_bot = 0, 0
    else: # square image
        new_h, new_w = sh, sw
        pad_left, pad_right, pad_top, pad_bot = 0, 0, 0, 0

    # set pad color
    if len(img.shape) == 3 and not isinstance(padColor, (list, tuple, np.ndarray)): # color image but only one color provided
        padColor = [padColor]*3

    # scale and pad
    scaled_img = cv.resize(img, (new_w, new_h), interpolation=interp)
    scaled_img = cv.copyMakeBorder(scaled_img, pad_top, pad_bot, pad_left, pad_right, borderType=cv.BORDER_CONSTANT, value=padColor)

    return scaled_img

def get_date_and_time():
    curr_time = time.strftime("%H:%M:%S", time.localtime())
    curr_date = datetime.datetime.today().strftime ('%d-%b-%Y')
    return curr_date, curr_time