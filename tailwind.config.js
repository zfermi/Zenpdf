/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#6C9A8B',
          dark: '#5A8577',
          light: '#A8C4B8',
        },
        secondary: {
          DEFAULT: '#2D3436',
          dark: '#1A1D1E',
          light: '#4A4F51',
        },
        sand: {
          DEFAULT: '#E8DCC4',
          light: '#F5F0E5',
          dark: '#D4C8B0',
        },
        zen: {
          charcoal: '#2D3436',
          sage: '#6C9A8B',
          sand: '#E8DCC4',
          cream: '#FFFEF9',
        },
      },
      boxShadow: {
        'custom': '0 1px 3px rgba(45, 52, 54, 0.08)',
        'custom-lg': '0 4px 12px rgba(45, 52, 54, 0.10)',
        'custom-hover': '0 8px 20px rgba(45, 52, 54, 0.12)',
        'zen': '0 2px 8px rgba(108, 154, 139, 0.15)',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
    },
  },
  plugins: [],
}
