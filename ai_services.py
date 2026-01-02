"""
AI Services Module for ZenPDF
Integrates with Claude (Anthropic) and OpenAI APIs for intelligent document processing.
Provides: Summarization, Q&A, and Data Extraction capabilities.
"""
import os
import json
import re
import logging
from typing import Optional, Dict, Any, List
from functools import lru_cache
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Custom exception for AI service errors"""
    pass


class AIService:
    """
    AI Service wrapper supporting multiple providers (Anthropic Claude, OpenAI)
    with automatic fallback and retry logic.
    """
    
    PROVIDERS = ['anthropic', 'openai']
    
    def __init__(self):
        self.anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        self.default_provider = os.environ.get('AI_PROVIDER', 'anthropic')
        
        # API endpoints
        self.anthropic_url = "https://api.anthropic.com/v1/messages"
        self.openai_url = "https://api.openai.com/v1/chat/completions"
        
        # Model configurations
        self.models = {
            'anthropic': os.environ.get('ANTHROPIC_MODEL', 'claude-3-haiku-20240307'),
            'openai': os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
        }
        
        # Rate limiting
        self.max_retries = 3
        self.timeout = 60
        
    def is_configured(self) -> bool:
        """Check if at least one AI provider is configured"""
        return bool(self.anthropic_api_key or self.openai_api_key)
    
    def get_available_provider(self) -> Optional[str]:
        """Get the first available configured provider"""
        if self.default_provider == 'anthropic' and self.anthropic_api_key:
            return 'anthropic'
        elif self.default_provider == 'openai' and self.openai_api_key:
            return 'openai'
        elif self.anthropic_api_key:
            return 'anthropic'
        elif self.openai_api_key:
            return 'openai'
        return None
    
    def _call_anthropic(self, prompt: str, system_prompt: str = "", max_tokens: int = 4096) -> str:
        """Call Anthropic Claude API"""
        headers = {
            "x-api-key": self.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": self.models['anthropic'],
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        response = requests.post(
            self.anthropic_url,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise AIServiceError(f"Anthropic API error: {response.status_code} - {response.text}")
        
        result = response.json()
        return result['content'][0]['text']
    
    def _call_openai(self, prompt: str, system_prompt: str = "", max_tokens: int = 4096) -> str:
        """Call OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.models['openai'],
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.3
        }
        
        response = requests.post(
            self.openai_url,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise AIServiceError(f"OpenAI API error: {response.status_code} - {response.text}")
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def generate(self, prompt: str, system_prompt: str = "", max_tokens: int = 4096, 
                 provider: Optional[str] = None) -> str:
        """
        Generate text using AI with automatic fallback.
        
        Args:
            prompt: The user prompt/question
            system_prompt: Optional system instructions
            max_tokens: Maximum tokens in response
            provider: Force specific provider ('anthropic' or 'openai')
            
        Returns:
            Generated text response
        """
        if provider is None:
            provider = self.get_available_provider()
        
        if not provider:
            raise AIServiceError("No AI provider configured. Please set ANTHROPIC_API_KEY or OPENAI_API_KEY.")
        
        last_error = None
        providers_to_try = [provider]
        
        # Add fallback provider
        if provider == 'anthropic' and self.openai_api_key:
            providers_to_try.append('openai')
        elif provider == 'openai' and self.anthropic_api_key:
            providers_to_try.append('anthropic')
        
        for current_provider in providers_to_try:
            for attempt in range(self.max_retries):
                try:
                    if current_provider == 'anthropic':
                        return self._call_anthropic(prompt, system_prompt, max_tokens)
                    else:
                        return self._call_openai(prompt, system_prompt, max_tokens)
                except requests.exceptions.Timeout:
                    last_error = AIServiceError(f"Request timeout after {self.timeout}s")
                    logger.warning(f"Attempt {attempt + 1} failed: timeout")
                except requests.exceptions.RequestException as e:
                    last_error = AIServiceError(f"Network error: {str(e)}")
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                except AIServiceError as e:
                    last_error = e
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    break  # Don't retry on API errors for same provider
        
        raise last_error or AIServiceError("All AI providers failed")


# Singleton instance
_ai_service = None

def get_ai_service() -> AIService:
    """Get singleton AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service


# ============== Specialized AI Functions ==============

def summarize_document(text: str, length: str = "medium", format: str = "paragraph") -> Dict[str, Any]:
    """
    Generate an intelligent summary of the document.
    
    Args:
        text: The document text to summarize
        length: 'short' (1-2 paragraphs), 'medium' (3-4 paragraphs), 'long' (detailed)
        format: 'paragraph', 'bullets', or 'executive'
        
    Returns:
        Dict with summary, key_points, word_count, etc.
    """
    ai = get_ai_service()
    
    length_instructions = {
        "short": "Keep the summary concise, 2-3 sentences maximum.",
        "medium": "Provide a moderate summary, 1-2 paragraphs.",
        "long": "Provide a comprehensive, detailed summary covering all main points."
    }
    
    format_instructions = {
        "paragraph": "Write in flowing paragraph format.",
        "bullets": "Present as bullet points for easy scanning.",
        "executive": "Write as an executive summary with a brief overview, key findings, and recommendations."
    }
    
    system_prompt = """You are a professional document analyst. Your task is to create clear, 
accurate summaries of documents. Focus on the most important information and maintain 
the original meaning. Be objective and factual."""
    
    prompt = f"""Please analyze and summarize the following document.

{length_instructions.get(length, length_instructions['medium'])}
{format_instructions.get(format, format_instructions['paragraph'])}

Also extract:
1. 3-5 key points from the document
2. Any important dates, numbers, or names mentioned
3. The main topic/theme in one sentence

Document:
---
{text[:50000]}  
---

Respond in this JSON format:
{{
    "summary": "Your summary here",
    "key_points": ["point 1", "point 2", ...],
    "important_entities": {{"dates": [], "numbers": [], "names": [], "organizations": []}},
    "main_topic": "One sentence describing the main topic",
    "document_type": "Best guess at document type (e.g., contract, report, article, etc.)"
}}"""

    try:
        response = ai.generate(prompt, system_prompt, max_tokens=2048)
        
        # Parse JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            result = json.loads(json_match.group())
            result['success'] = True
            result['original_word_count'] = len(text.split())
            result['summary_word_count'] = len(result.get('summary', '').split())
            return result
        else:
            # Fallback if JSON parsing fails
            return {
                'success': True,
                'summary': response,
                'key_points': [],
                'important_entities': {},
                'main_topic': 'Document analysis',
                'original_word_count': len(text.split()),
                'summary_word_count': len(response.split())
            }
            
    except Exception as e:
        logger.error(f"Summarization failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'summary': None
        }


def answer_question(text: str, question: str, context_window: int = 20000) -> Dict[str, Any]:
    """
    Answer questions about the document using AI.
    
    Args:
        text: The document text
        question: User's question about the document
        context_window: Maximum chars of text to send
        
    Returns:
        Dict with answer, confidence, relevant_quotes
    """
    ai = get_ai_service()
    
    system_prompt = """You are a helpful document analysis assistant. Answer questions about 
the provided document accurately and concisely. If the answer isn't in the document, say so clearly.
Always cite specific parts of the document when possible."""
    
    # Truncate text if too long
    truncated_text = text[:context_window]
    if len(text) > context_window:
        truncated_text += "\n\n[Document truncated due to length...]"
    
    prompt = f"""Based on the following document, please answer this question:

Question: {question}

Document:
---
{truncated_text}
---

Provide your response in this JSON format:
{{
    "answer": "Your detailed answer here",
    "confidence": "high/medium/low based on how clearly the document answers this",
    "relevant_quotes": ["Exact quotes from the document that support your answer"],
    "page_references": "Any page or section references if available",
    "additional_context": "Any relevant context or caveats"
}}

If the question cannot be answered from the document, set confidence to "not_found" and explain why."""

    try:
        response = ai.generate(prompt, system_prompt, max_tokens=1500)
        
        # Parse JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            result = json.loads(json_match.group())
            result['success'] = True
            result['question'] = question
            return result
        else:
            return {
                'success': True,
                'answer': response,
                'question': question,
                'confidence': 'medium',
                'relevant_quotes': []
            }
            
    except Exception as e:
        logger.error(f"Q&A failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'question': question,
            'answer': None
        }


def extract_structured_data(text: str, extraction_type: str = "general") -> Dict[str, Any]:
    """
    Extract structured data from document text.
    
    Args:
        text: The document text
        extraction_type: 'general', 'invoice', 'contract', 'resume', 'receipt'
        
    Returns:
        Dict with extracted structured data
    """
    ai = get_ai_service()
    
    extraction_schemas = {
        "general": """Extract all important data including:
- Names and contact information
- Dates and deadlines
- Monetary amounts
- Key terms and definitions
- Important numbers or IDs
- Organizations mentioned""",

        "invoice": """Extract invoice-specific data:
- Invoice number
- Invoice date
- Due date
- Vendor/seller name and address
- Buyer name and address
- Line items (description, quantity, unit price, total)
- Subtotal
- Tax amount
- Total amount
- Payment terms""",

        "contract": """Extract contract-specific data:
- Contract title/type
- Parties involved
- Effective date
- Expiration date
- Key terms and conditions
- Payment terms
- Obligations of each party
- Termination clauses
- Signatures""",

        "resume": """Extract resume/CV data:
- Full name
- Contact information (email, phone, address)
- Professional summary
- Work experience (company, title, dates, responsibilities)
- Education (institution, degree, dates)
- Skills
- Certifications""",

        "receipt": """Extract receipt data:
- Store/merchant name
- Store address
- Date and time
- Items purchased (name, quantity, price)
- Subtotal
- Tax
- Total
- Payment method"""
    }
    
    system_prompt = """You are a data extraction specialist. Extract structured information 
from documents with high accuracy. Always maintain the exact values as they appear in the 
document. If a field is not present, use null."""
    
    prompt = f"""Please extract structured data from the following document.

Extraction Instructions:
{extraction_schemas.get(extraction_type, extraction_schemas['general'])}

Document:
---
{text[:40000]}
---

Respond with a JSON object containing all extracted data. Use appropriate nested structures 
for complex data. Include a "confidence" field (high/medium/low) for each extracted value 
where possible.

Example format for invoice:
{{
    "document_type": "invoice",
    "invoice_number": {{"value": "INV-12345", "confidence": "high"}},
    "date": {{"value": "2024-01-15", "confidence": "high"}},
    "vendor": {{
        "name": {{"value": "Acme Corp", "confidence": "high"}},
        "address": {{"value": "123 Main St", "confidence": "medium"}}
    }},
    "line_items": [
        {{"description": "Widget A", "quantity": 5, "unit_price": 10.00, "total": 50.00}}
    ],
    "total": {{"value": 55.00, "confidence": "high"}}
}}

Now extract data from the provided document:"""

    try:
        response = ai.generate(prompt, system_prompt, max_tokens=3000)
        
        # Parse JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            result = json.loads(json_match.group())
            return {
                'success': True,
                'extraction_type': extraction_type,
                'data': result,
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            return {
                'success': False,
                'error': 'Could not parse structured data from response',
                'raw_response': response
            }
            
    except Exception as e:
        logger.error(f"Data extraction failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def detect_tables_in_text(text: str) -> Dict[str, Any]:
    """
    Detect and extract tables from document text.
    
    Args:
        text: The document text
        
    Returns:
        Dict with detected tables in structured format
    """
    ai = get_ai_service()
    
    system_prompt = """You are a table extraction specialist. Identify and extract any tabular 
data present in the document. Convert the tables to a structured format."""
    
    prompt = f"""Analyze this document and extract any tables or tabular data you find.

Document:
---
{text[:30000]}
---

For each table found, provide:
1. A description of what the table contains
2. Column headers
3. All rows of data
4. The location/context where you found it

Respond in this JSON format:
{{
    "tables_found": true/false,
    "table_count": number,
    "tables": [
        {{
            "table_id": 1,
            "description": "Description of table contents",
            "headers": ["Column1", "Column2", ...],
            "rows": [
                ["value1", "value2", ...],
                ["value1", "value2", ...]
            ],
            "context": "Where in the document this table was found"
        }}
    ]
}}

If no tables are found, return {{"tables_found": false, "table_count": 0, "tables": []}}"""

    try:
        response = ai.generate(prompt, system_prompt, max_tokens=4000)
        
        # Parse JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            result = json.loads(json_match.group())
            result['success'] = True
            return result
        else:
            return {
                'success': True,
                'tables_found': False,
                'table_count': 0,
                'tables': [],
                'note': 'No structured tables detected'
            }
            
    except Exception as e:
        logger.error(f"Table detection failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
