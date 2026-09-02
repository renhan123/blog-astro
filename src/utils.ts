export const categoryLabels: Record<string, string> = {
  backend: '后端',
  frontend: '前端',
  devops: 'DevOps',
  database: '数据库',
};

export function formatDate(date: Date) {
  return date.toISOString().slice(0, 10);
}

export function getPostSlug(id: string) {
  return id.replace(/.[^.]+$/, '');
}
