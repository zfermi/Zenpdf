# ZenPDF - Free PDF Split & Merge Tool

A modern, secure web application for splitting and merging PDF files. Built with Flask and designed for ease of use.

## Features

- ✅ **Split PDFs** - Extract pages by range, specific pages, or odd/even pages
- ✅ **Merge PDFs** - Combine multiple PDF files into one document
- ✅ **Drag & Drop** - Reorder files before merging
- ✅ **Secure** - Files are automatically deleted after processing
- ✅ **Free** - No registration required
- ✅ **Responsive** - Works on all devices

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

## Configuration

### Environment Variables

Create a `.env` file (optional) to set:
- `SECRET_KEY` - Flask session secret key (auto-generated if not set)

### File Limits

Current limits (configurable in `app.py`):
- Maximum file size: 10MB per file
- Maximum merge files: 5 files at once

## Project Structure

```
Zenpdf/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── index.html
│   ├── split.html
│   └── merge.html
├── static/              # Static files (CSS, JS, images)
│   └── styles.css
├── uploads/            # Temporary upload directory (auto-created)
├── split_folder/       # Split PDF outputs (auto-created)
└── merged_folder/      # Merged PDF outputs (auto-created)
```

## Security Features

- Filename sanitization to prevent path traversal
- File size validation
- File type validation
- Temporary file cleanup (auto-deleted after 1 hour)
- Secure file handling with unique filenames

## Monetization Ready

The application includes:
- Google AdSense integration slots (ready for ad code)
- Responsive ad placement (header, sidebar, content, footer)
- Structure ready for premium features

**To activate AdSense:**
1. Get your AdSense Publisher ID
2. Replace `ca-pub-XXXXXXXXXX` in templates with your actual ID
3. Replace `data-ad-slot="XXXXXXXXXX"` with your ad slot IDs

## Development

### Adding New Features

The codebase is structured for easy expansion:
- Add new routes in `app.py`
- Create new templates in `templates/`
- Add styles in `static/styles.css`

### Error Handling

The application includes comprehensive error handling:
- File validation errors
- PDF processing errors
- User-friendly error messages via Flask flash messages

## Deployment

### Recommended Platforms

- **Heroku** - Easy Flask deployment
- **DigitalOcean** - App Platform or Droplet
- **Railway** - Simple container deployment
- **AWS** - Elastic Beanstalk or EC2
- **Vercel** - With serverless functions

### Deployment Checklist

- [ ] Set `SECRET_KEY` environment variable
- [ ] Set `FLASK_ENV=production`
- [ ] Configure file size limits in server (nginx/apache)
- [ ] Set up SSL certificate
- [ ] Configure domain
- [ ] Add Google AdSense codes (optional)
- [ ] Set up monitoring/logging

## Future Enhancements

Planned features:
- [ ] Compress PDF
- [ ] PDF to Word/JPG conversion
- [ ] Rotate pages
- [ ] Add watermarks
- [ ] Protect/Unlock PDF
- [ ] OCR functionality
- [ ] User authentication
- [ ] Premium subscriptions

## License

MIT License - feel free to use and modify.

## Support

For issues or questions, please open an issue on GitHub.

---

**Note:** This is a production-ready MVP. For full SaaS features (user accounts, payments, etc.), additional development is required.

