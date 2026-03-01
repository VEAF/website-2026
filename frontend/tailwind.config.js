/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        veaf: {
          50:  '#f0f8fd',
          100: '#d9eef9',
          200: '#b3ddf3',
          300: '#7ec7ed',
          400: '#4ab3e7',
          500: '#2fa4e7',
          600: '#1e8cc7',
          700: '#1a75a8',
          800: '#165e87',
          900: '#033c73',
        },
        success: {
          50:  '#f3f8ec',
          100: '#e2edcc',
          200: '#c5db99',
          500: '#73a839',
          600: '#628f30',
          700: '#5c862e',
          800: '#4a6b25',
        },
        warning: {
          50:  '#fef3e6',
          100: '#fde0c0',
          200: '#fbc180',
          500: '#dd5600',
          600: '#bc4900',
          700: '#b14500',
          800: '#8e3700',
        },
        danger: {
          50:  '#fceced',
          100: '#f7cdce',
          200: '#ef9b9e',
          500: '#c71c22',
          600: '#a9181d',
          700: '#9f161b',
          800: '#7f1216',
        },
      },
      backgroundImage: {
        'veaf-gradient': 'linear-gradient(145deg, #349aed 50%, #34d8ed 100%)',
        'veaf-gradient-dark': 'linear-gradient(#04519b, #033c73 60%, #02325f)',
        'veaf-section': 'linear-gradient(145deg, #3b9cea 50%, #3db8eb 100%)',
      },
    },
  },
  plugins: [],
}
