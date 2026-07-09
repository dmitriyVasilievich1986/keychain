import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import { defineConfig, loadEnv } from 'vite';

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@components': resolve(__dirname, './src/components'),
        '@store': resolve(__dirname, './src/store'),
        '@pages': resolve(__dirname, './src/pages'),
        '@assets': resolve(__dirname, './src/assets'),
        '@utils': resolve(__dirname, './src/utils'),
      },
    },
    build: {
      outDir: '../static',
      emptyOutDir: false,
      sourcemap: env.VITE_SOURCEMAP === 'true',
      rollupOptions: {
        output: {
          assetFileNames: 'assets/[name]-[hash][extname]',
          chunkFileNames: 'assets/[name]-[hash].js',
          entryFileNames: 'assets/[name]-[hash].js',
        },
      },
    },
  };
});
