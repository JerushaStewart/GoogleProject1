import time
import os
from flask import Flask, redirect, request, send_file
from google.cloud import storage

os.makedirs('files', exist_ok = True)
app = Flask(__name__)
BUCKET_NAME = "imageproject1bucket"
storage_client = storage.Client()


@app.route('/')
def index():
    index_html="""
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
     <form method="post" enctype="multipart/form-data" action="/upload" >
  <div>
    <label for="file">Choose file to upload</label>
    <input type="file" id="file" name="form_file" accept="image/jpeg"/>
  </div>
  <div>
    <button>Submit</button>
  </div>
 </form>
 """
    end_html="""

    </div>
 <style>
 * {
   margin: 0;
   padding:0;
   
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
    padding:25px;
    
    }
    
 h1 {
   font-size: 20px;
   font-weight: bold;
   }
 
 .box {
   border: 1px solid black;
   }

   a{
    text-decoration: none; 
   }

 </style> 
 </body>
  
 </html>
 """    

    for file in list_files():
        index_html += "<li><a href=\"./files" + file + "\">" + file + "</a></li>" + end_html

    return index_html

def upload_to_bucket(bucket_name, file_path, file_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_path)
    

@app.route('/upload', methods=["POST"])
def upload():
    if 'form_file' not in request.files:
        return "No file part", 400  # Handle missing file in request

    file = request.files['form_file']
    
    if file.filename == '':
        return "No selected file", 400  # Handle empty filename

    file_path = os.path.join("./files", file.filename)
    file.save(file_path)
    upload_to_bucket(BUCKET_NAME, file_path, file.filename)
    
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
    # Development only: run "python main.py" and open http://localhost:8080
    # When deploying to Cloud Run, a production-grade WSGI HTTP server,
    # such as Gunicorn, will serve the app.
    app.run(host="localhost", port=8080, debug=True)

from google.cloud import datastore, storage
import time

datastore_client = datastore.Client()
storage_client = storage.Client()

###
# Datastore examples
###
def list_db_entries():
    query = datastore_client.query(kind="photos")

    for photo in query.fetch():
        print(photo.items())

def add_db_entry(object):
    entity = datastore.Entity(key=datastore_client.key('photos'))
    entity.update(object)

    datastore_client.put(entity)


def fetch_db_entry(object):
    #print(object)

    query = datastore_client.query(kind='photos')

    for attr in object.keys():
        query.add_filter(attr, "=", object[attr])

    obj = list(query.fetch())

    #print("fetch")
    #for photo in obj:
    #    print(photo.items())

    return obj

###
# Cloud Storage examples
###
def get_list_of_files(bucket_name):
    """Lists all the blobs in the bucket."""
    print("\n")
    print("get_list_of_files: "+bucket_name)

    blobs = storage_client.list_blobs(bucket_name)
    print(blobs)
    files = []
    for blob in blobs:
        files.append(blob.name)

    return files

def upload_file(bucket_name, file_name):
    """Send file to bucket."""
    print("\n")
    print("upload_file: "+bucket_name+"/"+file_name)

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    blob.upload_from_filename(file_name)

    return 

def download_file(bucket_name, file_name):
    """ Retrieve an object from a bucket and saves locally"""  
    print("\n")
    print("download_file: "+bucket_name+"/"+file_name)
    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(file_name)
    blob.download_to_filename(file_name)
    blob.reload()
    print(f"Blob: {blob.name}")
    print(f"Bucket: {blob.bucket.name}")
    print(f"Storage class: {blob.storage_class}")
    print(f"Size: {blob.size} bytes")
    print(f"Content-type: {blob.content_type}")
    print(f"Public URL: {blob.public_url}")

    return

# print(get_list_of_files("de-andrade-fau"))

# upload_file("de-andrade-fau", "test.txt")
# print(get_list_of_files("de-andrade-fau"))

# download_file("de-andrade-fau", "test.txt")
# upload_file("de-andrade-fau", "test1.txt")
# download_file("de-andrade-fau", "test1.txt")
# print(get_list_of_files("de-andrade-fau"))

# download_file("de-andrade-fau", "sample_640Ã—426.jpeg")


###
# Datastore
###
list_db_entries()

obj = {"name":"fau-rocks.jpeg", "url":"blablabla.com/ricardo.jpeg", "user":"rdeandrade", 'timestamp':int(time.time())}
add_db_entry(obj)

obj1 = {'user':'rdeandrade'}
print(obj1)
result=fetch_db_entry(obj1)
print(result)
print(len(result))