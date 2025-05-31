/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#5C6EFF',
          hover: '#4B5EE6',
          light: '#E8EBFF',
        },
        secondary: {
          orange: '#FF9B4E',
          green: '#4ECB71',
          red: '#FF6B6B',
          yellow: '#FFD93D',
          purple: '#9B59B6',
          blue: '#4169E1',
        },
        gray: {
          50: '#FAFBFC',
          100: '#F5F5F7',
          200: '#E8E8ED',
          300: '#E0E0E0',
          400: '#999999',
          500: '#666666',
          600: '#4A4A4A',
          700: '#333333',
          800: '#1A1A1A',
          900: '#0A0A0A',
        },
        error: '#FF4444',
        success: '#4ECB71',
        warning: '#FFD93D',
        info: '#5C6EFF',
      },
      borderRadius: {
        'sm': '6px',
        'DEFAULT': '8px',
        'md': '12px',
        'lg': '16px',
        'xl': '20px',
      },
      boxShadow: {
        'card': '0 2px 8px rgba(0,0,0,0.06)',
        'modal': '0 8px 32px rgba(0,0,0,0.12)',
        'button': '0 4px 12px rgba(92,110,255,0.25)',
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', '"Helvetica Neue"', 'Arial', 'sans-serif'],
      },
      fontSize: {
        'xs': '12px',
        'sm': '13px',
        'base': '14px',
        'lg': '16px',
        'xl': '18px',
        '2xl': '20px',
        '3xl': '24px',
        '4xl': '32px',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '120': '30rem',
      },
    },
  },
  plugins: [],
}