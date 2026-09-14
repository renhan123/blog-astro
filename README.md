# CodeEcho · blog-astro

> 一个基于 Astro 构建的个人技术博客，围绕 **后端开发、工程实践、AI + Agent** 持续沉淀内容，并逐步演进为一个更有“知识库感”的个人站点。

- 🌐 Online: https://echocode.com.cn
- ⚙️ Stack: Astro 7 / Markdown / astro:content / RSS / Vercel Analytics
- 🎯 Focus: 技术写作、系列化内容组织、站内知识导航助手（MVP）

---

## 目录

- [项目简介](#项目简介)
- [当前特性](#当前特性)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [内容写作规范](#内容写作规范)
- [Open Graph 分享图](#open-graph-分享图)
- [部署说明](#部署说明)
- [路线图](#路线图)
- [维护建议](#维护建议)

---

## 项目简介

`blog-astro` 不是一个纯模板博客，而是一个正在持续演进的个人技术站点。

这个项目当前主要在做三件事：

1. **沉淀内容**：记录后端开发、数据库、架构、部署、AI 工程实践等真实经验。
2. **组织内容**：通过推荐页、系列页、标签页、归档页，把零散文章组织成可阅读的路径。
3. **增强发现能力**：通过搜索、相关推荐、站内助手等方式，帮助读者更快找到合适内容。

当前内容主线：

- **AI + 工程实践**
- **后端技术沉淀**
- **个人成长 / 工程方法论**（规划中）

如果把它放在一个更产品化的视角看，它更像是：

> 一个从“个人博客”逐步走向“个人知识库”的站点。

---

## 当前特性

### 内容展示

- 首页 Hero + 内容方向导航
- 文章卡片列表
- 分类筛选
- 前端即时搜索
- 标签云与标签详情页
- 归档页
- 推荐文章页
- 系列页

### 阅读体验

- Markdown 文章渲染
- 文章目录（TOC）
- 标签跳转
- 上一篇 / 下一篇导航
- 系列阅读导航
- 相关文章推荐
- 默认 OG 图与文章级分享图
- RSS / Sitemap / canonical / Open Graph / Twitter Card

### 站内知识助手（MVP）

- 页面地址：`/assistant/`
- 仅基于站内文章内容回答
- 不联网
- 适合做阅读导航、主题定位、文章推荐、概念差异说明
- 当前是轻量规则匹配版本，还不是完整 RAG / Agent 系统

---

## 技术栈

### Core

- [Astro](https://astro.build/)
- `astro:content`
- Markdown

### Integrations

- `@astrojs/rss`
- `@vercel/analytics`

### Output

- 静态站点输出
- `astro build` 产物位于 `dist/`

推荐本地环境：

- Node.js 20+
- npm 10+

---

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 启动本地开发

```bash
npm run dev
```

### 3. 构建生产版本

```bash
npm run build
```

### 4. 预览构建结果

```bash
npm run preview
```

### 常用命令

```bash
# 本地开发
npm run dev

# 生产构建
npm run build

# 本地预览
npm run preview

# 生成分享图（需 Python + Pillow）
python3 scripts/generate_share_covers.py
```

---

## 项目结构

```text
blog-astro/
├── astro.config.mjs               # Astro 配置（site / sitemap）
├── package.json                   # 依赖与脚本
├── public/                        # 静态资源
│   ├── images/                    # 文章图片
│   ├── og/                        # 站点与文章分享图
│   └── robots.txt
├── scripts/
│   └── generate_share_covers.py   # 生成 OG 分享图
├── src/
│   ├── components/                # 复用组件
│   ├── content/                   # Markdown 内容
│   ├── layouts/                   # 页面布局
│   ├── pages/                     # 路由页面
│   ├── styles/                    # 全局样式
│   ├── content.config.ts          # 内容 schema
│   └── utils.ts                   # 工具函数
└── dist/                          # 构建输出目录
```

---

## 页面说明

| 路由 | 说明 |
|---|---|
| `/` | 首页，包含内容方向导航、搜索、筛选、文章列表 |
| `/blog/[slug]/` | 文章详情页 |
| `/tags/` | 标签云页 |
| `/tags/[tag]/` | 标签详情页 |
| `/archive/` | 归档页 |
| `/featured/` | 推荐文章页 |
| `/series/` | 系列页 |
| `/assistant/` | 站内知识助手 MVP |
| `/about/` | 关于页 |
| `/rss.xml` | RSS 订阅 |
| `/sitemap.xml` | 站点地图 |

---

## 内容写作规范

文章目录：

```text
src/content/blog/*.md
```

当前使用 `src/content.config.ts` 对 frontmatter 做 schema 约束。

### Frontmatter 示例

```yaml
---
title: 后端开发如何借助 AI 从 0 到 1 搭建个人博客
description: 作为一名以后端开发为主、前端经验有限的开发者，我是如何借助 AI 把博客真正上线的。
pubDate: 2026-09-03
category: backend
readTime: 13 分钟
tags:
  - AI
  - Astro
  - Vercel
draft: false
series: ai-engineering
seriesTitle: AI + 工程实践
seriesOrder: 1
featured: true
related:
  - loop-to-graph-engineering
---
```

### 字段说明

| 字段 | 说明 |
|---|---|
| `title` | 文章标题 |
| `description` | 文章摘要 |
| `pubDate` | 发布日期 |
| `category` | 分类，当前支持 `backend` / `frontend` / `devops` / `database` |
| `readTime` | 可选，手动设置阅读时长 |
| `tags` | 标签数组 |
| `draft` | 是否为草稿 |
| `series` | 系列标识 |
| `seriesTitle` | 系列展示标题 |
| `seriesOrder` | 系列内顺序 |
| `featured` | 是否出现在推荐页 |
| `related` | 相关推荐 slug 列表 |

> 如果未填写 `readTime`，页面会根据正文内容自动估算阅读时长。

### 当前搜索能力说明

首页当前的前端搜索主要基于：

- 标题
- 摘要
- 标签

它还不是全文检索系统，这一点后续可以继续升级。

---

## Open Graph 分享图

项目自带分享图生成脚本：

```bash
python3 scripts/generate_share_covers.py
```

生成结果：

- 站点默认分享图：`public/og/site-cover.png`
- 文章分享图：`public/og/posts/*.png`

### 依赖

```bash
pip3 install pillow
```

> 当前脚本默认使用 macOS 系统字体路径；如果迁移到其他环境，可能需要调整字体配置。

---

## 部署说明

这是一个静态站点项目，适合部署到：

- Vercel
- Netlify
- GitHub Pages
- 任意支持静态资源托管的平台

当前配置更适合直接部署到 **Vercel**。

基本流程：

1. 推送代码到 Git 仓库
2. 执行 `npm install`
3. 执行 `npm run build`
4. 发布 `dist/` 输出结果

站点配置位于：

```js
// astro.config.mjs
site: 'https://echocode.com.cn'
```

---

## 路线图

接下来比较自然的演进方向包括：

- [ ] 持续补齐更多系列文章
- [ ] 打磨 About 页的人设与个人介绍
- [ ] 优化首页搜索，逐步从前端匹配走向更强的检索能力
- [ ] 继续增强相关文章与阅读路径推荐
- [ ] 将 `/assistant/` 从 MVP 升级为更完整的站内问答 / RAG 版本
- [ ] 补齐更多文章级 OG 图和内容资产

---

## 维护建议

如果你是这个项目未来的维护者，建议优先阅读以下文件：

- `src/content.config.ts`：内容字段定义
- `src/layouts/BaseLayout.astro`：全站布局与 SEO Meta
- `src/pages/index.astro`：首页结构与搜索/筛选逻辑
- `src/pages/blog/[slug].astro`：文章详情页主逻辑
- `src/pages/assistant.astro`：知识助手 MVP 逻辑
- `scripts/generate_share_covers.py`：分享图生成逻辑

这几个文件基本覆盖了当前项目最核心的能力。

---

## 备注

这个项目当前已经不是“刚搭起来的博客模板”，而是一个已经可以稳定写作、构建、发布，并持续演进的个人博客项目。

如果后续继续补齐内容与站内导航能力，它会越来越接近一个真正可持续维护的个人知识站点。

