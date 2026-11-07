import { getCollection, type CollectionEntry } from 'astro:content';
import episodes from './data/episodes.json';
import type { Lang } from './i18n';

export type Episode = (typeof episodes)[number];
export type Post = CollectionEntry<'blog'>;

export { episodes };

export const postSlug = (p: Post) => p.id.split('/').slice(1).join('/');
export const postUrl = (p: Post) => `/${p.data.lang}/blog/${postSlug(p)}/`;
export const episodeUrl = (e: Episode, lang: Lang) => `/${lang}/episodes/${e.slug}/`;

// Scheduled publishing: a post goes live when its date arrives (the deploy workflow rebuilds daily).
// SHOW_ALL=1 shows future posts for local preview.
const now = Date.now();
export const isLive = (p: Post) => !p.data.draft && (process.env.SHOW_ALL === '1' || p.data.date.valueOf() <= now);

export async function posts(lang?: Lang) {
  const all = await getCollection('blog', (p) => isLive(p) && (!lang || p.data.lang === lang));
  return all.sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());
}

export async function translationOf(p: Post) {
  const all = await getCollection('blog', (q) => isLive(q));
  return all.find((q) => q.data.translationKey === p.data.translationKey && q.data.lang !== p.data.lang) ?? null;
}
