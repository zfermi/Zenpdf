"""
Document Intelligence Module for ZenPDF
Handles PDF text extraction, table detection, and document processing
for AI-powered features like summarization, Q&A, and data extraction.
"""
import os
import re
import io
import csv
import json
import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

logger = logging.getLogger(__name__)


class DocumentExtractionError(Exception):
    """Custom exception for document extraction errors"""
    pass


class PDFProcessor:
    """
    Process PDF files for AI analysis.
    Extracts text using multiple methods with fallback to OCR.
    """
    
    def __init__(self):
        self.ocr_available = OCR_AVAILABLE
        self.max_pages = 100  # Maximum pages to process
        self.min_text_length = 50  # Minimum text to consider extraction successful
        
    def extract_text(self, pdf_path: str, use_ocr_fallback: bool = True) -> Dict[str, Any]:
        """
        Extract text from PDF using best available method.
        
        Args:
            pdf_path: Path to PDF file
            use_ocr_fallback: Whether to use OCR if text extraction fails
            
        Returns:
            Dict with extracted text and metadata
        """
        if not os.path.exists(pdf_path):
            raise DocumentExtractionError(f"File not found: {pdf_path}")
        
        result = {
            'success': False,
            'text': '',
            'pages': [],
            'page_count': 0,
            'extraction_method': None,
            'word_count': 0,
            'char_count': 0,
            'has_images': False,
            'metadata': {}
        }
        
        # Try PyPDF2 first (fast, works for native PDFs)
        try:
            text, pages, metadata = self._extract_with_pypdf2(pdf_path)
            
            if len(text.strip()) >= self.min_text_length:
                result['text'] = text
                result['pages'] = pages
                result['page_count'] = len(pages)
                result['extraction_method'] = 'pypdf2'
                result['metadata'] = metadata
                result['success'] = True
                result['word_count'] = len(text.split())
                result['char_count'] = len(text)
                logger.info(f"Successfully extracted {len(text)} chars with PyPDF2")
                return result
            else:
                logger.info("PyPDF2 extraction returned minimal text, trying OCR")
                
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {str(e)}")
        
        # Fallback to OCR if enabled and available
        if use_ocr_fallback and self.ocr_available:
            try:
                text, pages = self._extract_with_ocr(pdf_path)
                result['text'] = text
                result['pages'] = pages
                result['page_count'] = len(pages)
                result['extraction_method'] = 'ocr'
                result['success'] = True
                result['word_count'] = len(text.split())
                result['char_count'] = len(text)
                result['has_images'] = True
                logger.info(f"Successfully extracted {len(text)} chars with OCR")
                return result
                
            except Exception as e:
                logger.error(f"OCR extraction failed: {str(e)}")
                result['error'] = str(e)
        
        if not result['success']:
            result['error'] = "Could not extract text from PDF. The file may be empty, corrupted, or contain only images."
        
        return result
    
    def _extract_with_pypdf2(self, pdf_path: str) -> Tuple[str, List[Dict], Dict]:
        """Extract text using PyPDF2"""
        if PdfReader is None:
            raise DocumentExtractionError("PyPDF2 not available")
        
        reader = PdfReader(pdf_path)
        pages = []
        full_text = []
        
        # Extract metadata
        metadata = {}
        if reader.metadata:
            for key in ['/Title', '/Author', '/Subject', '/Creator', '/Producer']:
                if key in reader.metadata:
                    metadata[key.lstrip('/')] = str(reader.metadata[key])
        
        # Limit pages
        num_pages = min(len(reader.pages), self.max_pages)
        
        for i in range(num_pages):
            page = reader.pages[i]
            text = page.extract_text() or ''
            
            pages.append({
                'page_number': i + 1,
                'text': text,
                'word_count': len(text.split()),
                'char_count': len(text)
            })
            full_text.append(text)
        
        return '\n\n'.join(full_text), pages, metadata
    
    def _extract_with_ocr(self, pdf_path: str, dpi: int = 200) -> Tuple[str, List[Dict]]:
        """Extract text using OCR (Tesseract)"""
        if not self.ocr_available:
            raise DocumentExtractionError("OCR not available. Install pytesseract and pdf2image.")
        
        # Convert PDF pages to images
        images = convert_from_path(pdf_path, dpi=dpi)
        
        pages = []
        full_text = []
        
        # Limit pages
        num_pages = min(len(images), self.max_pages)
        
        for i, image in enumerate(images[:num_pages]):
            # Perform OCR
            text = pytesseract.image_to_string(image, lang='eng')
            
            pages.append({
                'page_number': i + 1,
                'text': text,
                'word_count': len(text.split()),
                'char_count': len(text),
                'ocr_processed': True
            })
            full_text.append(text)
        
        return '\n\n'.join(full_text), pages
    
    def get_page_text(self, pdf_path: str, page_numbers: List[int]) -> Dict[str, Any]:
        """Extract text from specific pages only"""
        result = self.extract_text(pdf_path)
        
        if not result['success']:
            return result
        
        filtered_pages = [p for p in result['pages'] if p['page_number'] in page_numbers]
        filtered_text = '\n\n'.join([p['text'] for p in filtered_pages])
        
        return {
            'success': True,
            'text': filtered_text,
            'pages': filtered_pages,
            'page_count': len(filtered_pages)
        }


