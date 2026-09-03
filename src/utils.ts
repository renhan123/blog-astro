export const categoryLabels: Record<string, string> = {
  backend: '后端',
  frontend: '前端',
  devops: 'DevOps',
  database: '数据库',
};

export function formatDate(date: Date) {
  return date.toISOString().slice(0, 10);
}

export function formatDateZh(date: Date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}年${m}月${d}日`;
}

export function getPostSlug(id: string) {
  return id.replace(/.[^.]+$/, '');
}

export function getTagSlug(tag: string) {
  return tag
    .trim()
    .toLowerCase()
    .replace(/[\s\/]+/g, '-')
    .replace(/[^\p{L}\p{N}-]+/gu, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

/**
 * 根据文章正文自动计算阅读时间
 * 中文字符 + 英文单词，按每分钟 300 字/词计算
 */
export function calculateReadTime(body: string): string {
  // 移除 frontmatter
  const content = body.replace(/^---[\s\S]*?---/, '');
  // 统计中文字符
  const cnChars = content.match(/[\u4e00-\u9fa5]/g)?.length || 0;
  // 统计英文单词
  const enWords = content.match(/[a-zA-Z]+/g)?.length || 0;
  // 总阅读时间（分钟）
  const minutes = Math.max(1, Math.ceil((cnChars + enWords) / 300));
  return `${minutes} 分钟`;
}
