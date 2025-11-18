/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Cinnamon Brand Colors
        purple: {
          primary: '#5A3082',
          secondary: '#6B2C91',
          light: '#7A4BA3',
          lighter: '#8E5BB8',
          dark: '#4A1F6D',
        },
        success: {
          light: '#E8F5E9',
          DEFAULT: '#2E7D32',
          dark: '#1B5E20',
        },
        warning: {
          light: '#FFF3E0',
          DEFAULT: '#E65100',
          dark: '#BF360C',
        },
        neutral: {
          50: '#FAFAFA',
          100: '#F5F5F5',
          200: '#E0E0E0',
          300: '#BDBDBD',
          400: '#9E9E9E',
          500: '#757575',
          600: '#616161',
          700: '#424242',
          800: '#333333',
          900: '#212121',
        },
      },
      fontFamily: {
        inter: ['var(--font-inter)', 'sans-serif'],
        poppins: ['var(--font-poppins)', 'sans-serif'],
      },
      keyframes: {
        slideUp: {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        slideInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          from: { opacity: '0', transform: 'translateY(10px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        bubbleSlideFromLeft: {
          from: { opacity: '0', transform: 'translateX(-20px)' },
          to: { opacity: '1', transform: 'translateX(0)' },
        },
        typing: {
          '0%, 60%, 100%': { opacity: '0.3', transform: 'translateY(0)' },
          '30%': { opacity: '1', transform: 'translateY(-4px)' },
        },
      },
      animation: {
        slideUp: 'slideUp 0.3s ease-out',
        slideInUp: 'slideInUp 0.4s ease-out',
        fadeIn: 'fadeIn 0.3s ease-out',
        bubbleSlide: 'bubbleSlideFromLeft 0.5s ease-out',
        typing: 'typing 1.4s infinite',
      },
      borderRadius: {
        'skewed': '20px 0 20px 0',
        'skewed-sm': '18px 0 18px 0',
      },
    },
  },
  plugins: [],
}
