# -*- coding: utf-8 -*-
"""Animal_Class_final.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1poiUx4FXhpaOLBnHdlcGZm1bkQWgu32b
"""

from google.colab import drive
drive.mount('/content/drive')

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import os

"""bear - 125

bird - 137

cat - 123

cow - 131

deer - 127

dog - 122

dolphin - 129

Elephant - 133

giraffe- 129

horse- 130

kangaroo - 126

lion - 131

panda - 135

tiger - 129

zebra - 137
"""

dol = os.listdir('/content/drive/MyDrive/dataset/Dolphin')
print(dol[0:100])

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

img = mpimg.imread('/content/drive/MyDrive/dataset/Dolphin/Dolphin_5.jpg')
plt.imshow(img)
plt.show()
img.shape

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet50
from tensorflow.keras import layers, models, callbacks
import tensorflow as tf

# Dataset path and classes
base_path = '/content/drive/MyDrive/dataset/'  # Update with your dataset path
classes = ["Bear", "Bird", "Cat", "Cow", "Deer", "Dog", "Dolphin", "Elephant",
           "Giraffe", "Horse", "Kangaroo", "Lion", "Panda", "Tiger", "Zebra"]

# Set up data generators for real-time data loading and augmentation
train_datagen = ImageDataGenerator(
    rescale=1.0/255,
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    validation_split=0.2  # Splits the dataset into 80% train and 20% validation
)

train_generator = train_datagen.flow_from_directory(
    directory=base_path,
    target_size=(224, 224),
    batch_size=32,
    class_mode='sparse',
    subset='training'
)

validation_generator = train_datagen.flow_from_directory(
    directory=base_path,
    target_size=(224, 224),
    batch_size=32,
    class_mode='sparse',
    subset='validation'
)

# Define the model using ResNet50 as the base
base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
for layer in base_model.layers[-10:]:  # Unfreeze the last 10 layers for fine-tuning
    layer.trainable = True

model = models.Sequential([
    base_model,
    layers.Flatten(),
    layers.BatchNormalization(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.3),
    layers.BatchNormalization(),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.3),
    layers.BatchNormalization(),
    layers.Dense(len(classes), activation='softmax')
])

# Compile the model
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Define callbacks
lr_schedule = callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6, verbose=1)
early_stopping = callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

# Train the model with the generators
history = model.fit(
    train_generator,
    validation_data=validation_generator,
    epochs=50,
    callbacks=[lr_schedule, early_stopping]
)

# Evaluate the model
loss, accuracy = model.evaluate(validation_generator)
print("Loss: ", loss)
print("Accuracy: ", accuracy)

import cv2
from google.colab.patches import cv2_imshow
import numpy as np

input_image_path = input('Path of the image to be predicted')
input_image = cv2.imread(input_image_path)
cv2_imshow(input_image)
print(input_image.shape)
image_resized = cv2.resize(input_image,(224,224))
image_resized = image_resized/255
image_reshaped = np.reshape(image_resized,[1,224,224,3])
prediction = model.predict(image_reshaped)
print(prediction)
pred_label = np.argmax(prediction)
classes = ["Bear", "Bird", "Cat", "Cow", "Deer", "Dog", "Dolphin", "Elephant",
           "Giraffe", "Horse", "Kangaroo", "Lion", "Panda", "Tiger", "Zebra"]
print('The image is recognized as',classes[pred_label])

