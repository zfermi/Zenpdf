import os
import zipfile
import secrets
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify, session
from PyPDF2 import PdfReader, PdfWriter
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

__version__ = "1.0.0"

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB for free tier
MAX_MERGE_FILES = 5
ALLOWED_EXTENSIONS = {'pdf'}

# Flask configuration
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE * MAX_MERGE_FILES  # Allow total upload size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

# Folders for split and merged files
PARENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
SPLIT_FOLDER = os.path.join(PARENT_FOLDER, "split_folder")
MERGED_FOLDER = os.path.join(PARENT_FOLDER, "merged_folder")
UPLOAD_FOLDER = os.path.join(PARENT_FOLDER, "uploads")

# Ensure the folders exist
for folder in [SPLIT_FOLDER, MERGED_FOLDER, UPLOAD_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Clean up old files on startup
def cleanup_old_files(folder, max_age_hours=1):
    """Remove files older than max_age_hours"""
    try:
        current_time = datetime.now().timestamp()
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > (max_age_hours * 3600):
                    try:
                        os.remove(file_path)
                    except:
                        pass
    except:
        pass

cleanup_old_files(SPLIT_FOLDER)
cleanup_old_files(MERGED_FOLDER)
cleanup_old_files(UPLOAD_FOLDER)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sanitize_filename(filename):
    """Sanitize filename to prevent path traversal"""
    # Remove any path components
    filename = os.path.basename(filename)
    # Use werkzeug's secure_filename
    filename = secure_filename(filename)
    # Ensure it ends with .pdf
    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'
    return filename

def validate_file_size(file):
    """Validate file size"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        raise ValueError(f"File size exceeds {MAX_FILE_SIZE // (1024*1024)}MB limit")
    if size == 0:
        raise ValueError("File is empty")
    return size

@app.errorhandler(413)
@app.errorhandler(RequestEntityTooLarge)
def too_large(e):
    flash('File too large. Maximum size is 10MB.', 'error')
    return redirect(request.url), 413

@app.errorhandler(500)
def internal_error(e):
    flash('An error occurred. Please try again.', 'error')
    return redirect(url_for('home')), 500

@app.route('/')
def home():
    return render_template('index.html', version=__version__)

@app.route('/version')
def version():
    """API endpoint to check version"""
    return jsonify({
        'version': __version__,
        'name': 'ZenPDF',
        'status': 'production'
    })

@app.route('/split', methods=['GET', 'POST'])
def split_pdf():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                try:
                    # Validate file size
                    validate_file_size(file)
                    
                    # Sanitize filename and create unique name
                    safe_filename = sanitize_filename(file.filename)
                    unique_filename = f"{secrets.token_hex(8)}_{safe_filename}"
                    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                    file.save(file_path)

                    # Validate PDF
                    try:
                        reader = PdfReader(file_path)
                        page_count = len(reader.pages)
                        if page_count == 0:
                            os.remove(file_path)
                            flash('Invalid PDF: File has no pages.', 'error')
                            return render_template('split.html', file_uploaded=False)
                    except Exception as e:
                        os.remove(file_path)
                        flash(f'Invalid PDF file: {str(e)}', 'error')
                        return render_template('split.html', file_uploaded=False)

                    # Store filename in session for next request
                    session['split_file'] = unique_filename
                    flash('PDF uploaded successfully!', 'success')
                    return render_template('split.html', file_uploaded=True, page_count=page_count, file_name=unique_filename)
                    
                except ValueError as e:
                    flash(str(e), 'error')
                except Exception as e:
                    flash(f'Error uploading file: {str(e)}', 'error')
            else:
                flash('Please select a valid PDF file.', 'error')
        
        elif 'split_type' in request.form:
            try:
                file_name = session.get('split_file') or request.form.get('file_name')
                if not file_name:
                    flash('File not found. Please upload again.', 'error')
                    return render_template('split.html', file_uploaded=False)
                
                file_path = os.path.join(UPLOAD_FOLDER, file_name)
                
                if not os.path.exists(file_path):
                    flash('File not found. Please upload again.', 'error')
                    session.pop('split_file', None)
                    return render_template('split.html', file_uploaded=False)
                
                split_type = request.form['split_type']
                pages_to_split = []
                
                reader = PdfReader(file_path)
                total_pages = len(reader.pages)

                # Get the page numbers to split based on user input
                if split_type == 'range':
                    try:
                        start_page = int(request.form.get('start_page', 1))
                        end_page = int(request.form.get('end_page', total_pages))
                        
                        # Validate range
                        if start_page < 1 or end_page > total_pages or start_page > end_page:
                            flash(f'Invalid page range. Please enter pages between 1 and {total_pages}.', 'error')
                            return render_template('split.html', file_uploaded=True, 
                                                 page_count=total_pages, file_name=file_name)
                        
                        pages_to_split = list(range(start_page - 1, end_page))
                    except ValueError:
                        flash('Please enter valid page numbers.', 'error')
                        return render_template('split.html', file_uploaded=True, 
                                             page_count=total_pages, file_name=file_name)
                        
                elif split_type == 'specific':
                    try:
                        specific_pages = request.form.get('specific_pages', '').strip()
                        # Support both comma-separated and range notation (e.g., "1,3,5-7")
                        page_set = set()
                        for part in specific_pages.split(','):
                            part = part.strip()
                            if '-' in part:
                                start, end = map(int, part.split('-'))
                                page_set.update(range(start, end + 1))
                            else:
                                page_set.add(int(part))
                        
                        pages_to_split = sorted([p - 1 for p in page_set if 1 <= p <= total_pages])
                        
                        if not pages_to_split:
                            flash('No valid pages specified.', 'error')
                            return render_template('split.html', file_uploaded=True, 
                                                 page_count=total_pages, file_name=file_name)
                    except ValueError:
                        flash('Invalid page format. Use comma-separated numbers or ranges (e.g., 1,3,5-7).', 'error')
                        return render_template('split.html', file_uploaded=True, 
                                             page_count=total_pages, file_name=file_name)
                        
                elif split_type == 'even':
                    pages_to_split = [i for i in range(total_pages) if (i + 1) % 2 == 0]
                elif split_type == 'odd':
                    pages_to_split = [i for i in range(total_pages) if (i + 1) % 2 != 0]
                else:
                    flash('Invalid split type.', 'error')
                    return render_template('split.html', file_uploaded=True, 
                                         page_count=total_pages, file_name=file_name)

                if not pages_to_split:
                    flash('No pages selected to split.', 'error')
                    return render_template('split.html', file_uploaded=True, 
                                         page_count=total_pages, file_name=file_name)

                # Split PDF and create ZIP
                zip_file_path = split_pdf_pages(file_path, pages_to_split, SPLIT_FOLDER)
                
                # Clean up uploaded file
                try:
                    os.remove(file_path)
                    session.pop('split_file', None)
                except:
                    pass

                # Send ZIP file for download
                return send_file(zip_file_path, as_attachment=True, 
                               download_name=f"split_pages_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                               mimetype='application/zip')
                
            except Exception as e:
                flash(f'Error processing PDF: {str(e)}', 'error')
                session.pop('split_file', None)
                return render_template('split.html', file_uploaded=False)

    return render_template('split.html', file_uploaded=False)

@app.route('/merge', methods=['GET', 'POST'])
def merge_pdf():
    if request.method == 'POST':
        files = request.files.getlist('files')
        
        if not files or all(f.filename == '' for f in files):
            flash('Please select at least one PDF file.', 'error')
            return render_template('merge.html', files_uploaded=False)
        
        if len(files) > MAX_MERGE_FILES:
            flash(f'Maximum {MAX_MERGE_FILES} files allowed for merging.', 'error')
            return render_template('merge.html', files_uploaded=False)
        
        file_paths = []
        errors = []
        
        for idx, file in enumerate(files):
            if file and file.filename and allowed_file(file.filename):
                try:
                    validate_file_size(file)
                    
                    safe_filename = sanitize_filename(file.filename)
                    unique_filename = f"{secrets.token_hex(8)}_{idx}_{safe_filename}"
                    file_path = os.path.join(MERGED_FOLDER, unique_filename)
                    file.save(file_path)
                    
                    # Validate PDF
                    try:
                        reader = PdfReader(file_path)
                        if len(reader.pages) == 0:
                            os.remove(file_path)
                            errors.append(f'{file.filename}: Invalid PDF (no pages)')
                            continue
                    except Exception as e:
                        os.remove(file_path)
                        errors.append(f'{file.filename}: {str(e)}')
                        continue
                    
                    file_paths.append(unique_filename)
                    
                except ValueError as e:
                    errors.append(f'{file.filename}: {str(e)}')
                except Exception as e:
                    errors.append(f'{file.filename}: {str(e)}')
            else:
                errors.append(f'{file.filename}: Invalid file type' if file.filename else 'Empty file')
        
        if errors:
            for error in errors:
                flash(error, 'error')
        
        if file_paths:
            session['merge_files'] = file_paths
            flash(f'Successfully uploaded {len(file_paths)} file(s)!', 'success')
            return render_template('merge.html', files_uploaded=True, file_paths=file_paths)
        else:
            return render_template('merge.html', files_uploaded=False)

    return render_template('merge.html', files_uploaded=False)

@app.route('/rearrange', methods=['POST'])
def rearrange_files():
    """Handle drag-and-drop reordering of files"""
    try:
        file_paths = request.json.get('file_paths', [])
        # Validate all files exist
        valid_paths = []
        for path in file_paths:
            if os.path.exists(os.path.join(MERGED_FOLDER, path)):
                valid_paths.append(path)
        return jsonify({'success': True, 'file_paths': valid_paths})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/merge_files', methods=['POST'])
def merge_files():
    try:
        file_paths = session.get('merge_files') or request.form.getlist('file_paths[]')
        
        if not file_paths:
            flash('No files to merge. Please upload files first.', 'error')
            return redirect(url_for('merge_pdf'))
        
        # Validate all files exist
        valid_paths = []
        for file_path in file_paths:
            full_path = os.path.join(MERGED_FOLDER, file_path)
            if os.path.exists(full_path):
                valid_paths.append(file_path)
        
        if not valid_paths:
            flash('Files not found. Please upload again.', 'error')
            session.pop('merge_files', None)
            return redirect(url_for('merge_pdf'))
        
        # Merge PDFs
        merged_file_path = merge_pdf_files(valid_paths, MERGED_FOLDER)
        
        # Clean up session
        session.pop('merge_files', None)
        
        # Send merged file for download
        return send_file(merged_file_path, as_attachment=True,
                       download_name=f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                       mimetype='application/pdf')
                       
    except Exception as e:
        flash(f'Error merging PDFs: {str(e)}', 'error')
        session.pop('merge_files', None)
        return redirect(url_for('merge_pdf'))

def split_pdf_pages(pdf_path, pages_to_split, output_dir):
    """Split PDF pages and create ZIP file"""
    reader = PdfReader(pdf_path)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_file_path = os.path.join(output_dir, f"split_pages_{timestamp}.zip")

    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for page_num in pages_to_split:
            if page_num >= len(reader.pages):
                continue
                
            writer = PdfWriter()
            writer.add_page(reader.pages[page_num])

            split_filename = f"page_{page_num + 1}.pdf"
            split_file_path = os.path.join(output_dir, split_filename)
            
            with open(split_file_path, "wb") as output_pdf:
                writer.write(output_pdf)

            # Add to ZIP
            zip_file.write(split_file_path, split_filename)
            
            # Clean up individual file
            try:
                os.remove(split_file_path)
            except:
                pass

    return zip_file_path

def merge_pdf_files(file_paths, output_dir):
    """Merge multiple PDF files into one"""
    writer = PdfWriter()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    for pdf_file in file_paths:
        pdf_path = os.path.join(MERGED_FOLDER, pdf_file)
        if not os.path.exists(pdf_path):
            continue
            
        try:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                writer.add_page(page)
        except Exception as e:
            continue

    merged_file_path = os.path.join(output_dir, f"merged_{timestamp}.pdf")
    with open(merged_file_path, "wb") as output_pdf:
        writer.write(output_pdf)

    # Clean up individual files
    for pdf_file in file_paths:
        try:
            os.remove(os.path.join(MERGED_FOLDER, pdf_file))
        except:
            pass

    return merged_file_path

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host=host, port=port, debug=debug)

