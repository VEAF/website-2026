import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { versionPlugin } from './vite-plugin-version'

export default defineConfig({
  plugins: [vue(), versionPlugin()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    hmr: {
      host: process.env.VIRTUAL_HOST || 'localhost',
      clientPort: 80,
    },
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
