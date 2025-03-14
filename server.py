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

selected_scanner = None

def get_available_scanners():
    try:
        result = subprocess.run(['scanimage', '-L'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        scanners = []
        for line in result.stdout.split('\n'):
            if line.strip():
                # Extract device name from the output
                device = line.split('`')[1].split("'")[0] if '`' in line else None
                if device:
                    scanners.append({
                        'device': device,
                        'description': line
                    })
        return scanners
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Error getting scanners: {e.stderr}")
        return []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scanfunction', methods=['POST'])
def scan_function():
    file_name = request.get_json().get('filename')
    
    if not file_name:
        return jsonify({"error": "Filename is required"}), 400
        
    try:
        result = subprocess.run(f'scanRessources/scanDocument.sh {file_name}', 
                              capture_output=True, 
                              text=True, 
                              shell=True, 
                              check=True, 
                              executable="/bin/bash")
                              
        if "scanimage: no SANE devices found" in result.stderr:
            app.logger.error("No scanner found")
            return jsonify({"error": "No scanner found. Please check if your scanner is connected."}), 400
            
        expected_pdf = f"scanRessources/{file_name}.pdf"
        if not os.path.exists(expected_pdf):
            app.logger.error(f"PDF file not created at expected path: {expected_pdf}")
            return jsonify({"error": "Failed to create PDF file. Please check scanner connection and try again."}), 500
            
        grid_html = createDownloadGrid()
        return jsonify({"html": grid_html, "success": True})
        
    except subprocess.CalledProcessError as e:
        if "scanimage: no SANE devices found" in e.stderr:
            app.logger.error("No scanner found")
            return jsonify({"error": "No scanner found. Please check if your scanner is connected."}), 400
        elif "scanimage: open of device" in e.stderr:
            app.logger.error("Scanner connection error")
            return jsonify({"error": "Could not open scanner. Please check if it's connected and powered on."}), 400
        else:
            app.logger.error(f"Scanner error: {e.stderr}")
            return jsonify({"error": "An unexpected error occurred while scanning. Please check your scanner connection."}), 400
        
    except Exception as e:
        app.logger.error(f"Unexpected error during scan: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/reload', methods=['POST'])
def createDownloadGrid():
    pdf_files = [file for file in glob.glob("scanRessources/*.*") if not file.endswith('.sh')]
    html = ""
    for file in pdf_files:
        html += createDownloadCardForPdf(file)
    return jsonify({"html": html, "success": True})
    

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
    try:
        filepath = request.get_json().get('filepath')
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404
        os.remove(filepath)
        grid_html = createDownloadGrid()
        return jsonify({"html": grid_html, "success": True})
    except Exception as e:
        app.logger.error(f"Delete error: {str(e)}")
        return jsonify({"error": f"Failed to delete file: {str(e)}"}), 500

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/api/scanners', methods=['GET'])
def list_scanners():
    scanners = get_available_scanners()
    return jsonify({
        'scanners': scanners,
        'selected_scanner': selected_scanner
    })

@app.route('/api/scanner', methods=['POST'])
def set_scanner():
    global selected_scanner
    data = request.get_json()
    selected_scanner = data.get('device')
    
    try:
        with open('scanRessources/scanner_config', 'w') as f:
            f.write(selected_scanner)
    except Exception as e:
        app.logger.error(f"Failed to save scanner configuration: {e}")
        return jsonify({'error': 'Failed to save scanner configuration'}), 500
        
    return jsonify({'success': True, 'selected_scanner': selected_scanner})

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5400, debug=True)
