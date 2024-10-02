# -*- coding: utf-8 -*-
"""Dog vs Cat Classification.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/110U5JIXIRHuF9YAlfdLOnTfi9Q0oyqGr
"""

!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

!kaggle competitions download -c dogs-vs-cats

from zipfile import ZipFile
dataset = '/content/dogs-vs-cats.zip'

with ZipFile(dataset,'r') as zip:
  zip.extractall()
  print('The dataset is extracted')

from zipfile import ZipFile
dataset = '/content/train.zip'

with ZipFile(dataset,'r') as zip:
  zip.extractall()
  print('The dataset is extracted')

import os
path, dirs, files = next(os.walk('/content/train'))
file_count = len(files)
print('Number of images',file_count)

file_names = os.listdir('/content/train/')
print(file_names)

len(file_names)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
from sklearn.model_selection import train_test_split
from google.colab.patches import cv2_imshow

img = mpimg.imread('/content/train/cat.2590.jpg')
img_plt =  plt.imshow(img)
plt.show()

img = mpimg.imread('/content/train/dog.8593.jpg')
img_plt = plt.imshow(img)
plt.show()

"""**Counting no of dogs and cats**"""

file_names = os.listdir('/content/train/')

dog_count = 0
cat_count = 0

for file in (file_names):
    name = file[0:3]

    if name == 'dog':
        dog_count +=1
    else:
        cat_count +=1

print('Number of dogs',dog_count)
print('Number of cats',cat_count)

os.mkdir('/content/image resized/')

"""**Resizing Images**"""

original_folder = '/content/train/'
resized_folder  = '/content/image resized/'


for i in range(2000):
     filename = os.listdir(original_folder)[i]
     img_path = original_folder + filename

     img = Image.open(img_path)
     img = img.resize((224,224))
     img = img.convert('RGB')


     newImgPath = resized_folder + filename
     img.save(newImgPath)

"""**Creating labels for cats(0) and dogs(1)**"""

filenames = os.listdir('/content/image resized/')

labels = []

for i in range(2000):
    filename = filenames[i]

    if filename[0:3] == 'dog':
       labels.append(1)
    else:
       labels.append(0)

print(labels[0:10])
print(len(filenames))

print(filenames[0:10])

values,counts = np.unique(labels,return_counts = True)
print(values)
print(counts)

"""**Coverting all resized images to numpy array**"""

import cv2
import glob

image_directory = '/content/image resized/'
image_extensions = ['png','jpg']

files = []

[files.extend(glob.glob(image_directory + '*.' + e )) for e in image_extensions]

dog_cat_images = np.asarray([cv2.imread(file) for file in files])

for i in range(5):
  print(files[i])
type(files)

print(dog_cat_images)

type(dog_cat_images)
print(dog_cat_images.shape)

"""**Train Test Split**"""

X = dog_cat_images

Y = np.asarray(labels)

X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size=0.2,random_state = 3)

print(X.shape,X_train.shape,X_test.shape)

"""**Scaling the dataset**"""

X_train_scaled = X_train/255
X_test_scaled  = X_test/255

print(X_train_scaled)

"""**Building Neural Network**"""

import tensorflow as tf
import tensorflow_hub as hub
from tensorflow import keras

#!pip install --upgrade tensorflow==2.11.0 tensorflow-hub keras==2.11.0

print(tf.__version__)
print(hub.__version__)

mobilenet_model = 'https://tfhub.dev/google/tf2-preview/mobilenet_v2/feature_vector/4'

# Load the pre-trained model from TensorFlow Hub
pretrained_model = hub.KerasLayer(mobilenet_model, input_shape=(224, 224, 3), trainable=False)

num_of_classes = 2

# Build the model using Sequential API
model = keras.Sequential([
                           pretrained_model,
                           keras.layers.Dense(num_of_classes, activation='softmax') ])


model.summary()

model.compile(
              optimizer = 'adam',
              loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits = True),
              metrics = ['acc']
)

model.fit( X_train_scaled, Y_train, epochs = 5 )

score, accuracy = model.evaluate(X_test_scaled,Y_test)
print('Test Loss',score)
print('Test Accuracy',accuracy)

input_image_path = input()
input_image = cv2.imread(input_image_path)
cv2_imshow(input_image)

input_image_resize = cv2.resize(input_image,(224,224))

input_image_scaled = input_image_resize/255

input_image_reshaped = np.reshape(input_image_scaled,[1,224,224,3])

input_prediction = model.predict(input_image_reshaped)

input_pred_label = np.argmax(input_prediction)

if input_pred_label == 0:
  print('The image is a cat')
else:
  print('The image is a dog')

