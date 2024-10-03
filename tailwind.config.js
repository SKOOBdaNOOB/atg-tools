/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/templates/**/*.html',
    './venv/lib/python3.12/site-packages/crispy_tailwind/templates/tailwind/**/*.html',
    // Add other paths as needed
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui'),
  ],
  daisyui: {
    themes: [
      {
        atgtheme: {
          "primary": "#1E3A8A",
          "secondary": "#9333EA",
          "accent": "#10B981",
          "neutral": "#3D4451",
          "base-100": "#FFFFFF",
          // Additional colors...
        },
      },
    ],
  },
}
