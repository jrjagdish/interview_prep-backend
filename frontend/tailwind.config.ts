import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './hooks/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      opacity: {
        3: '0.03',
        8: '0.08',
        12: '0.12',
        15: '0.15',
      },
      animation: {
        'wave-ring': 'wave-ring 2s ease-out infinite',
        'wave-ring-2': 'wave-ring 2s ease-out 0.4s infinite',
        'wave-ring-3': 'wave-ring 2s ease-out 0.8s infinite',
        'breathe': 'breathe 3s ease-in-out infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
      },
      keyframes: {
        'wave-ring': {
          '0%': { transform: 'scale(1)', opacity: '0.6' },
          '100%': { transform: 'scale(2)', opacity: '0' },
        },
        'breathe': {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.04)' },
        },
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 20px 4px rgba(99,102,241,0.4)' },
          '50%': { boxShadow: '0 0 40px 12px rgba(99,102,241,0.7)' },
        },
      },
    },
  },
  plugins: [],
}
export default config
