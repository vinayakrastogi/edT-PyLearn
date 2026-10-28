import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: env.PYLEARN_BACKEND_URL || 'http://127.0.0.1:8000',
        // Preserve the browser host for redirects and host-only session cookies.
        changeOrigin: false,
      },
    },
  },
  }
})
