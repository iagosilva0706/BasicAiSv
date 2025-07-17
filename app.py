
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
import numpy as np
import tensorflow as tf
import os
import uuid

# Download model if not present
if not os.path.exists('model.h5'):
    os.system("wget https://your-cloud-storage-link/model.h5 -O model.h5")

# Load model once
model = tf.keras.models.load_model('model.h5')

# Initialize FastAPI
app = FastAPI()

@app.post("/signature-verify/")
def signature_verify(signature_image: UploadFile = File(...), database_image: UploadFile = File(...)):
    temp_sig = save_temp_file(signature_image)
    temp_db = save_temp_file(database_image)

    score = predict_similarity(temp_sig, temp_db)

    if score >= 0.9:
        result = "match"
        explanation = "The signatures are highly similar. High confidence match."
    elif score >= 0.7:
        result = "similar"
        explanation = "The signatures show moderate similarity. Potential match with some variations."
    else:
        result = "no_match"
        explanation = "The signatures do not sufficiently match. Possible fraud or mismatch."

    return JSONResponse({
        "score": round(float(score) * 100, 2),
        "result": result,
        "verification": explanation
    })

def save_temp_file(file: UploadFile):
    temp_filename = f"/tmp/{uuid.uuid4()}.png"
    with open(temp_filename, "wb") as f:
        f.write(file.file.read())
    return temp_filename

def preprocess(image_path):
    image = Image.open(image_path).convert('L')
    image = image.resize((220, 155))
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=(0, -1))
    return image

def predict_similarity(image1_path, image2_path):
    img1 = preprocess(image1_path)
    img2 = preprocess(image2_path)
    prediction = model.predict([img1, img2])
    return float(prediction[0][0])
