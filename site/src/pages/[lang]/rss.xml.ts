import rss from '@astrojs/rss';
import type { APIContext } from 'astro';
import { ui, langs, type Lang } from '../../i18n';
import { posts, postUrl } from '../../lib';

export const getStaticPaths = () => langs.map((lang) => ({ params: { lang } }));

export async function GET(context: APIContext) {
  const lang = context.params.lang as Lang;
  const t = ui[lang];
  return rss({
    title: `${t.site} · ${t.blog}`,
    description: t.tagline,
    site: context.site!,
    items: (await posts(lang)).map((p) => ({
      title: p.data.title,
      description: p.data.description,
      pubDate: p.data.date,
      link: postUrl(p),
      categories: p.data.tags,
    })),
    customData: `<language>${lang === 'fa' ? 'fa-IR' : 'en'}</language>`,
  });
}
