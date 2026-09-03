import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { getPostSlug } from '../utils';

export async function GET(context: { site: string }) {
  const posts = (await getCollection('blog', ({ data }) => !data.draft)).sort(
    (a, b) => b.data.pubDate.getTime() - a.data.pubDate.getTime()
  );

  return rss({
    title: 'CodeEcho - 个人技术博客',
    description: '分享编程心得、技术笔记与工程实践',
    site: context.site,
    items: posts.map((post) => ({
      title: post.data.title,
      pubDate: post.data.pubDate,
      description: post.data.description,
      link: `/blog/${getPostSlug(post.id)}/`,
    })),
    customData: `<language>zh-CN</language>`,
  });
}