class TableExtractor:
    """
    Extract tables from PDF documents.
    Uses pattern matching and AI assistance for complex tables.
    """
    
    def __init__(self):
        self.table_patterns = [
            # Tab or multiple space separated values
            r'([^\t\n]+[\t ]{2,}[^\t\n]+)',
            # Pipe separated values  
            r'([^|\n]+\|[^|\n]+)',
            # Comma separated with consistent structure
            r'^([^,\n]+,){2,}[^,\n]+$'
        ]
    
    def extract_tables_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect and extract table-like structures from text.
        
        Returns:
            List of detected tables with headers and rows
        """
        tables = []
        lines = text.split('\n')
        
        current_table = None
        table_start = None
        
        for i, line in enumerate(lines):
            # Check if line looks like table data
            is_table_line = self._is_table_line(line)
            
            if is_table_line:
                if current_table is None:
                    current_table = []
                    table_start = i
                current_table.append(line)
            else:
                if current_table and len(current_table) >= 2:
                    # Process completed table
                    table = self._parse_table(current_table, table_start)
                    if table:
                        tables.append(table)
                current_table = None
                table_start = None
        
        # Handle table at end of text
        if current_table and len(current_table) >= 2:
            table = self._parse_table(current_table, table_start)
            if table:
                tables.append(table)
        
        return tables
    
    def _is_table_line(self, line: str) -> bool:
        """Check if a line appears to be part of a table"""
        if not line.strip():
            return False
        
        # Check for common table separators
        has_tabs = '\t' in line
        has_pipes = '|' in line and line.count('|') >= 2
        has_multiple_spaces = '  ' in line and len(line.split()) >= 3
        
        # Check for consistent column-like structure
        parts = re.split(r'[\t|]|\s{2,}', line)
        has_columns = len([p for p in parts if p.strip()]) >= 2
        
        return (has_tabs or has_pipes or has_multiple_spaces) and has_columns
    
    def _parse_table(self, lines: List[str], start_line: int) -> Optional[Dict[str, Any]]:
        """Parse table lines into structured data"""
        if not lines:
            return None
        
        # Detect separator type
        if '|' in lines[0]:
            separator = '|'
        elif '\t' in lines[0]:
            separator = '\t'
        else:
            separator = r'\s{2,}'
        
        rows = []
        for line in lines:
            if separator in ['\t', '|']:
                cells = [cell.strip() for cell in line.split(separator) if cell.strip()]
            else:
                cells = [cell.strip() for cell in re.split(separator, line) if cell.strip()]
            
            if cells:
                rows.append(cells)
        
        if len(rows) < 2:
            return None
        
        # First row is typically headers
        headers = rows[0]
        data_rows = rows[1:]
        
        # Normalize column count
        max_cols = max(len(row) for row in rows)
        headers = headers + [''] * (max_cols - len(headers))
        data_rows = [row + [''] * (max_cols - len(row)) for row in data_rows]
        
        return {
            'table_id': start_line,
            'headers': headers,
            'rows': data_rows,
            'row_count': len(data_rows),
            'column_count': len(headers),
            'start_line': start_line + 1,
            'end_line': start_line + len(lines)
        }
    
    def tables_to_csv(self, tables: List[Dict[str, Any]]) -> str:
        """Convert extracted tables to CSV format"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        for i, table in enumerate(tables):
            if i > 0:
                writer.writerow([])  # Blank row between tables
            
            writer.writerow([f"--- Table {i + 1} ---"])
            writer.writerow(table['headers'])
            
            for row in table['rows']:
                writer.writerow(row)
        
        return output.getvalue()
    
    def tables_to_json(self, tables: List[Dict[str, Any]]) -> str:
        """Convert extracted tables to JSON format"""
        json_tables = []
        
        for table in tables:
            headers = table['headers']
            json_rows = []
            
            for row in table['rows']:
                row_dict = {}
                for j, header in enumerate(headers):
                    key = header or f'column_{j + 1}'
                    value = row[j] if j < len(row) else ''
                    row_dict[key] = value
                json_rows.append(row_dict)
            
            json_tables.append({
                'table_id': table['table_id'],
                'data': json_rows
            })
        
        return json.dumps(json_tables, indent=2)


