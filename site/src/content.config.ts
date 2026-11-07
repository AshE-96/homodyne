import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const link = z.object({ title: z.string(), url: z.string().url() });

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string().max(200),
    lang: z.enum(['fa', 'en']),
    translationKey: z.string(),
    hmd: z.string(),
    kind: z.enum(['companion', 'deep-dive']),
    date: z.coerce.date(),
    updated: z.coerce.date().optional(),
    tags: z.array(z.string()).default([]),
    sources: z.array(link).default([]),
    datasets: z.array(link.extend({ license: z.string().optional() })).default([]),
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };
