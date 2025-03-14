import subprocess
from flask import Response
import time, glob, os
from flask import Flask, render_template, request, jsonify, send_file
import stat
from PyPDF2 import PdfMerger

app = Flask(__name__)

# Add execute permission to the script
script_path = 'scanRessources/scanDocument.sh'
st = os.stat(script_path)
os.chmod(script_path, st.st_mode | stat.S_IEXEC)

selected_scanner = None
selected_dpi = "600"

def get_available_scanners():
    try:
        result = subprocess.run(['scanimage', '-L'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        scanners = []
        for line in result.stdout.split('\n'):
            if line.strip():
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
    
    # Remove .pdf extension if present to avoid creating file.pdf.pdf
    file_name = file_name.rstrip('.pdf')
        
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
            
        html = generate_download_grid()
        return jsonify({"html": html, "success": True})
        
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
def reload_grid():
    html = generate_download_grid()
    return jsonify({"html": html, "success": True})
    
def generate_download_grid():
    pdf_files = [file for file in glob.glob("scanRessources/*.*") if not file.endswith('.sh')]
    html = ""
    for file in pdf_files:
        html += createDownloadCardForPdf(file)
    return html

def createDownloadCardForPdf(path: str):
    file_name = path.split('/')[1]
    return f"""<article>
            <header>{file_name}</header>
            <div class="button-group">
                <button role="button" class="secondary" onclick="download(\'{path}\')">Download</button>
                <button role="button" class="outline" onclick="addPage(\'{path}\')">Add Page</button>
                <button role="button" class="outline contrary" onclick="deleteFile(\'{path}\')">Delete</button>
            </div>
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
        html = generate_download_grid()
        return jsonify({"html": html, "success": True})
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

@app.route('/api/scanner', methods=['GET'])
def get_scanner():
    global selected_scanner
    
    try:
        if os.path.exists('scanRessources/scanner_config'):
            with open('scanRessources/scanner_config', 'r') as f:
                selected_scanner = f.read().strip()
    except Exception as e:
        app.logger.error(f"Failed to read scanner configuration: {e}")
    
    return jsonify({'selected_scanner': selected_scanner})

@app.route('/api/dpi', methods=['GET'])
def get_dpi():
    global selected_dpi
    
    try:
        if os.path.exists('scanRessources/dpi_config'):
            with open('scanRessources/dpi_config', 'r') as f:
                selected_dpi = f.read().strip()
    except Exception as e:
        app.logger.error(f"Failed to read DPI configuration: {e}")
    
    return jsonify({'dpi': selected_dpi})

@app.route('/api/dpi', methods=['POST'])
def set_dpi():
    global selected_dpi
    data = request.get_json()
    selected_dpi = data.get('dpi')
    
    if not selected_dpi:
        return jsonify({'error': 'DPI value is required'}), 400
    
    try:
        with open('scanRessources/dpi_config', 'w') as f:
            f.write(selected_dpi)
    except Exception as e:
        app.logger.error(f"Failed to save DPI configuration: {e}")
        return jsonify({'error': 'Failed to save DPI configuration'}), 500
        
    return jsonify({'success': True, 'dpi': selected_dpi})

@app.route('/add_page', methods=['POST'])
def add_page():
    try:
        data = request.get_json()
        original_file = data.get('original_file')
        new_filename = data.get('new_filename')
        
        if not original_file or not new_filename:
            return jsonify({"error": "Both original file and new filename are required"}), 400
        
        new_filename = new_filename.rstrip('.pdf')
            
        result = subprocess.run(f'scanRessources/scanDocument.sh {new_filename}', 
                              capture_output=True, 
                              text=True, 
                              shell=True, 
                              check=True, 
                              executable="/bin/bash")
                              
        new_pdf = f"scanRessources/{new_filename}.pdf"
        
        if not os.path.exists(new_pdf):
            return jsonify({"error": "Failed to create new page"}), 500
        merger = PdfMerger()
        merger.append(original_file)
        merger.append(new_pdf)
        
        merger.write(original_file)
        merger.close()
        
        os.remove(new_pdf)
        
        html = generate_download_grid()
        return jsonify({"html": html, "success": True})
        
    except subprocess.CalledProcessError as e:
        if "scanimage: no SANE devices found" in e.stderr:
            return jsonify({"error": "No scanner found. Please check if your scanner is connected."}), 400
        elif "scanimage: open of device" in e.stderr:
            return jsonify({"error": "Could not open scanner. Please check if it's connected and powered on."}), 400
        else:
            return jsonify({"error": f"Scanner error: {e.stderr}"}), 400
            
    except Exception as e:
        app.logger.error(f"Error adding page: {str(e)}")
        return jsonify({"error": f"Failed to add page: {str(e)}"}), 500

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5400, debug=True)
