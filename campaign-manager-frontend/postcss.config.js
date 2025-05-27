module.exports = {
  plugins: {
    // Try both standard module names and explicit paths
    tailwindcss: {},
    autoprefixer: {},
    // If the above fails, try explicit paths
    '/usr/local/lib/node_modules/tailwindcss': {},
    '/usr/local/lib/node_modules/autoprefixer': {},
  },
}
