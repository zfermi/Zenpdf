# OCR Implementation Plan for ZenPDF

## 🎯 Goal
Add OCR (Optical Character Recognition) to convert scanned PDFs and images to searchable, editable text.

---

## 📋 Overview

**What is OCR?**
- Converts images of text (scanned PDFs, photos) into machine-readable text
- Makes scanned documents searchable and editable
- Essential premium feature for PDF tools

**Use Cases:**
- Scanned documents → Searchable PDFs
- Image-based PDFs → Editable Word documents
- Old paper documents → Digital text

---

## 🛠️ Technology Stack

### **Option 1: Tesseract OCR (Recommended for MVP)**

**Pros:**
- ✅ Free and open-source
- ✅ Works offline (no API costs)
- ✅ 80-85% accuracy on clean documents
- ✅ Supports 100+ languages
- ✅ Easy to integrate with Python

**Cons:**
- ⚠️ Lower accuracy on complex layouts (tables, forms)
- ⚠️ Requires image preprocessing for best results
- ⚠️ CPU intensive

**Libraries Needed:**
```bash
pip install pytesseract pdf2image Pillow opencv-python numpy
```

**System Dependencies:**
- Tesseract OCR engine
- Poppler (for PDF to image conversion)

---

### **Option 2: Cloud OCR APIs (Future Upgrade)**

**Google Cloud Vision API:**
- 95-99% accuracy
- $1.50 per 1,000 pages
- Best for complex documents

**AWS Textract:**
- Excellent for forms and tables
- $1.50 per 1,000 pages
- Built-in table extraction

**Azure Computer Vision:**
- Good accuracy
- $1.00 per 1,000 pages
- Multi-language support

---

## 🚀 Implementation Phases

### **Phase 1: Basic OCR (Week 1-2)**

**Goal:** Convert scanned PDFs to searchable PDFs

**Features:**
- Upload scanned PDF
- Extract text using Tesseract
- Create searchable PDF with text layer
- Download result

**Tech Stack:**
- `pytesseract` - OCR engine wrapper
- `pdf2image` - Convert PDF pages to images
- `PyPDF2` - PDF manipulation
- `reportlab` or `fpdf` - Create searchable PDFs

**Steps:**
1. Convert PDF pages to images (300 DPI)
2. Preprocess images (grayscale, denoise, deskew)
3. Run OCR on each page
4. Overlay text on original PDF
5. Return searchable PDF

---

### **Phase 2: Image Preprocessing (Week 3)**

**Goal:** Improve OCR accuracy with image enhancement

**Preprocessing Steps:**
1. **Grayscale Conversion** - Remove color noise
2. **Thresholding** - Convert to black & white
3. **Noise Removal** - Clean up specks
4. **Deskewing** - Straighten tilted text
5. **Contrast Enhancement** - Make text clearer

**Libraries:**
- `OpenCV (cv2)` - Image processing
- `NumPy` - Array operations
- `Pillow` - Basic image ops

---

### **Phase 3: Advanced Features (Week 4)**

**Features:**
- Language selection (English, Spanish, French, etc.)
- Confidence scoring
- Layout preservation
- Table detection
- Multi-column text handling

---

### **Phase 4: Premium Integration (Week 5)**

**Features:**
- Batch OCR (multiple files)
- Progress tracking
- Email notification when complete
- Cloud storage integration

---

## 💻 Code Structure

```
Zenpdf/
├── ocr/
│   ├── __init__.py
│   ├── ocr_engine.py          # Main OCR logic
│   ├── preprocessor.py        # Image preprocessing
│   ├── pdf_converter.py       # PDF to image conversion
│   └── searchable_pdf.py      # Create searchable PDFs
├── templates/
│   └── ocr.html               # OCR upload page
└── static/
    └── ocr_samples/           # Sample files for testing
```

---

## 📝 Sample Implementation

### **1. Install Dependencies**

**On Ubuntu/Debian (Railway):**
```bash
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-eng poppler-utils
pip install pytesseract pdf2image Pillow opencv-python-headless numpy
```

**On Windows (Local Dev):**
```bash
# Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
# Install Poppler from: https://github.com/oschwartz10612/poppler-windows/releases
pip install pytesseract pdf2image Pillow opencv-python numpy
```

---

### **2. Basic OCR Function**

```python
# ocr/ocr_engine.py
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import cv2
import numpy as np

def preprocess_image(image):
    """Enhance image for better OCR accuracy"""
    # Convert PIL to OpenCV format
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    # Noise removal
    denoised = cv2.medianBlur(thresh, 3)
    
    # Convert back to PIL
    return Image.fromarray(denoised)

def extract_text_from_pdf(pdf_path, language='eng'):
    """Extract text from PDF using OCR"""
    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=300)
    
    extracted_text = []
    
    for page_num, image in enumerate(images, 1):
        # Preprocess image
        processed_image = preprocess_image(image)
        
        # Extract text
        text = pytesseract.image_to_string(
            processed_image,
            lang=language,
            config='--psm 3 --oem 3'  # Auto page segmentation, LSTM engine
        )
        
        extracted_text.append({
            'page': page_num,
            'text': text,
            'confidence': get_confidence(processed_image)
        })
    
    return extracted_text

def get_confidence(image):
    """Get OCR confidence score"""
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    confidences = [int(conf) for conf in data['conf'] if conf != '-1']
    return sum(confidences) / len(confidences) if confidences else 0
```

