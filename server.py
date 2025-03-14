import subprocess
from flask import Response
import time, glob, os
from flask import Flask, render_template, request, jsonify, send_file
import stat
from PyPDF2 import PdfMerger, PdfReader

app = Flask(__name__)

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
    app.logger.info(f"Found PDF files: {pdf_files}")
    html = ""
    for file in pdf_files:
        html += createDownloadCardForPdf(file)
    app.logger.info(f"Generated HTML: {html}")
    return html

def createDownloadCardForPdf(path: str):
    file_name = path.split('/')[1]
    return f"""<article data-file="{path}">
            <header>{file_name}</header>
            <div class="document-actions">
                <button role="button" class="secondary" onclick="download('{path}')">Download</button>
                <button role="button" class="outline contrary" onclick="deleteFile('{path}')">Delete</button>
            </div>
            <div class="add-page-section">
                <input
                    type="text"
                    class="add-page-input"
                    placeholder="Enter filename for new page"
                    aria-label="New page filename"
                />
                <button role="button" class="outline" onclick="addPage('{path}')">Add Page</button>
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
                if selected_scanner:
                    return jsonify({'selected_scanner': selected_scanner})
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

def scan_document(filename: str) -> str:
    """
    Scan a document and return the path to the created PDF.
    
    Args:
        filename: The name of the file to create (without .pdf extension)
        
    Returns:
        str: Path to the created PDF file
        
    Raises:
        subprocess.CalledProcessError: If scanning fails
        FileNotFoundError: If the PDF is not created after scanning
    """
    app.logger.info(f"Running scan for new page with filename: {filename}")
    
    result = subprocess.run(
        f'scanRessources/scanDocument.sh {filename}',
        capture_output=True,
        text=True,
        shell=True,
        check=True,
        executable="/bin/bash"
    )
    
    pdf_path = f"scanRessources/{filename}.pdf"
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not created at: {pdf_path}")
        
    return pdf_path

def merge_pdfs(original_file: str, new_file: str, temp_file: str) -> None:
    """
    Merge two PDF files and save to a temporary file.
    The new file will be appended to the original file.
    
    Args:
        original_file: Path to the original PDF
        new_file: Path to the new PDF to append
        temp_file: Path to save the merged PDF temporarily
        
    Raises:
        Exception: If merge fails or resulting file is invalid
    """
    app.logger.info(f"Starting PDF merge process with temp file: {temp_file}")
    
    merger = PdfMerger()
    try:
        # First append the original file
        merger.append(original_file)
        # Then append the new file (this will be the second page)
        merger.append(new_file)
        # Write to temporary file
        merger.write(temp_file)
    finally:
        merger.close()
    
    # Verify the merged file exists and has content
    if not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
        raise Exception("Merged file is empty or does not exist")
        
    # Verify the merged file has the correct number of pages
    try:
        with open(temp_file, 'rb') as f:
            pdf = PdfReader(f)
            if len(pdf.pages) != 2:
                raise Exception(f"Expected 2 pages in merged file, got {len(pdf.pages)}")
    except Exception as e:
        app.logger.error(f"Error verifying merged PDF: {str(e)}")
        raise Exception("Failed to verify merged PDF structure")

def cleanup_files(files_to_remove: list[str]) -> None:
    """
    Remove a list of files, logging any errors but continuing.
    
    Args:
        files_to_remove: List of file paths to remove
    """
    for file_path in files_to_remove:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            app.logger.warning(f"Failed to remove file {file_path}: {str(e)}")

def verify_file_exists(file_path: str, description: str) -> None:
    """
    Verify that a file exists, raising an appropriate error if not.
    
    Args:
        file_path: Path to the file to check
        description: Description of the file for error messages
        
    Raises:
        FileNotFoundError: If the file does not exist
    """
    if not os.path.exists(file_path):
        error_msg = f"{description} not found at: {file_path}"
        app.logger.error(error_msg)
        raise FileNotFoundError(error_msg)

@app.route('/add_page', methods=['POST'])
def add_page():
    """
    Add a new page to an existing PDF document.
    
    Request body:
        original_file: Path to the original PDF
        new_filename: Name for the new page (without .pdf extension)
        
    Returns:
        JSON response with updated HTML grid or error message
    """
    try:
        # Validate input
        data = request.get_json()
        original_file = data.get('original_file')
        new_filename = data.get('new_filename')
        
        if not original_file or not new_filename:
            return jsonify({"error": "Both original file and new filename are required"}), 400
        
        new_filename = new_filename.rstrip('.pdf')
        app.logger.info(f"Starting add_page with original_file: {original_file}, new_filename: {new_filename}")
        
        # Verify original file exists
        verify_file_exists(original_file, "Original file")
        
        # Scan new page
        new_pdf = scan_document(new_filename)
        
        # Prepare for merge
        merged_temp = f"scanRessources/temp_merged_{new_filename}.pdf"
        files_to_cleanup = [new_pdf]
        
        try:
            # Merge PDFs
            merge_pdfs(original_file, new_pdf, merged_temp)
            files_to_cleanup.append(merged_temp)
            
            # Remove original and new files
            cleanup_files([original_file, new_pdf])
            
            # Rename merged file to original name
            os.rename(merged_temp, original_file)
            files_to_cleanup.remove(merged_temp)
            
            # Verify final file
            verify_file_exists(original_file, "Final merged file")
            
            # Generate response
            html = generate_download_grid()
            if not html.strip():
                raise Exception("Failed to generate HTML for updated file list")
            
            app.logger.info("Successfully completed PDF merge and file updates")
            return jsonify({"html": html, "success": True})
            
        except Exception as e:
            app.logger.error(f"Error during PDF merge: {str(e)}")
            cleanup_files(files_to_cleanup)
            raise
            
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Scanner error: {e.stderr}")
        if "scanimage: no SANE devices found" in e.stderr:
            return jsonify({"error": "No scanner found. Please check if your scanner is connected."}), 400
        elif "scanimage: open of device" in e.stderr:
            return jsonify({"error": "Could not open scanner. Please check if it's connected and powered on."}), 400
        else:
            return jsonify({"error": f"Scanner error: {e.stderr}"}), 400
            
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
        
    except Exception as e:
        app.logger.error(f"Error adding page: {str(e)}")
        return jsonify({"error": f"Failed to add page: {str(e)}"}), 500

@app.route('/check_file', methods=['POST'])
def check_file():
    try:
        filepath = request.get_json().get('filepath')
        if not filepath:
            return jsonify({"exists": False, "error": "No filepath provided"}), 400
            
        file_exists = os.path.exists(filepath)
        return jsonify({"exists": file_exists})
    except Exception as e:
        app.logger.error(f"Error checking file: {str(e)}")
        return jsonify({"exists": False, "error": str(e)}), 500

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5400, debug=True)
