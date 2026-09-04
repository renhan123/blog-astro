import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://echocode.com.cn',
  sitemap: true,
  legacy: {
    collectionsBackwardsCompat: true,
  },
});
