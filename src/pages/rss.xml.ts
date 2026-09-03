import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { getPostSlug } from '../utils';

export async function GET(context: { site: string }) {
  const posts = (await getCollection('blog', ({ data }) => !data.draft)).sort(
    (a, b) => b.data.pubDate.getTime() - a.data.pubDate.getTime()
  );

  return rss({
    title: 'CodeEcho - 沉淀技术实践，构建个人知识库',
    description: '记录后端开发、工程实践与 AI 探索，把真实经验持续沉淀下来。',
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
