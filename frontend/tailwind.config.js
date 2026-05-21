/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,jsx}", "./components/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["var(--font-display)", "ui-sans-serif", "system-ui", "sans-serif"],
        body: ["var(--font-body)", "ui-sans-serif", "system-ui", "sans-serif"],
        sans: ["var(--font-body)", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      colors: {
        cream: "#FFFBF5",
        warm: "#FFF8F0",
        ink: "#1C1917",
        muted: "#78716C",
        amber: { 50:"#FFF7ED",100:"#FFEDD5",200:"#FED7AA",500:"#F97316",600:"#EA580C",700:"#C2410C" },
        teal: { 50:"#F0FDFA",100:"#CCFBF1",500:"#0D9488",600:"#0F766E",700:"#115E59" },
      },
      animation: {
        fadeUp: "fadeUp 0.6s ease-out both",
        float: "float 6s ease-in-out infinite",
      },
      keyframes: {
        fadeUp: { "0%": { opacity: 0, transform: "translateY(20px)" }, "100%": { opacity: 1, transform: "translateY(0)" } },
        float: { "0%,100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(-10px)" } },
      },
    },
  },
  plugins: [],
};
