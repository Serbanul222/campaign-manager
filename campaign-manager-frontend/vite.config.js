import { defineConfig } from 'vite';

// Try to import React plugin, but don't fail if it's not available
let reactPlugin = null;
try {
  reactPlugin = require('@vitejs/plugin-react');
} catch (e) {
  console.warn('React plugin not found, proceeding with basic configuration');
}

export default defineConfig({
  plugins: reactPlugin ? [reactPlugin()] : [],
  server: {
    // Explicitly set the port
    port: 5173,
    // Always listen on all network interfaces
    host: '0.0.0.0',
    // Don't try to find another port if 5173 is in use
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://backend:5000',
        changeOrigin: true,
        // Remove '/api' prefix when forwarding to the backend
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
    hmr: {
      // Use localhost instead of the container name
      host: 'localhost',
      port: 5173,
      // This tells the browser to connect to localhost instead of frontend
      clientPort: 5173
    },
    watch: {
      usePolling: true,
      interval: 1000,
    },
    cors: true,
  },
});