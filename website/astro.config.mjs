// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// GitHub Pages project sites live under /<repository>/.
// Override with ATLAS_SITE / ATLAS_BASE (the deploy workflow sets them).
const site = process.env.ATLAS_SITE || 'https://xiaobo-coder.github.io';
const base = process.env.ATLAS_BASE ?? '/AI4SE-Atlas';

export default defineConfig({
  site,
  base,
  trailingSlash: 'ignore',
  build: { format: 'directory' },
  vite: { plugins: [tailwindcss()] },
});
