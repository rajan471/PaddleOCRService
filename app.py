import tensorflow as tf
import requests
import cv2
import numpy as np
import pandas as pd
from huggingface_hub import Repository
from datetime import datetime
from PIL import Image
from paddleocr import PaddleOCR
from io import BytesIO
from flask import Flask, request, jsonify
            
"""
Paddle OCR
"""
def ocr_with_paddle(img):
    finaltext = ''
    ocr = PaddleOCR(lang='en', use_angle_cls=True)
    
    # Convert PIL Image to numpy array if it's not already
    if isinstance(img, Image.Image):
        img = np.array(img)
    
    # Ensure image is in RGB format
    if len(img.shape) == 2:  # If grayscale
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    elif img.shape[2] == 4:  # If RGBA
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
    
    result = ocr.ocr(img)
    
    if result is None or len(result) == 0:
        return ''
        
    # Handle both old and new PaddleOCR versions
    first_result = result[0] if isinstance(result, list) else result
    
    for item in first_result:
        text = item[1][0] if isinstance(item, list) else item.text
        finaltext += ' ' + text
        
    return finaltext.strip()

# """
# Keras OCR
# """
# def ocr_with_keras(img):
#     output_text = ''
#     pipeline=keras_ocr.pipeline.Pipeline()
#     images=[keras_ocr.tools.read(img)]
#     predictions=pipeline.recognize(images)
#     first=predictions[0]
#     for text,box in first:
#         output_text += ' '+ text
#     return output_text

# """
# easy OCR
# """
# # gray scale image
# def get_grayscale(image):
#     return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# # Thresholding or Binarization
# def thresholding(src):
#     return cv2.threshold(src,127,255, cv2.THRESH_TOZERO)[1]
# def ocr_with_easy(img):
#     gray_scale_image=get_grayscale(img)
#     thresholding(gray_scale_image)
#     cv2.imwrite('image.png',gray_scale_image)
#     reader = easyocr.Reader(['th','en'])
#     bounds = reader.readtext('image.png',paragraph="False",detail = 0)
#     bounds = ''.join(bounds)
#     return bounds
        
# """
# Generate OCR
# """
# def generate_ocr(Method,img):
    
#     text_output = ''
#     if (img).any():
#         add_csv = []
#         image_id = 1
#         print("Method___________________",Method)
#         if Method == 'EasyOCR':
#             text_output = ocr_with_easy(img)
#         if Method == 'KerasOCR':
#             text_output = ocr_with_keras(img)
#         if Method == 'PaddleOCR':
#             text_output = ocr_with_paddle(img)
       
#         try:
#             flag(Method,text_output,img)
#         except Exception as e:
#             print(e)
#         return text_output
#     else:
#         raise gr.Error("Please upload an image!!!!")
    
#     # except Exception as e:
#     #     print("Error in ocr generation ==>",e)
#     #     text_output = "Something went wrong"
#     # return text_output
    

# """
# Create user interface for OCR demo
# """

# # image = gr.Image(shape=(300, 300))
# image = gr.Image()
# method = gr.Radio(["PaddleOCR","EasyOCR", "KerasOCR"],value="PaddleOCR")
# output = gr.Textbox(label="Output")

# demo = gr.Interface(
#     generate_ocr,
#     [method,image],
#     output,
#     title="Optical Character Recognition",
#     css=".gradio-container {background-color: lightgray} #radio_div {background-color: #FFD8B4; font-size: 40px;}",
#     article = """<p style='text-align: center;'>Feel free to give us your thoughts on this demo and please contact us at 
#                     <a href="mailto:letstalk@pragnakalp.com" target="_blank">letstalk@pragnakalp.com</a> 
#                     <p style='text-align: center;'>Developed by: <a href="https://www.pragnakalp.com" target="_blank">Pragnakalp Techlabs</a></p>"""
    

# )
# # demo.launch(enable_queue = False)
# demo.launch()


# from sentence_transformers import SentenceTransformer

app = Flask(__name__)

@app.route('/extract', methods=['POST'])
def extract():
    # Debug logging
    print("Content-Type:", request.content_type)
    print("Files:", request.files)
    print("Data:", request.data)
    print("Headers:", dict(request.headers))

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
        return jsonify({'error': 'Unsupported file format'}), 415
    
    try:
        # Read the image file
        img_bytes = file.read()
        img = Image.open(BytesIO(img_bytes))
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Process with PaddleOCR
        text = ocr_with_paddle(img)
        
        if not text:
            return jsonify({'error': 'No text detected in image'}), 422
            
        return jsonify({'text': text})
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")  # Add logging
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
