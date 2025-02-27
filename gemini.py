import time
import os
import requests
import json
from flask import Flask, redirect, request, send_file
from google.cloud import storage

os.makedirs('files', exist_ok=True)
app = Flask(__name__)
BUCKET_NAME = "project2bucketapi"
storage_client = storage.Client()

# Set your Gemini API endpoint and key
GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyDoJe2CnZe64sbOL-GLJKWWcWrEr3Zqi28"
GEMINI_API_KEY = "AIzaSyDqR-M6RQ5iV-OUPUA5GMsAkV9pfJObyN8"


def generate_caption_and_description(image_path):
    """Invoke Gemini AI API to get the caption and description for the image."""
    with open(image_path, 'rb') as image_file:
        files = {'file': image_file}
        headers = {
            'Authorization': f'Bearer {GEMINI_API_KEY}',
        }

        response = requests.post(GEMINI_API_ENDPOINT, files=files, headers=headers)
        
        if response.status_code == 200:
            response_json = response.json()
            title = response_json.get("title", "No Title")
            description = response_json.get("description", "No Description")
            return title, description
        else:
            print(f"Error from Gemini API: {response.status_code}")
            return "Error", "Unable to generate description"


def upload_to_bucket(bucket_name, file_path, file_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_path)


@app.route('/')
def index():
    index_html = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image insert</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Style+Script&display=swap" rel="stylesheet">
    <link href="/style.css" rel="stylesheet" type="text/css" media="all">
  </head>
  <body>
    <center><h1 class="title">To Upload or Not to Upload</h1></center>

    <div class="main_box">
      <h1>Upload Images Below</h1>
      <form method="post" enctype="multipart/form-data" action="/upload">
        <div>
          <label for="file">Choose file to upload</label>
          <input type="file" id="file" name="form_file" accept="image/jpeg"/>
        </div>
        <div>
          <button>Submit</button>
        </div>
      </form>

      <h2>Uploaded Files:</h2>
      <ul>
      """  
    for file in list_files():
        index_html += f'<li><a href="./files/{file}">{file}</a></li>'

    index_html += """
    </ul>
    </div>
    <style>
    * {
      margin: 0;
      padding: 0;
    }

    li {
      list-style-type: none;
    }

    body {
      background-color: white;
    }

    .title {
      font-family: "Style Script", serif;
      font-weight: 400;
      font-style: bold;
      font-size: 50px;
      color: #ff62bf;
    }

    .main_box {
      border-radius: 5px;
      border: 5px solid #ff62bf;
      background-color: pink;
      margin: 10px 200px 0 200px;
      padding: 25px;
    }

    h1 {
      font-size: 20px;
      font-weight: bold;
    }

    .box {
      border: 1px solid black;
    }

    a {
      text-decoration: none; 
    }

    </style> 
  </body>
</html>
    """
    return index_html


@app.route('/upload', methods=["POST"])
def upload():
    if 'form_file' not in request.files:
        return "No file part", 400  # Handle missing file in request

    file = request.files['form_file']
    
    if file.filename == '':
        return "No selected file", 400  # Handle empty filename

    file_path = os.path.join("./files", file.filename)
    file.save(file_path)
    
    # Upload the image to the Google Cloud Storage bucket
    upload_to_bucket(BUCKET_NAME, file_path, file.filename)
    
    # Generate caption and description from the Gemini AI API
    title, description = generate_caption_and_description(file_path)
    
    # Create JSON response
    response_data = {
        "title": title,
        "description": description
    }
    
    # Save the JSON data to the same bucket
    json_filename = os.path.splitext(file.filename)[0] + ".json"
    json_file_path = os.path.join("./files", json_filename)
    
    with open(json_file_path, 'w') as json_file:
        json.dump(response_data, json_file)
    
    # Upload the JSON file to the same bucket
    upload_to_bucket(BUCKET_NAME, json_file_path, json_filename)
    
    return redirect("/")


@app.route('/files')
def list_files():
    files = os.listdir("./files")
    jpegs = []
    for file in files:
        if file.lower().endswith(".jpeg") or file.lower().endswith(".jpg"):
            jpegs.append(file)
    
    return jpegs


@app.route('/files/<filename>')
def get_file(filename):
  return send_file('./files/'+filename)


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
