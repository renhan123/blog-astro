import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    category: z.enum(['backend', 'frontend', 'devops', 'database']),
    readTime: z.string().optional(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
    series: z.string().optional(),
    seriesTitle: z.string().optional(),
    seriesOrder: z.number().int().positive().optional(),
    featured: z.boolean().default(false),
    related: z.array(z.string()).default([]),
  }),
});

const translation = defineCollection({
  type: 'data',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    source: z.string().optional(),
    author: z.string().optional(),
    level: z.enum(['beginner', 'intermediate', 'advanced']).default('intermediate'),
    tags: z.array(z.string()).default([]),
    estimatedMinutes: z.number().int().positive().optional(),
    heroNote: z.string().optional(),
    publishedAt: z.coerce.date().optional(),
    sentences: z.array(
      z.object({
        id: z.string(),
        en: z.string(),
        zhReference: z.string(),
        note: z.string().optional(),
      })
    ).min(1),
  }),
});

export const collections = { blog, translation };
