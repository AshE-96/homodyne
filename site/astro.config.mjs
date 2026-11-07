import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://homodyne.m2gh.ir',
  trailingSlash: 'always',
  integrations: [
    sitemap({
      i18n: { defaultLocale: 'fa', locales: { fa: 'fa-IR', en: 'en' } },
      filter: (page) => !page.includes('/decks/'),
    }),
  ],
});
