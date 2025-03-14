import subprocess
from flask import Response
import time, glob, os
from flask import Flask, render_template, request, jsonify, send_file
import stat

app = Flask(__name__)

# Add execute permission to the script
script_path = 'scanRessources/scanDocument.sh'
st = os.stat(script_path)
os.chmod(script_path, st.st_mode | stat.S_IEXEC)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scanfunction', methods=['POST'])
def scan_function():
    app.logger.info(request.get_json().get('type'))
    file_name = request.get_json().get('filename')
    subprocess.run(f'scanRessources/scanDocument.sh {file_name}', capture_output=True, text=True, shell=True, check=True, executable="/bin/bash")
    return createDownloadGrid()

@app.route('/reload', methods=['POST'])
def createDownloadGrid():
    pdf_files = [file for file in glob.glob("scanRessources/*.*") if not file.endswith('.sh')]
    html = ""
    for file in pdf_files:
        html += createDownloadCardForPdf(file)
    return html
    

def createDownloadCardForPdf(path: str):
    file_name = path.split('/')[1]
    return f"""<article>
            <header>{file_name}</header>
            <button role="button" class="secondary" onclick="download(\'{path}\')">Download</button>
            <button role="button" class="outline contrary" onclick="deleteFile(\'{path}\')">Delete</button>
            </article>"""


@app.route('/download', methods=['POST'])
def download():
    try:
        filepath = request.get_json().get('filepath')
        app.logger.info(f"Starting download for: {filepath}")
        if not os.path.exists(filepath):
            app.logger.error(f"File not found: {filepath}")
            return "File not found", 404
        app.logger.info(f"Sending file: {filepath}")
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        app.logger.error(f"Download error: {str(e)}")
        return str(e), 500

@app.route('/deleteFile', methods=['POST'])
def delete():
    os.remove(request.get_json().get('filepath'))
    return createDownloadGrid()

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5400, debug=True)
