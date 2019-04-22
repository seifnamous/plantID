import numpy as np 
import pandas as pd 
import os, sys
import random

# Image processing
from scipy.misc import imsave, imread, imresize
from PIL import Image

# Pre-processing
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split

# Modelling
from keras.layers import Dropout, Flatten,Activation, Dense
from keras.models import model_from_json
from keras.optimizers import SGD
from keras import backend as K
from keras import applications
from keras.preprocessing.image import array_to_img, img_to_array, load_img, image

# Pickle
import pickle

# API
from flask import Flask
from flask import render_template, url_for, redirect, request, session, send_from_directory

# Bakckend
import mysql.connector

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
print(APP_ROOT)

# Predict the clas name and the likelihood of each class
def classify(imgarray, loaded_model):
    class_names = ['Daisy','Dandelion','Rose','Sunflower','Tulip']
    preds = loaded_model.predict(imgarray)
    classification = np.argmax(preds)
    final = pd.DataFrame({'Flower Type' : np.array(class_names),'Likelihood' :preds[0]})
    K.clear_session()
    return final.sort_values(by = 'Likelihood',ascending=False),class_names[classification]
    
@app.route('/')
def index():
	return render_template('home.html')

@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/upload')
def upload():
	return render_template('upload.html')

# Display results and update MySQL data base
@app.route('/predict', methods=['GET','POST'])
def predict():
	K.clear_session()
	config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'Plants'
    }
	stock = os.path.join(APP_ROOT, 'static/flowers')
	#json_file = open('model/modelFlower.json','r')
	#loaded_model_json = json_file.read()
	#json_file.close()
	#loaded_model = model_from_json(loaded_model_json)
	#loaded_model.load_weights("model/modelFlower.h5")
	
	filename = 'model/modelFlower.pkl'
	loaded_model = pickle.load(open(filename, 'rb'))
	
	print("Loaded Model from disk")
	loaded_model.compile(loss = "categorical_crossentropy", optimizer = SGD(lr=0.0001, momentum=0.9), metrics=["categorical_accuracy"])

	flopred =  request.files['flower']
	imgtest = load_img(flopred,target_size=(256,256))
	imgarray = img_to_array(imgtest)
	imgarray = imgarray/255
	imgarray = imgarray.reshape(1,imgarray.shape[0],imgarray.shape[1],imgarray.shape[2])

	filename = flopred.filename
	flowerimg = Image.open(flopred)
	new_img = flowerimg.resize((256,256))
	destination = "/".join([stock, filename])
	new_img.save(destination)
	
	final,pred_class = classify(imgarray, loaded_model)
	connection = mysql.connector.connect(**config)
	cursor = connection.cursor()
	cursor.execute("INSERT INTO flowers (file_name,type) VALUES (%s, %s)", (filename,pred_class))
	connection.commit()

	#Store model prediction results to pass to the web page
	message = "This is a: {}".format(pred_class)
	return render_template("predict.html", tables=[final.to_html(classes='data')], titles=final.columns.values, msg=message, flow=filename)

@app.route('/predict/<filename>')
def classified_image(filename):
	return send_from_directory("static/flowers", filename)

if __name__ == '__main__':
    app.run(host = '0.0.0.0',port=4000)