---

### **3. Flask Route**

```python
# app.py
@app.route('/ocr', methods=['GET', 'POST'])
@login_required  # Premium only
def ocr_pdf():
    """OCR PDF conversion"""
    if not current_user.is_premium:
        flash('OCR is a premium feature. Upgrade to access!', 'error')
        return redirect(url_for('pricing'))
    
    if request.method == 'POST':
        file = request.files.get('file')
        language = request.form.get('language', 'eng')
        
        if file and allowed_file(file.filename):
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Perform OCR
                from ocr.ocr_engine import extract_text_from_pdf
                results = extract_text_from_pdf(filepath, language)
                
                # Create searchable PDF
                from ocr.searchable_pdf import create_searchable_pdf
                output_path = create_searchable_pdf(filepath, results)
                
                # Record usage
                record_usage('ocr', file_size=os.path.getsize(filepath))
                
                # Clean up
                os.remove(filepath)
                
                return send_file(output_path, as_attachment=True)
                
            except Exception as e:
                flash(f'OCR failed: {str(e)}', 'error')
                
    return render_template('ocr.html')
```

---

### **4. HTML Template**

```html
<!-- templates/ocr.html -->
<form method="POST" enctype="multipart/form-data">
    <h2>OCR - Convert Scanned PDFs to Searchable Text</h2>
    
    <input type="file" name="file" accept=".pdf" required>
    
    <select name="language">
        <option value="eng">English</option>
        <option value="spa">Spanish</option>
        <option value="fra">French</option>
        <option value="deu">German</option>
    </select>
    
    <button type="submit">Convert to Searchable PDF</button>
</form>
```

---

## 🐳 Docker/Railway Setup

### **Dockerfile Updates**

```dockerfile
# Add to your Dockerfile
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-spa \
    tesseract-ocr-fra \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install pytesseract pdf2image opencv-python-headless
```

---

## 📊 Performance Considerations

### **Resource Usage:**
- **Memory:** ~25MB per page at 300 DPI
- **CPU:** High during OCR processing
- **Time:** ~2-5 seconds per page

### **Optimization Strategies:**
1. **Async Processing** - Use Celery for background jobs
2. **Caching** - Cache preprocessed images
3. **Batch Processing** - Process multiple pages in parallel
4. **Quality Settings** - Lower DPI for faster processing (200 DPI vs 300 DPI)

---

## 💰 Cost Analysis

### **Tesseract (Self-Hosted):**
- **Cost:** $0 (free)
- **Server:** ~$0.10/hour extra CPU usage
- **Total:** ~$0.001 per page

### **Cloud OCR:**
- **Google Vision:** $0.0015 per page
- **AWS Textract:** $0.0015 per page
- **Total:** $1.50 per 1,000 pages

**Recommendation:** Start with Tesseract, upgrade to cloud OCR if accuracy is insufficient.

---

## 🎯 Success Metrics

### **Phase 1 (MVP):**
- ✅ 80%+ OCR accuracy on clean scans
- ✅ <10 seconds per page processing
- ✅ Supports English language
- ✅ Creates searchable PDFs

### **Phase 2 (Production):**
- ✅ 90%+ accuracy with preprocessing
- ✅ <5 seconds per page
- ✅ Supports 5+ languages
- ✅ Batch processing

---

## 🚀 Launch Checklist

- [ ] Install Tesseract on Railway
- [ ] Create OCR module structure
- [ ] Implement basic OCR function
- [ ] Add image preprocessing
- [ ] Create searchable PDF generator
- [ ] Build OCR upload page
- [ ] Add to premium features
- [ ] Test with sample scanned PDFs
- [ ] Update pricing page
- [ ] Deploy to production

---

## 📚 Resources

- [Tesseract Documentation](https://tesseract-ocr.github.io/)
- [Pytesseract GitHub](https://github.com/madmaze/pytesseract)
- [PDF2Image Docs](https://github.com/Belval/pdf2image)
- [OpenCV Tutorials](https://docs.opencv.org/4.x/d9/df8/tutorial_root.html)

---

## 🎓 Learning Path

1. **Week 1:** Learn Tesseract basics, test with sample images
2. **Week 2:** Implement PDF to image conversion
3. **Week 3:** Master image preprocessing techniques
4. **Week 4:** Build searchable PDF creation
5. **Week 5:** Integrate into ZenPDF, test, deploy

---

**Estimated Time to MVP:** 2-3 weeks  
**Difficulty:** Medium  
**Impact:** High (major premium feature)
