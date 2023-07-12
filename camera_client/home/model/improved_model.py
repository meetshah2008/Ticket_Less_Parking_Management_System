# Works exactly for N100

import os
import cv2
import numpy as np
import pandas as pd
import tensorflow as tf
import pytesseract as pt
import plotly.express as px
import matplotlib.pyplot as plt
import xml.etree.ElementTree as xet
import re
import easyocr

from glob import glob
from skimage import io
from shutil import copy
from keras.models import Model
from keras.callbacks import TensorBoard
from sklearn.model_selection import train_test_split
from keras.applications import InceptionResNetV2
from keras.layers import Dense, Dropout, Flatten, Input
# from keras.preprocessing.image import load_img, img_to_array
from PIL import Image

from keras.utils import load_img, img_to_array

def enlarge_plt_display(image, scale_factor):
    width = int(image.shape[1] * scale_factor / 100)
    height = int(image.shape[0] * scale_factor / 100)
    dim = (width, height)
    plt.figure(figsize = dim)
    plt.axis('off') 
    plt.imshow(image)

    cv2.imwrite("result.png", image)

def carplate_extract(image, carplate_haar_cascade):
    
    carplate_rects = carplate_haar_cascade.detectMultiScale(image,scaleFactor=1.1, minNeighbors=5) 

    for x,y,w,h in carplate_rects: 
        carplate_img_extract = image[y+15:y+h-10 ,x+15:x+w-20] 
        
    return carplate_img_extract

def enlarge_img(image, scale_percent):
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized_image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
    return resized_image



def object_detection(model, input_image):
    
    im = Image.fromarray(input_image)
    im.save("temp.jpeg")

    image = load_img("temp.jpeg") # PIL object
    image = np.array(image,dtype=np.uint8) # 8 bit array (0,255)
    image1 = load_img("temp.jpeg",target_size=(224,224))

    # Read image
    # image = load_img(path) # PIL object
    # print(input_image.shape, "shape type", type(input_image))
    # image = np.array(input_image,dtype=np.uint8) # 8 bit array (0,255)
    # # image1 = load_img(path,target_size=(224,224))
    # image1 = Image.fromarray(input_image)
    # image1.resize((244, 244))
    # print(image1.shape, "shape type", type(image1))
    # image1 = cv2.reshape(input_image, (244, 244), interpolation=cv2.INTER_LINEAR)
    
    # Data preprocessing
    image_arr_224 = img_to_array(image1)/255.0 # Convert to array & normalized
    h,w,d = image.shape
    test_arr = image_arr_224.reshape(1,224,224,3)
    
    # Make predictions
    coords = model.predict(test_arr)
    
    # Denormalize the values
    denorm = np.array([w,w,h,h])
    coords = coords * denorm
    coords = coords.astype(np.int32)
    
    # Draw bounding on top the image
    xmin, xmax,ymin,ymax = coords[0]
    pt1 =(xmin,ymin)
    pt2 =(xmax,ymax)
    print(pt1, pt2)
    cv2.rectangle(image,pt1,pt2,(0,255,0),3)
    return image, coords


def recognition(input_image):

    model = tf.keras.models.load_model('/home/matrix/Documents/camera_client/home/model/object_detection.h5')
    print('Model loaded Sucessfully')

    image, cods = object_detection(model, input_image)
    fig = px.imshow(image)
    fig.update_layout(width=700, height=500, margin=dict(l=10, r=10, b=10, t=10),xaxis_title='Figure 14')

    # img = np.array(load_img(path))
    xmin ,xmax,ymin,ymax = cods[0]
    roi = input_image[ymin:ymax,xmin:xmax]
    fig = px.imshow(roi)
    fig.update_layout(width=350, height=250, margin=dict(l=10, r=10, b=10, t=10),xaxis_title='Figure 15 Cropped image')

    carplate_extract_img = enlarge_img(roi, 150)
    carplate_extract_img_gray = cv2.cvtColor(carplate_extract_img, cv2.COLOR_RGB2GRAY)
    carplate_extract_img_gray_blur = cv2.medianBlur(carplate_extract_img_gray,3) # Kernel size 3

    # text = pt.image_to_string(carplate_extract_img_gray_blur)
    # print(text)

    reader = easyocr.Reader(['en'])
    text = reader.readtext(carplate_extract_img_gray_blur)
    print(text)

    finalText = ""

    for i in text:
        finalText += i[1]

    return finalText