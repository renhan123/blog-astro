<div align="right">
  <a href="./README_EN.md">English</a> | 中文
</div>

<div align="center">
  <img src="./docs/images/readme-banner.png" alt="CodeEcho cover" width="100%" />
  <h1>CodeEcho · blog-astro</h1>
  <h3>📝 一个持续沉淀后端开发、工程实践与 AI 思考的个人技术博客</h3>
  <p><em>从个人博客出发，逐步演进为更有“知识库感”的个人站点。</em></p>

  <img src="https://img.shields.io/github/stars/renhan123/blog-astro?style=flat&logo=github" alt="GitHub stars" />
  <img src="https://img.shields.io/github/forks/renhan123/blog-astro?style=flat&logo=github" alt="GitHub forks" />
  <img src="https://img.shields.io/badge/framework-Astro-ff5d01?style=flat&logo=astro" alt="Astro" />
  <img src="https://img.shields.io/badge/content-Markdown-brightgreen?style=flat" alt="Markdown" />
  <img src="https://img.shields.io/badge/language-Chinese-green?style=flat" alt="Language" />
  <a href="https://github.com/renhan123/blog-astro"><img src="https://img.shields.io/badge/GitHub-Project-blue?style=flat&logo=github" alt="GitHub Project" /></a>
  <a href="https://echocode.com.cn"><img src="https://img.shields.io/badge/在线访问-CodeEcho-success?style=flat&logo=google-chrome" alt="Online Site" /></a>
</div>

---

## 🎯 项目介绍

**CodeEcho / blog-astro** 是一个基于 **Astro** 构建的个人技术博客项目。

这个项目并不只是一个简单的博客模板，而是希望围绕“**技术内容沉淀 + 内容组织 + 阅读导航**”逐步演进成一个更完整的个人知识站点。

当前主要聚焦在这些方向：

- **后端开发**：数据库、缓存、并发、架构演进
- **工程实践**：部署、性能、系统设计、真实踩坑总结
- **AI + Agent**：AI Coding、Agent 工程化、知识助手探索

如果用一句话概括它：

> 这是一个从“写文章”走向“组织知识”的个人博客项目。

---

## 📚 快速开始

### 在线访问

- **博客地址**：https://echocode.com.cn
- **仓库地址**：https://github.com/renhan123/blog-astro

### 本地运行

#### 1. 安装依赖

```bash
npm install
```

#### 2. 启动开发环境

```bash
npm run dev
```

#### 3. 构建生产版本

```bash
npm run build
```

#### 4. 预览构建结果

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

# 生成 Open Graph 分享图（需 Python + Pillow）
python3 scripts/generate_share_covers.py
```

---

## ✨ 你能在这个项目里看到什么？

- 📖 **真实技术写作**：不是 demo 文案，而是围绕后端、工程、AI 的持续写作
- 🧭 **内容组织能力**：推荐页、系列页、标签页、归档页共同形成阅读路径
- 🔍 **站内发现能力**：首页搜索、标签导航、相关文章推荐、知识助手
- 🖼️ **分享与 SEO 基础设施**：RSS、Sitemap、OG 图、canonical、Twitter Card
- 🤖 **站内知识助手 MVP**：尝试把博客从“内容展示”升级到“内容导航”

---

## 📖 内容导航

### 推荐阅读入口

| 入口 | 说明 | 状态 |
| --- | --- | --- |
| [推荐文章](/featured/) | 第一次访问博客时最适合先看的代表性内容 | ✅ |
| [内容系列](/series/) | 按主题组织阅读路径 | ✅ |
| [标签页](/tags/) | 从标签维度快速发现相关文章 | ✅ |
| [归档页](/archive/) | 按时间线回看内容沉淀 | ✅ |
| [知识助手](/assistant/) | 基于站内文章的阅读导航助手 | ✅ MVP |

### 当前系列导航

| 系列 | 说明 | 当前文章数 | 状态 |
| --- | --- | --- | --- |
| AI + 工程实践 | 围绕 AI Coding、Agent 工程化、个人博客实践与方法沉淀 | 2 | ✅ |
| 后端技术沉淀 | 围绕数据库、缓存、并发、部署、架构等核心能力持续沉淀 | 5 | ✅ |
| 个人成长 / 工程方法论 | 更偏长期方法、学习路径、认知整理 | 0 | 🚧 规划中 |

### 当前文章目录

| 文章 | 分类 | 系列 | 发布日期 | 推荐 |
| --- | --- | --- | --- | --- |
| [后端开发如何借助 AI 从 0 到 1 搭建个人博客](./src/content/blog/ai-build-personal-blog.md) | backend | AI + 工程实践 | 2026-09-03 | ⭐ |
| [从 Loop 到 Graph Engineering 的演进思考与实战](./src/content/blog/loop-to-graph-engineering.md) | backend | AI + 工程实践 | 2026-09-03 | ⭐ |
| [深入理解微服务架构：从单体到分布式的演进之路](./src/content/blog/microservice-evolution.md) | backend | 后端技术沉淀 | 2026-08-25 |  |
| [React 性能优化实战：从渲染机制到工程实践](./src/content/blog/react-performance.md) | frontend | - | 2026-08-20 |  |
| [Docker 容器化部署指南：从 Dockerfile 到生产环境](./src/content/blog/docker-deploy-guide.md) | devops | 后端技术沉淀 | 2026-08-15 |  |
| [MySQL 索引优化：从 B+ 树到执行计划分析](./src/content/blog/mysql-indexing.md) | database | 后端技术沉淀 | 2026-08-10 |  |
| [Go 并发编程：Goroutine、Channel 与 Context 深入解析](./src/content/blog/go-concurrency.md) | backend | 后端技术沉淀 | 2026-08-05 |  |
| [Redis 实战：缓存策略、数据结构与性能调优](./src/content/blog/redis-practice.md) | database | 后端技术沉淀 | 2026-07-28 |  |

---

## 🧱 核心能力

### 内容展示

- 首页 Hero 区与内容方向导航
- 文章列表与卡片式展示
- 分类筛选
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
- 阅读时长估算

### 站内知识助手（MVP）

- 路由：`/assistant/`
- 只基于站内文章内容回答
- 不联网
- 适合做阅读导航、主题定位、相关文章推荐
- 当前是轻量规则匹配版本，后续可升级为更完整的 RAG / Agent 版本

### SEO / 分享能力

- RSS
- Sitemap
- canonical
- Open Graph
- Twitter Card
- 站点默认分享图 + 文章级分享图

---

## 📄 页面导航

| 页面 | 说明 |
| --- | --- |
| `/` | 首页，包含内容方向导航、搜索、筛选与文章列表 |
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

## 🗂️ 项目结构

```text
blog-astro/
├── astro.config.mjs               # Astro 配置（site / sitemap）
├── package.json                   # 依赖与脚本
├── public/                        # 静态资源
│   ├── images/                    # 文章插图
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

