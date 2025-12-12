/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Taxini Brand Colors (from your design)
        'taxini-dark': '#0a1f1a',      // Dark green background
        'taxini-dark-light': '#0f2920', // Lighter dark green
        'taxini-yellow': '#ffd000',     // Primary yellow
        'taxini-yellow-dark': '#e6bb00', // Darker yellow for hover
        'taxini-green': '#1a4d3a',      // Medium green
        'taxini-text': '#ffffff',       // White text
        'taxini-text-gray': '#a0a0a0',  // Gray text
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'taxini': '0 10px 40px rgba(255, 208, 0, 0.1)',
        'taxini-lg': '0 20px 60px rgba(255, 208, 0, 0.15)',
      },
      borderRadius: {
        'taxini': '20px',
        'taxini-lg': '30px',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.4s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        }
      }
    },
  },
  plugins: [],
}
