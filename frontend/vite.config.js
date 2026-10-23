import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Backend the dev server proxies to. Override with BACKEND_URL if port 8000 is taken.
const backendUrl = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001,
    strictPort: true,
    host: true,
    proxy: {
      '/api': {
        target: backendUrl,
        changeOrigin: true,
        secure: false,
      },
      '/health': {
        target: backendUrl,
        changeOrigin: true,
        secure: false,
      }
    }
  },
  build: {
    outDir: 'dist',
  }
});