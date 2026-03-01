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
