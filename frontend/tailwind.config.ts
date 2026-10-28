import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Brand colors
        'brand-yellow': '#FFE135',
        'brand-pink': '#FF4D6D',
        'brand-green': '#00C875',
        'brand-blue': '#3A86FF',
        'brand-purple': '#8338EC',
        'brand-orange': '#FB5607',
        // Backgrounds — never pure white
        'bg-base': '#FFF9E6',
        'bg-card': '#FFFDF5',
        'bg-dark': '#0D0D0D',
        // Text
        'text-primary': '#0D0D0D',
        'text-muted': '#4A4A4A',
        // Borders
        'border-dark': '#1A1A1A',
      },
      fontFamily: {
        heading: ['"Space Grotesk"', 'sans-serif'],
        mono: ['"Space Mono"', 'monospace'],
        body: ['Inter', 'sans-serif'],
      },
      fontSize: {
        'display': ['3.5rem', { lineHeight: '1.1', fontWeight: '800' }],
        'h1': ['2.5rem', { lineHeight: '1.2', fontWeight: '700' }],
        'h2': ['2rem', { lineHeight: '1.25', fontWeight: '700' }],
        'h3': ['1.5rem', { lineHeight: '1.3', fontWeight: '600' }],
      },
      borderWidth: {
        '3': '3px',
        '4': '4px',
      },
      boxShadow: {
        // Hard neobrutalist shadows — no blur
        'neo': '4px 4px 0px #1A1A1A',
        'neo-lg': '6px 6px 0px #1A1A1A',
        'neo-sm': '2px 2px 0px #1A1A1A',
        'neo-yellow': '4px 4px 0px #FFE135',
        'neo-pink': '4px 4px 0px #FF4D6D',
        'neo-green': '4px 4px 0px #00C875',
        'neo-blue': '4px 4px 0px #3A86FF',
        'neo-purple': '4px 4px 0px #8338EC',
        'none': 'none',
      },
      borderRadius: {
        DEFAULT: '2px',
        'sm': '2px',
        'md': '4px',
        'lg': '4px',
        // Explicitly no large radii in neobrutalism
      },
      animation: {
        'bounce-in': 'bounceIn 200ms ease-out',
        'slide-up': 'slideUp 200ms ease-out',
        'shake': 'shake 300ms ease-in-out',
        'pop': 'pop 150ms ease-out',
      },
      keyframes: {
        bounceIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '70%': { transform: 'scale(1.05)' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(16px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        shake: {
          '0%, 100%': { transform: 'translateX(0)' },
          '20%': { transform: 'translateX(-4px)' },
          '40%': { transform: 'translateX(4px)' },
          '60%': { transform: 'translateX(-4px)' },
          '80%': { transform: 'translateX(4px)' },
        },
        pop: {
          '0%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.08)' },
          '100%': { transform: 'scale(1)' },
        },
      },
    },
  },
  plugins: [],
}

export default config
