from flask import Flask, render_template, request, jsonify, send_file
import glob
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scanfunction', methods=['POST'])
def scan_function():
    app.logger.info(request.get_json().get('type'))
    pdf_files = glob.glob("scanRessources/*.pdf")
    
    html = ""
    for file in pdf_files:
        html += createDownloadCardForPdf(file)
    return html

def createDownloadCardForPdf(path: str):
    file_name = path.split('/')[1]
    return f"""<article><header>{file_name}</header><button role="button" class="secondary" onclick="download(\'{path}\')">Download</button>
            <button role="button" class="outline contrary" onclick="delete(\'{path}\')">Delete</button></article>"""


@app.route('/download', methods=['POST'])
def download():
    filepath = request.get_json().get('filepath')
    app.logger.info(filepath)
    return send_file(filepath, as_attachment=True)

@app.route('/delete', methods=['POST'])
def delete():
    os.remove(request.get_json().get('filepath'))
    return True

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5400, debug=True)