## ✍️ 内容写作方式

文章位于：

```text
src/content/blog/*.md
```

通过 `src/content.config.ts` 中的 schema 进行约束。

### Frontmatter 示例

```yaml
---
title: 后端开发如何借助 AI 从 0 到 1 搭建个人博客
description: 作为一名以后端开发为主、前端经验有限的开发者，我是如何借助 AI，把博客真正上线的。
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

### 当前支持字段

- `title`：文章标题
- `description`：文章摘要
- `pubDate`：发布日期
- `category`：分类，当前支持 `backend / frontend / devops / database`
- `readTime`：可选，手动设置阅读时长
- `tags`：标签数组
- `draft`：是否草稿
- `series`：系列标识
- `seriesTitle`：系列展示标题
- `seriesOrder`：系列内顺序
- `featured`：是否出现在推荐页
- `related`：相关推荐文章 slug 列表

> 如果未填写 `readTime`，页面会根据正文内容自动估算阅读时长。

### 当前搜索说明

首页当前搜索主要基于：

- 标题
- 摘要
- 标签

它现在还不是全文检索系统，后续可以继续升级。

---

## 🖼️ Open Graph 分享图

项目内置了分享图生成脚本：

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

## 🚀 部署说明

这是一个静态站点项目，适合部署到：

- Vercel
- Netlify
- GitHub Pages
- 任意支持静态资源托管的平台

当前配置更适合直接部署到 **Vercel**。

基础流程：

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

## 🛣️ 下一步规划

- [ ] 持续补齐更多系列文章
- [ ] 打磨 About 页的人设与介绍
- [ ] 优化首页搜索，逐步走向更强的检索能力
- [ ] 继续增强相关文章与阅读路径推荐
- [ ] 将 `/assistant/` 从 MVP 升级为更完整的站内问答 / RAG 版本
- [ ] 补齐更多文章级 OG 图与内容资产

---

## 🤝 如何贡献

欢迎任何形式的改进与建议：

- 🐛 报告 Bug
- 💡 提出功能建议
- 📝 优化 README、页面文案或内容结构
- ✍️ 增补文章内容与系列组织方式

如果你在阅读、写作、页面体验或 SEO 方面有好的建议，也欢迎提 Issue 或 PR。

---

## 🙌 维护建议

如果你是未来维护者，建议优先阅读这些文件：

- `src/content.config.ts`：内容字段定义
- `src/layouts/BaseLayout.astro`：全站布局与 SEO Meta
- `src/pages/index.astro`：首页结构与搜索/筛选逻辑
- `src/pages/blog/[slug].astro`：文章详情页主逻辑
- `src/pages/assistant.astro`：知识助手 MVP 逻辑
- `scripts/generate_share_covers.py`：分享图生成逻辑

---

## 🙏 致谢

这个项目当前以个人博客为主，但也借鉴了许多优秀的开源项目写法、文档组织方式和技术社区实践方式。

感谢所有帮助我持续完善博客内容、写作方向和工程体验的人。

<div align="center" style="margin-top: 20px;">
  <a href="https://github.com/renhan123/blog-astro/graphs/contributors">
    <img src="https://contrib.rocks/image?repo=renhan123/blog-astro" alt="contributors" />
  </a>
</div>

---

## Star History

<div align="center">
  <a href="https://star-history.com/#renhan123/blog-astro&Date">
    <img src="https://api.star-history.com/svg?repos=renhan123/blog-astro&type=Date" alt="Star History Chart" width="100%" />
  </a>
</div>

---

## 📜 开源说明

当前仓库暂未单独补充明确的 `LICENSE` 文件。

如果你希望把它作为长期维护的公开项目，建议后续补充一个明确的开源协议（例如 MIT、Apache-2.0 等），方便他人理解使用边界。

---

<div align="center">
  <p>⭐ 如果这个项目对你有帮助，欢迎点一个 Star。</p>
</div>

