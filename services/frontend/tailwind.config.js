/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Pretendard', 'Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        display: ['Raleway', 'Montserrat', 'Pretendard', 'sans-serif'],
      },
      colors: {
        // Legacy primary (기존 코드 호환용)
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        // 새로운 Ocean 컬러 (메인)
        ocean: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#b9e5fe',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',  // 메인 블루
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        // Wave 컬러 (서브)
        wave: {
          50: '#f0fdfa',
          100: '#ccfbf1',
          200: '#99f6e4',
          300: '#5eead4',
          400: '#2dd4bf',
          500: '#14b8a6',  // 메인 티알
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',
        },
      },
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
        'glow': '0 0 15px rgba(14, 165, 233, 0.3)',
        'wave': '0 4px 20px -2px rgba(20, 184, 166, 0.2)',
      },
      animation: {
        'wave': 'wave 3s ease-in-out infinite',
        'ripple': 'ripple 0.6s linear',
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        wave: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        ripple: {
          '0%': { transform: 'scale(0)', opacity: '1' },
          '100%': { transform: 'scale(4)', opacity: '0' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
      backgroundImage: {
        'gradient-ocean': 'linear-gradient(135deg, #0ea5e9 0%, #14b8a6 100%)',
        'gradient-wave': 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
      },
    },
  },
  plugins: [],
}
