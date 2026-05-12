import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    {
      name: 'serve-data',
      configureServer(server) {
        server.middlewares.use('/data', (req, res, next) => {
          import('fs').then(fs => {
            import('path').then(path => {
              const decodedUrl = decodeURIComponent(req.url || '');
              const dockerPath = '/data' + decodedUrl;
              const localPath = path.resolve(__dirname, '../data' + decodedUrl);
              
              const fileToServe = fs.existsSync(dockerPath) ? dockerPath : localPath;
              if (fs.existsSync(fileToServe)) {
                res.setHeader('Access-Control-Allow-Origin', '*');
                if (fileToServe.endsWith('.json')) res.setHeader('Content-Type', 'application/json');
                if (fileToServe.endsWith('.bin')) res.setHeader('Content-Type', 'application/octet-stream');
                if (fileToServe.endsWith('.mp3')) res.setHeader('Content-Type', 'audio/mpeg');
                fs.createReadStream(fileToServe).pipe(res);
              } else {
                next();
              }
            });
          });
        });
      }
    }
  ],
  server: {
    port: 3400,
    allowedHosts: ['s2.local'],
    fs: {
      allow: ['..', '/data']
    },
    proxy: {
      '/api': 'http://backend:8000'
    }
  }
})
