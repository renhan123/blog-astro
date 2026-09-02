import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://echocode.com.cn',
  legacy: {
    collectionsBackwardsCompat: true,
  },
});
