"""
OCR Engine for ZenPDF
Converts scanned PDFs to searchable text using Tesseract OCR
"""
import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import cv2
import numpy as np
from datetime import datetime


class OCREngine:
    """Main OCR processing engine"""
    
    def __init__(self, dpi=300, language='eng'):
        """
        Initialize OCR engine
        
        Args:
            dpi (int): Resolution for PDF to image conversion (default: 300)
            language (str): Tesseract language code (default: 'eng')
        """
        self.dpi = dpi
        self.language = language
        
    def preprocess_image(self, image):
        """
        Enhance image for better OCR accuracy
        
        Args:
            image (PIL.Image): Input image
            
        Returns:
            PIL.Image: Preprocessed image
        """
        # Convert PIL to OpenCV format
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding for better results
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Noise removal
        denoised = cv2.medianBlur(thresh, 3)
        
        # Deskew if needed
        denoised = self.deskew(denoised)
        
        # Convert back to PIL
        return Image.fromarray(denoised)
    
    def deskew(self, image):
        """
        Correct skewed/tilted text
        
        Args:
            image (numpy.ndarray): Input image
            
        Returns:
            numpy.ndarray: Deskewed image
        """
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
            
        # Rotate image to deskew
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        return rotated
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from PDF using OCR
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            list: List of dicts with page number, text, and confidence
        """
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=self.dpi)
        
        extracted_text = []
        
        for page_num, image in enumerate(images, 1):
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Extract text with configuration
            text = pytesseract.image_to_string(
                processed_image,
                lang=self.language,
                config='--psm 3 --oem 3'  # Auto page segmentation, LSTM engine
            )
            
            # Get confidence score
            confidence = self.get_confidence(processed_image)
            
            extracted_text.append({
                'page': page_num,
                'text': text.strip(),
                'confidence': round(confidence, 2),
                'word_count': len(text.split())
            })
        
        return extracted_text
    
    def get_confidence(self, image):
        """
        Get OCR confidence score (0-100)
        
        Args:
            image (PIL.Image): Input image
            
        Returns:
            float: Average confidence score
        """
        try:
            data = pytesseract.image_to_data(
                image, 
                output_type=pytesseract.Output.DICT
            )
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            return sum(confidences) / len(confidences) if confidences else 0
        except:
            return 0
    
    def extract_text_from_image(self, image_path):
        """
        Extract text from a single image file
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            dict: Extracted text and metadata
        """
        image = Image.open(image_path)
        processed_image = self.preprocess_image(image)
        
        text = pytesseract.image_to_string(
            processed_image,
            lang=self.language,
            config='--psm 3 --oem 3'
        )
        
        return {
            'text': text.strip(),
            'confidence': self.get_confidence(processed_image),
            'word_count': len(text.split())
        }


def create_searchable_pdf(original_pdf_path, ocr_results, output_path=None):
    """
    Create a searchable PDF by overlaying OCR text on original PDF
    
    Args:
        original_pdf_path (str): Path to original PDF
        ocr_results (list): OCR results from extract_text_from_pdf
        output_path (str): Output file path (optional)
        
    Returns:
        str: Path to searchable PDF
    """
    from PyPDF2 import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    import io
    
    if output_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = original_pdf_path.replace('.pdf', f'_searchable_{timestamp}.pdf')
    
    reader = PdfReader(original_pdf_path)
    writer = PdfWriter()
    
    for page_num, page in enumerate(reader.pages):
        # Get OCR text for this page
        ocr_text = ocr_results[page_num]['text'] if page_num < len(ocr_results) else ""
        
        # Create invisible text layer
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFillColorRGB(0, 0, 0, alpha=0)  # Invisible text
        can.setFont("Helvetica", 10)
        
        # Add text (simplified - in production, you'd need proper positioning)
        text_object = can.beginText(10, 750)
        for line in ocr_text.split('\n'):
            text_object.textLine(line)
        can.drawText(text_object)
        can.save()
        
        # Merge text layer with original page
        packet.seek(0)
        text_pdf = PdfReader(packet)
        page.merge_page(text_pdf.pages[0])
        
        writer.add_page(page)
    
    # Write output
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)
    
    return output_path


# Example usage
if __name__ == "__main__":
    # Initialize OCR engine
    ocr = OCREngine(dpi=300, language='eng')
    
    # Extract text from PDF
    results = ocr.extract_text_from_pdf('sample.pdf')
    
    # Print results
    for result in results:
        print(f"Page {result['page']}:")
        print(f"Confidence: {result['confidence']}%")
        print(f"Text: {result['text'][:200]}...")  # First 200 chars
        print("-" * 50)
    
    # Create searchable PDF
    searchable_pdf = create_searchable_pdf('sample.pdf', results)
    print(f"Searchable PDF created: {searchable_pdf}")
