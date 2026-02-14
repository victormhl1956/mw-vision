/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        osint: {
          bg: '#0a0e27',
          panel: '#1a1f3a',
          card: 'rgba(26, 31, 58, 0.7)',
          cyan: '#00d4ff',
          red: '#ff3366',
          orange: '#ff9900',
          green: '#00ff88',
          purple: '#9d4edd',
          gold: '#ffd700',
          text: '#ffffff',
          'text-dim': '#a0a0b0',
          'text-muted': '#6b7280',
        },
      },
      fontFamily: {
        orbitron: ['Orbitron', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        sans: ['Inter', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-threat': 'linear-gradient(90deg, #00ff00, #ffff00, #ff9900, #ff0000)',
        'gradient-panel': 'linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(157, 78, 221, 0.1))',
      },
      animation: {
        'scanline': 'scanline 4s linear infinite',
        'fade-in': 'fade-in 0.15s ease-out forwards',
        'spin-slow': 'spin-slow 8s linear infinite',
      },
      keyframes: {
        scanline: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        'fade-in': {
          from: { opacity: '0', transform: 'translateY(4px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'spin-slow': {
          from: { transform: 'rotate(0deg)' },
          to: { transform: 'rotate(360deg)' },
        },
      },
    },
  },
  plugins: [],
}