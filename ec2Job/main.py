from sre_constants import SUCCESS
import subprocess
from werkzeug.utils import secure_filename
import os
from flask import Flask, flash, request, redirect, url_for
import requests


UPLOAD_FOLDER = '../vdbs'
DESTINATION_FOLDER = '../exrs'
ALLOWED_EXTENSIONS = {'vdb'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DESTINATION_FOLDER'] = DESTINATION_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 300 * 1000 * 1000

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def hello_world():
    return {"hello":"world"}


@app.route('/processvdb', methods=['POST'])
def processVDB():
    error = None
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            # No file part
            return {"error":"nofilepart"}
        file = request.files['file']
        # empty file without a filename.
        if file.filename == '':
            # No selected file'
            return {"error":"nofilename"}
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            print("FILENAME is " + filename)
            completeuploadfile = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            completerenderfile = os.path.join(app.config['DESTINATION_FOLDER'], filename.split(".")[0]+".exr")
            file.save(completeuploadfile)

            completedprocess = subprocess.run([\
                "vdb_render", \
                completeuploadfile, \
                completerenderfile])

            if completedprocess.returncode != 0:
                return {"error":"CONVERSION FAILED"}

            completedprocess = subprocess.run(["aws", "s3" ,"mv", completerenderfile, "s3://exrbucket"])
            if completedprocess.returncode != 0:
                return {"error":"Bucket upload FAILED"}

            print("conversion and upload complete")
            
            return {"info":"SUCESS"}

    return {"error":"request method invalid for this process"}




