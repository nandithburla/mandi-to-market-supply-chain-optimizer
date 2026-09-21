/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        agri: {
          50: "#f0fdf4",
          100: "#dcfce7",
          200: "#bbf7d0",
          300: "#86efac",
          400: "#4ade80",
          500: "#22c55e",
          600: "#16a34a",
          700: "#15803d",
          800: "#166534",
          900: "#14532d",
          950: "#052e16",
        },
        emerald: {
          DEFAULT: "#10b981",
          dark: "#064e3b",
          light: "#d1fae5",
        },
        amber: {
          DEFAULT: "#f59e0b",
          dark: "#78350f",
          light: "#fef3c7",
        },
        slate: {
          850: "#151e2e",
          900: "#0f172a",
          950: "#090d16",
        }
      },
      fontFamily: {
        sans: [
          "Outfit",
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(0, 0, 0, 0.08)",
        "glass-dark": "0 8px 32px 0 rgba(0, 0, 0, 0.37)",
        "glow-emerald": "0 0 20px -5px rgba(16, 185, 129, 0.3)",
      }
    },
  },
  plugins: [],
}
