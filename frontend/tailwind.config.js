/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#06090f",
          900: "#0b1220",
          800: "#111827"
        },
        mint: "#10b981",
        coral: "#fb7185",
        amber: "#f59e0b"
      }
    }
  },
  plugins: []
};

