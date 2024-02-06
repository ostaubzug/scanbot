from flask import Flask, render_template, request, jsonify
import glob

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scanfunction', methods=['POST'])
def scan_function():
    app.logger.info(request.get_json().get('type'))

    return createReturnHtml()

def createReturnHtml():
    pdf_files = glob.glob("scanRessources/*.pdf")
    html = ""
    for file in pdf_files:
        filename = file.split('/')[-1]
        html += createDownloadCardForPdf(filename)
    return html

def createDownloadCardForPdf(file_name: str):
    return f'<article><header>{file_name}</header><button role="button" class="secondary">Download</button></article>'

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5400, debug=True)
