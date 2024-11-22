import cv2
import pytesseract
import re
from flask import Flask, request, jsonify
import os
import tempfile

app = Flask(__name__)

# Function to extract text from image using OCR
def extract_text_from_image(image_path):
    image = cv2.imread(image_path)
    text = pytesseract.image_to_string(image)
    print("OCR Result:\n", text)  # Print OCR result to terminal
    return text

# Function to extract name and ID number using regex
def extract_info(ocr_text):
    id_pattern = r'(\d{3}-\d{4}-\d{7}-\d{1})'
    name_pattern = r'Name[:\s]*([A-Za-z\s]+(?:\s[A-Za-z\s]+)*)'

    extracted_name = None
    extracted_id = None

    lines = ocr_text.split('\n')

    for line in lines:
        name_match = re.search(name_pattern, line)
        if name_match:
            extracted_name = name_match.group(1).strip()
        
        id_match = re.search(id_pattern, line)
        if id_match:
            extracted_id = id_match.group(1).strip()

    return extracted_name, extracted_id

@app.route('/extract', methods=['POST'])
def extract_info_api():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided.'}), 400

    image_file = request.files['image']

    # Create a temporary file to save the image
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        temp_file.write(image_file.read())
        temp_file_path = temp_file.name  # Get the name of the temp file

    try:
        ocr_result = extract_text_from_image(temp_file_path)
        extracted_name, extracted_id = extract_info(ocr_result)
    finally:
        # Clean up the temporary image file
        os.remove(temp_file_path)

    return jsonify({
        'name': extracted_name,
        'id_number': extracted_id
    })

if __name__ == "__main__":
    app.run(port=3001)