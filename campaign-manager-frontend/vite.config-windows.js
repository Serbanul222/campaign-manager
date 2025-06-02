// Windows VM-specific Vite configuration
// This file is used when running on Windows VM
// Your original vite.config.js remains unchanged for localhost development

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
    // Listen on all network interfaces for Windows VM access
    host: '0.0.0.0',
    // Don't try to find another port if 5173 is in use
    strictPort: true,
    // Configure proxy to backend running in Docker
    proxy: {
      '/api': {
        target: 'http://backend:5000',  // Use Docker service name
        changeOrigin: true,
        secure: false,
        // Keep /api prefix as your backend expects it
        rewrite: (path) => path
      },
    },
    hmr: {
      // Allow HMR to work from any host
      port: 5173,
    },
    watch: {
      usePolling: true,
      interval: 1000,
    },
    cors: true,
  },
  // Define global constants for development
  define: {
    __API_URL__: '"http://localhost:5000"',  // Will be overridden by .env.windows
  }
});