/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "nexus-void":    "#040408",
        "nexus-deep":    "#080b14",
        "nexus-surface": "#0d1117",
        "nexus-elevated":"#13192a",
        "nexus-text":    "#e2e8f0",
        "nexus-muted":   "#8892a4",
        "nexus-primary": "#6366f1",
        "nexus-accent":  "#8b5cf6",
        "nexus-cyan":    "#06b6d4",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Consolas", "monospace"],
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-nexus":  "linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%)",
      },
      animation: {
        "glow-pulse": "nexus-glow-pulse 3s ease-in-out infinite",
        "float":      "float 4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
