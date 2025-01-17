from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
import os

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import cv2
import time

from lime import lime_image
from skimage.segmentation import mark_boundaries
from skimage.color import gray2rgb


from torchvision import datasets, transforms

# import matplotlib.pyplot as plt
# import numpy as np
# import seaborn as sn
# from xai import preprocess_image

app = Flask(__name__)
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('nav.html')
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        filename = file.filename
        
        print('\nfile {} saved\n'.format(file.filename)) 
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 
        print(file,"----------------------------------------")
        return redirect(url_for('uploaded_file', filename=filename))

import torch
import torch.nn as nn
import torchvision.models as models
NUMBER_OF_CLASSES = 4


def load_single_image(image_path):
    # Define transformations
    t = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize((256, 256)),
    ])

    # Load and transform the image
    image = Image.open(image_path)
    image = t(image)

    return image

class ResNet50(nn.Module):
    def __init__(self, NUMBER_OF_CLASSES):
        super(ResNet50, self).__init__()
        self.resnet50 = models.resnet50(pretrained=True)
        num_ftrs = self.resnet50.fc.in_features
        self.resnet50.fc = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(num_ftrs, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, NUMBER_OF_CLASSES),
        )

    def forward(self, x):
        x = self.resnet50(x)
        return x
    
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(filepath)
    model1 = ResNet50(NUMBER_OF_CLASSES)
    # Save the trained model
    model_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resnet50_model1.pth')
    # torch.save(model, model_path)
    model1 = torch.load(model_path, map_location=torch.device('cpu'))
    # model.load_state_dict(torch.load(model_path))
    model1.eval()

    # number of classes
    input_tensor = load_single_image(filepath)
    input_batch = input_tensor.unsqueeze(0) 
    # Create an instance of the ResNet50 model
    # Run inference
    with torch.no_grad():
        class_labels = ["Cataract", "Diabetic Retinopathy", "Glaucoma", "Normal"]
        class_index = np.argmax(model1(input_batch))
        predicted_class = class_labels[class_index]
        print("##########################################################")
        print(predicted_class)
        print("##########################################################")



    model_path = os.path.join(app.config['UPLOAD_FOLDER'], 'model_resnet50.h5')
   
    model = tf.keras.models.load_model(model_path)
    explainer = lime_image.LimeImageExplainer()

    
    # Read and preprocess the image
    img = cv2.imread(filepath)
    if img is None:
        print("Error: Unable to read the image.!!!!!")
    else:
        img = preprocess_image(img)
    
    lime_explanation = generate_lime_explanation(model, img,explainer)

    fig, ax = plt.subplots(1, 2, figsize=(15, 5))

    ax[0].imshow(img[0])
    ax[0].set_title(f'Original Image')

    ax[1].imshow(lime_explanation)
    ax[1].set_title(f'LIME Explanation : {predicted_class}')

    # Save the figure
    filename_parts = filename.split('.')
    img_name = filename_parts[0] + '_xai.' + filename_parts[1]
    print(img_name)

    img_path=os.path.join(app.config['UPLOAD_FOLDER'], img_name)
    plt.savefig(img_path)  # Change the filename as needed
    plt.close()  # Close the figure to release memory
    return render_template('nav.html', filename=filename,result=predicted_class,img=img_name)



# Required function declaration


# Function to preprocess image
def preprocess_image(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    img = cv2.resize(img, (256, 256))  # Resize to match model input shape
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    img = img.astype('float32') / 255  # Normalize
    return img

def generate_lime_explanation(model, image,explainer):
    explanation = explainer.explain_instance(image[0].astype('double'), model.predict, top_labels=1, hide_color=0, num_samples=1000)
    lime_explanation, mask = explanation.get_image_and_mask(explanation.top_labels[0], positive_only=True, num_features=5, hide_rest=False)

    # Convert Lime explanation to RGB format
    lime_explanation_rgb = gray2rgb(lime_explanation)

    # Overlay Lime explanation on the original image using the mask
    marked_explanation = mark_boundaries(image[0], mask)

    return marked_explanation


# def load_single_image(image_path):
#     # Define transformations
#     t = transforms.Compose([
#         transforms.ToTensor(),
#         transforms.Resize((256, 256)),
#     ])

    # Load and transform the image
    image = Image.open(image_path)
    image = t(image)

    return image


if __name__ == '__main__':
    app.run(debug=True)
