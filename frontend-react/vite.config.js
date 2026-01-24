import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  // Load env variables
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    // If VITE_BASE_PATH is set (for GitHub Pages), use it. 
    // Otherwise, default to '/' (for Docker/Localhost)
    base: env.VITE_BASE_PATH || '/',
    server: {
      host: true,
      strictPort: true,
      port: 5173,
      watch: {
        usePolling: true
      }
    }
  }
})