// serve_build.js - Serve React build as Windows service
const express = require('express');
const path = require('path');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = 3000;
const HOST = '0.0.0.0'; // Listen on all interfaces

console.log('🚀 Starting Campaign Manager Frontend Service');
console.log(`📁 Serving from: ${path.join(__dirname, 'dist')}`);
console.log(`🌐 Frontend will be available at: http://192.168.103.111:${PORT}`);

// Proxy API requests to Flask backend
app.use('/api', createProxyMiddleware({
    target: 'http://localhost:5000',
    changeOrigin: true,
    logLevel: 'info',
    onError: (err, req, res) => {
        console.error('Proxy Error:', err);
        res.status(500).json({ error: 'Backend service unavailable' });
    }
}));

// Serve static files from React build
app.use(express.static(path.join(__dirname, 'dist')));

// Handle React Router - send all requests to index.html
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

// Error handling
app.use((err, req, res, next) => {
    console.error('Server Error:', err);
    res.status(500).json({ error: 'Internal server error' });
});

// Start server
const server = app.listen(PORT, HOST, () => {
    console.log(`✅ Frontend service running on http://${HOST}:${PORT}`);
    console.log('🔗 API requests will be proxied to backend on port 5000');
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('🛑 Received SIGTERM, shutting down gracefully');
    server.close(() => {
        console.log('✅ Frontend service stopped');
        process.exit(0);
    });
});

process.on('SIGINT', () => {
    console.log('🛑 Received SIGINT, shutting down gracefully');
    server.close(() => {
        console.log('✅ Frontend service stopped');
        process.exit(0);
    });
});