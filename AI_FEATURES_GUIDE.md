# AI Document Intelligence - Setup & Usage Guide

## 🎯 Overview

ZenPDF now includes AI-powered document intelligence features that allow users to:

1. **📝 PDF Summarizer** - Generate intelligent summaries with key points
2. **📊 Table Extractor** - Extract tables from PDFs to CSV/JSON/Excel
3. **💬 PDF Q&A Chat** - Ask questions about document contents

These are **Premium features** - users must be logged in with an active premium subscription.

---

## 🛠️ Setup Instructions

### 1. Get API Keys

You need at least ONE of these AI providers configured:

**Option A: Anthropic Claude (Recommended)**
1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Create an account and add payment method
3. Generate an API key
4. Cost: ~$0.25 per 1M input tokens, ~$1.25 per 1M output tokens (Claude 3 Haiku)

**Option B: OpenAI**
1. Go to [platform.openai.com](https://platform.openai.com/)
2. Create an account and add payment method
3. Generate an API key
4. Cost: ~$0.50 per 1M input tokens, ~$1.50 per 1M output tokens (GPT-3.5)

### 2. Configure Environment Variables

Add these to your `.env` file:

```bash
# AI Document Intelligence
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
ANTHROPIC_MODEL=claude-3-haiku-20240307

# Optional: OpenAI as fallback
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Default provider: 'anthropic' or 'openai'
AI_PROVIDER=anthropic
```

### 3. Install Dependencies

```bash
pip install anthropic>=0.18.0 openai>=1.12.0
```

Or update from requirements.txt:
```bash
pip install -r requirements.txt
```

### 4. Deploy

For Railway:
```bash
# The environment variables will be read from Railway's dashboard
# Add ANTHROPIC_API_KEY (and optionally OPENAI_API_KEY) in Railway's Variables section
```

---

## 📱 User Guide

### PDF Summarizer (`/ai/summarize`)

**What it does:**
- Extracts text from uploaded PDF
- Generates an AI-powered summary
- Extracts key points and main topics
- Identifies document type

**Options:**
- **Summary Length**: Short, Medium, Long
- **Format**: Paragraph, Bullet Points, Executive Summary

**Output:**
- Main topic/theme
- Detailed summary
- Key points list
- Document type classification
- Word counts (original vs summary)

### Table Extractor (`/ai/extract-tables`)

**What it does:**
- Detects tables in PDF documents
- Extracts data to structured format
- Uses pattern matching + AI detection

**Export Formats:**
- CSV - Universal spreadsheet format
- JSON - Structured data format
- Excel - Coming soon

**Best for:**
- Invoices
- Financial reports
- Data sheets
- Tabular documents

### PDF Q&A Chat (`/ai/qa`)

**What it does:**
- Upload a PDF document
- Ask natural language questions
- Get AI-powered answers with citations

**Features:**
- Natural language understanding
- Source citations (quotes from document)
- Confidence scoring (high/medium/low)
- Conversation history

**Example Questions:**
- "What is this document about?"
- "Summarize the main points"
- "What are the key dates mentioned?"
- "Who are the parties involved?"
- "What is the total amount?"

---

## 💰 Cost Estimation

### Anthropic Claude 3 Haiku (Recommended)
- Input: $0.25 / 1M tokens
- Output: $1.25 / 1M tokens
- **Average cost per document**: $0.001 - $0.01

### OpenAI GPT-3.5 Turbo
- Input: $0.50 / 1M tokens
- Output: $1.50 / 1M tokens
- **Average cost per document**: $0.002 - $0.02

### Monthly Cost Estimates
| Users | Docs/Day | Monthly Cost (Claude) |
|-------|----------|----------------------|
| 100   | 50       | ~$1.50               |
| 500   | 250      | ~$7.50               |
| 1000  | 500      | ~$15.00              |

---

## 🔧 Technical Details

### File Structure
```
Zenpdf/
├── ai_services.py          # AI API integrations
├── document_intelligence.py # PDF processing
├── templates/
│   ├── ai-tools.html       # AI Tools hub
│   ├── ai-summarize.html   # Summarizer UI
│   ├── ai-extract-tables.html  # Table Extractor UI
│   └── ai-qa.html          # Q&A Chat UI
├── app.py                  # Routes (ai_tools, ai_summarize, etc.)
└── requirements.txt        # Dependencies
```

### Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/ai-tools` | GET | AI Tools hub page |
| `/ai/summarize` | GET, POST | PDF Summarizer |
| `/ai/extract-tables` | GET, POST | Table Extractor |
| `/ai/qa` | GET, POST | PDF Q&A Chat |
| `/ai/process-pdf` | POST | Process PDF for Q&A |

### Rate Limits
- Summarize: 20 requests/hour
- Extract Tables: 20 requests/hour
- Q&A: 30 requests/hour
- PDF Processing: 30 requests/hour

### Security
- All files are processed in memory and deleted immediately
- No document content is stored on servers
- API keys are server-side only (never exposed to browser)
- Premium user authentication required

---

## 🐛 Troubleshooting

### "AI service not configured"
**Cause:** No API key set
**Fix:** Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in environment

### "Failed to extract text from PDF"
**Cause:** PDF is image-based or encrypted
**Fix:** Use OCR feature first, or provide a native PDF

### "PDF contains too little text"
**Cause:** PDF has less than 50 characters of text
**Fix:** Ensure PDF is not blank or image-only

### Import Errors
**Cause:** Missing dependencies
**Fix:** Run `pip install anthropic openai`

---

## 🚀 Future Enhancements

- [ ] Excel export for table extraction
- [ ] Batch document processing
- [ ] Multi-language translation
- [ ] Document comparison
- [ ] Custom extraction templates
- [ ] API access for developers
- [ ] Workflow automation (Zapier integration)

---

## 📊 Analytics Tracking

AI feature usage is tracked with these operations:
- `ai_summarize` - PDF summarization
- `ai_extract_tables` - Table extraction
- `ai_qa` - Q&A questions answered

View usage in Admin Panel under Usage Records.
