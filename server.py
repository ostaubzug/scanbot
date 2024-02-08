import subprocess
import time, glob, os
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scanfunction', methods=['POST'])
def scan_function():
    app.logger.info(request.get_json().get('type'))
    subprocess.run('scanRessources/scanDocument.sh', capture_output=True, text=True)
    createDownloadGrid()

@app.route('/reload', methods=['POST'])
def createDownloadGrid():
    pdf_files = glob.glob("scanRessources/*.pdf")
    html = ""
    for file in pdf_files:
        html += createDownloadCardForPdf(file)
    return html
    

def createDownloadCardForPdf(path: str):
    file_name = path.split('/')[1]
    return f"""<article>
            <header>{file_name}</header>
            <button role="button" class="secondary" onclick="download(\'{path}\')">Download</button>
            <button role="button" onclick="">Append</button>
            <button role="button" class="outline contrary" onclick="deleteFile(\'{path}\')">Delete</button>
            </article>"""


@app.route('/download', methods=['POST'])
def download():
    filepath = request.get_json().get('filepath')
    app.logger.info(filepath)
    return send_file(filepath, as_attachment=True)

@app.route('/deleteFile', methods=['POST'])
def delete():
    os.remove(request.get_json().get('filepath'))
    return createDownloadGrid()

def getDeviceName():
    return subprocess.run('scanRessources/getMachineName.sh', capture_output=True, text=True).stdout
     

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5400, debug=True)
