import subprocess
import time, glob, os
from flask import Flask, render_template, request, jsonify, send_file
import stat

app = Flask(__name__)

# Add execute permission to the script
script_path = 'scanRessources/scanDocument.sh'
st = os.stat(script_path)
os.chmod(script_path, st.st_mode | stat.S_IEXEC)

script_path = 'scanRessources/scanTiffHighRes.sh'
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

@app.route('/scanfunctionTiffHighRes', methods=['POST'])
def scan_function_highRes():
    app.logger.info(request.get_json().get('type'))
    file_name = request.get_json().get('filename')
    subprocess.run(f'scanRessources/scanTiffHighRes.sh {file_name}', capture_output=True, text=True, shell=True, check=True, executable="/bin/bash")
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
            <button role="button" class="secondary" onclick="downloadHighRes(\'{path}\')">DownloadHighRes</button>
            <button role="button" class="outline contrary" onclick="deleteFile(\'{path}\')">Delete</button>
            </article>"""


@app.route('/download', methods=['POST'])
def download():
    filepath = request.get_json().get('filepath')
    app.logger.info(filepath)
    return send_file(filepath, as_attachment=True)

@app.route('/downloadHighREs', methods=['POST'])
def downloadHighRes():
   filepath = request.get_json().get('filepath')
   app.logger.info(filepath)
   
   def generate():
       with open(filepath, 'rb') as f:
           while True:
               chunk = f.read(8192)  # 8KB chunks
               if not chunk:
                   break
               yield chunk

   return Response(
       generate(),
       mimetype='application/octet-stream',
       headers={'Content-Disposition': f'attachment; filename={os.path.basename(filepath)}'}
   )

@app.route('/deleteFile', methods=['POST'])
def delete():
    os.remove(request.get_json().get('filepath'))
    return createDownloadGrid()

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5400, debug=True)
