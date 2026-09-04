import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { getPostSlug, getTagSlug } from '../utils';

function escapeXml(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

export const GET: APIRoute = async ({ site }) => {
  const siteUrl = site || new URL('https://echocode.com.cn');
  const posts = (await getCollection('blog', ({ data }) => !data.draft)).sort(
    (a, b) => b.data.pubDate.getTime() - a.data.pubDate.getTime()
  );

  const staticPages = [
    '/',
    '/about/',
    '/archive/',
    '/featured/',
    '/series/',
    '/tags/',
    '/rss.xml',
  ];

  const tags = new Set<string>();
  posts.forEach((post) => post.data.tags.forEach((tag) => tags.add(tag)));

  const urls = [
    ...staticPages.map((path) => ({
      loc: new URL(path, siteUrl).toString(),
      lastmod: new Date().toISOString(),
    })),
    ...posts.map((post) => ({
      loc: new URL('/blog/' + getPostSlug(post.id) + '/', siteUrl).toString(),
      lastmod: post.data.pubDate.toISOString(),
    })),
    ...Array.from(tags).map((tag) => ({
      loc: new URL('/tags/' + getTagSlug(tag) + '/', siteUrl).toString(),
      lastmod: new Date().toISOString(),
    })),
  ];

  const body = urls
    .map((item) => {
      return '  <url>\n'
        + '    <loc>' + escapeXml(item.loc) + '</loc>\n'
        + '    <lastmod>' + item.lastmod + '</lastmod>\n'
        + '  </url>';
    })
    .join('\n');

  const xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    + '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + body + '\n'
    + '</urlset>';

  return new Response(xml, {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
    },
  });
};