# Singleton instances
_pdf_processor = None
_table_extractor = None

def get_pdf_processor() -> PDFProcessor:
    """Get singleton PDF processor instance"""
    global _pdf_processor
    if _pdf_processor is None:
        _pdf_processor = PDFProcessor()
    return _pdf_processor

def get_table_extractor() -> TableExtractor:
    """Get singleton table extractor instance"""
    global _table_extractor
    if _table_extractor is None:
        _table_extractor = TableExtractor()
    return _table_extractor


# ============== High-Level Functions ==============

def process_pdf_for_ai(pdf_path: str) -> Dict[str, Any]:
    """
    Process a PDF and prepare it for AI analysis.
    
    Returns:
        Dict with extracted text, tables, and metadata
    """
    processor = get_pdf_processor()
    table_extractor = get_table_extractor()
    
    # Extract text
    extraction_result = processor.extract_text(pdf_path)
    
    if not extraction_result['success']:
        return extraction_result
    
    # Extract tables
    tables = table_extractor.extract_tables_from_text(extraction_result['text'])
    
    return {
        'success': True,
        'text': extraction_result['text'],
        'pages': extraction_result['pages'],
        'page_count': extraction_result['page_count'],
        'word_count': extraction_result['word_count'],
        'char_count': extraction_result['char_count'],
        'extraction_method': extraction_result['extraction_method'],
        'metadata': extraction_result.get('metadata', {}),
        'tables': tables,
        'table_count': len(tables),
        'file_name': os.path.basename(pdf_path),
        'file_size': os.path.getsize(pdf_path),
        'processed_at': datetime.utcnow().isoformat()
    }


def extract_tables_to_format(pdf_path: str, output_format: str = 'json') -> Dict[str, Any]:
    """
    Extract tables from PDF and return in specified format.
    
    Args:
        pdf_path: Path to PDF file
        output_format: 'json', 'csv', or 'excel'
        
    Returns:
        Dict with table data in requested format
    """
    processor = get_pdf_processor()
    table_extractor = get_table_extractor()
    
    # Extract text
    extraction_result = processor.extract_text(pdf_path)
    
    if not extraction_result['success']:
        return extraction_result
    
    # Extract tables
    tables = table_extractor.extract_tables_from_text(extraction_result['text'])
    
    if not tables:
        return {
            'success': True,
            'tables_found': False,
            'message': 'No tables detected in the document.',
            'table_count': 0
        }
    
    # Format output
    if output_format == 'csv':
        formatted_data = table_extractor.tables_to_csv(tables)
        content_type = 'text/csv'
        extension = 'csv'
    elif output_format == 'json':
        formatted_data = table_extractor.tables_to_json(tables)
        content_type = 'application/json'
        extension = 'json'
    else:
        formatted_data = table_extractor.tables_to_json(tables)
        content_type = 'application/json'
        extension = 'json'
    
    return {
        'success': True,
        'tables_found': True,
        'table_count': len(tables),
        'tables': tables,
        'formatted_data': formatted_data,
        'content_type': content_type,
        'extension': extension,
        'file_name': os.path.basename(pdf_path)
    }
