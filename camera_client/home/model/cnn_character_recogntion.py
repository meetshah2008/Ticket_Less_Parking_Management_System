import tensorflow as tf
from tensorflow import keras
from keras.models import model_from_json
import cv2
import numpy as np


def load_keras_model(model_name):
    # Load json and create model
    json_file = open('home/model/model_LicensePlate.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    # Load weights into new model
    model.load_weights("home/model/model_LicensePlate.h5")
    return model


def get_characters(char):

    pre_trained_model = load_keras_model('model_LicensePlate')

    def fix_dimension(img):
        new_img = np.zeros((28,28,3))
        for i in range(3):
            new_img[:,:,i] = img 
        return new_img
    
    def show_results():
        dic = {}
        characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for i,c in enumerate(characters):
            dic[i] = c

        output = []
        for i,ch in enumerate(char): #iterating over the characters
            img_ = cv2.resize(ch, (28,28), interpolation=cv2.INTER_AREA)
            img = fix_dimension(img_)
            img = img.reshape(1,28,28,3) #preparing image for the model

            # y_ = pre_trained_model.predict_classes(img)[0] #predicting the class
            # y_ = (pre_trained_model.predict(img) > 0.5).astype("int32")[0]

            predict_x=pre_trained_model.predict(img) 
            y_=np.argmax(predict_x,axis=1)

            print("y_ : ", y_)
            y_ = y_[0]
            print("y_ : ", y_)

            character = dic[y_] #
            output.append(character) #storing the result in a list
            
        plate_number = ''.join(output)
        
        return plate_number
    
    return show_results()