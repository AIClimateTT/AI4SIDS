/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import { devtools } from '@tanstack/devtools-vite'
import { tanstackStart } from '@tanstack/react-start/plugin/vite'
import viteReact from '@vitejs/plugin-react'
import viteTsConfigPaths from 'vite-tsconfig-paths'
import tailwindcss from '@tailwindcss/vite'
import { nitro } from 'nitro/vite'
import { tanstackRouter } from '@tanstack/router-plugin/vite'
const config = defineConfig({
  plugins: [
    tailwindcss(),
    // tanstackStart(),
    // nitro({ 
    //   preset: 'node-server',            
    // }),
    tanstackRouter({ target: 'react', autoCodeSplitting: true }),
    devtools(),
    viteTsConfigPaths({
      projects: ['./tsconfig.json'],
    }),
    
    viteReact(),
  ],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest.setup.ts'],
  },
})

export default config