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
          DEFAULT: '#FF5656',
          dark: '#FF3333',
          light: '#FFE5E5',
        },
        secondary: {
          DEFAULT: '#4CAF50',
          dark: '#45A049',
        },
        accent: '#2196F3',
      },
      boxShadow: {
        'custom': '0 2px 4px rgba(0, 0, 0, 0.08)',
        'custom-lg': '0 4px 12px rgba(0, 0, 0, 0.12)',
        'custom-hover': '0 8px 24px rgba(0, 0, 0, 0.15)',
      },
    },
  },
  plugins: [],
}
