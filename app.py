import os
import requests
from flask import Flask, request, render_template
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set up the upload folder and API credentials
UPLOAD_FOLDER = 'uploads'
API_URL = 'https://api.ocr.space/parse/image'  # Replace with your actual API endpoint
API_KEY = os.getenv('OCR_API_KEY')  # Get API key from environment variable

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html', result=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('index.html', result='No file part')

    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', result='No selected file')

    # Save the uploaded file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Call the OCR API
    with open(file_path, 'rb') as f:
        response = requests.post(API_URL, files={'file': f}, data={'apikey': API_KEY})

    # Check the response
    if response.status_code == 200:
        data = response.json()
        # Handle cases where no text is found
        if 'ParsedResults' in data and len(data['ParsedResults']) > 0:
            result_text = data['ParsedResults'][0]['ParsedText']
            return render_template('index.html', result=result_text)
        else:
            return render_template('index.html', result='No text found in the image.')
    else:
        return render_template('index.html', result='Error: ' + response.text)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
