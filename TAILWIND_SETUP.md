# Tailwind CSS Setup

This project uses Tailwind CSS for styling.

## Installation

```bash
npm install
```

## Building CSS

### Development (watch mode)
```bash
npm run watch:css
```

### Production (minified)
```bash
npm run build:css
```

## File Structure

- `tailwind.config.js` - Tailwind configuration with custom colors
- `static/input.css` - Source CSS file with Tailwind directives
- `static/output.css` - Generated CSS file (used by templates)
- `static/styles.css` - Legacy custom CSS (can be removed)

## Custom Colors

The project uses custom brand colors defined in `tailwind.config.js`:

- **Primary**: `#FF5656` (red)
- **Primary Dark**: `#FF3333`
- **Primary Light**: `#FFE5E5`
- **Secondary**: `#4CAF50` (green)
- **Accent**: `#2196F3` (blue)

## Usage in Templates

All HTML templates should reference `output.css`:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='output.css') }}">
```

## Custom Components

Custom component classes are defined in `static/input.css`:

- `.tool-card` - Card component for tool displays
- `.btn-primary` - Primary button styling
- `.alert`, `.alert-success`, `.alert-error`, etc. - Alert messages

## Deployment

Before deploying, always run:

```bash
npm run build:css
```

This ensures the `output.css` file is minified and up-to-date.
