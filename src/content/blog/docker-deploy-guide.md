---
title: Docker 容器化部署指南：从 Dockerfile 到生产环境
description: Docker 已经是现代应用部署的标配。但写出一个高效的 Dockerfile 和搭建一套可靠的 CI/CD 流水线，中间有很多细节值得注意。
pubDate: 2026-08-15
category: devops
readTime: 14 分钟
tags:
  - Docker
  - DevOps
  - CI/CD
draft: false
---

## Dockerfile 最佳实践

一个好的 Dockerfile 应该构建快、镜像小、安全性高。几个关键点：

- 使用多阶段构建减小镜像体积
- 利用构建缓存：变化频率低的层放前面
- 使用 dockerignore 排除不必要的文件

~~~bash
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o server .

FROM alpine:3.19
RUN apk --no-cache add ca-certificates
WORKDIR /app
COPY --from=builder /app/server .
EXPOSE 8080
CMD ["./server"]
~~~

### 为什么要多阶段构建

第一阶段用完整的构建工具链（编译器、依赖库）产出二进制，第二阶段只拷贝二进制到干净的运行时镜像。Go 项目从 1GB+ 缩到 20MB 是常态。Node 项目同理——`node_modules` 里的 devDependencies 不应该进运行时镜像：

~~~bash
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
~~~

### 缓存友好的层排序

Docker 按层缓存，某层失效则其后所有层重建。`COPY go.mod go.sum` 和 `go mod download` 放在 `COPY . .` 之前，代码改动就不会触发依赖重新下载。同理，把最不常变的指令放前面，最常变的（源码拷贝）放最后。

### 安全加固细节

~~~dockerfile
# 1. 用非 root 用户运行
RUN addgroup -S app && adduser -S app -G app
USER app

# 2. 声明只读文件系统兼容性
VOLUME /tmp

# 3. 固定基础镜像版本，不用 latest（FROM alpine）
FROM alpine:3.19

# 4. 健康检查让编排系统感知进程假死
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget -qO- http://localhost:8080/healthz || exit 1
~~~

配合 `.dockerignore` 排除 `.git`、`node_modules`、`dist`、`.env` 等文件，既减小构建上下文体积，也避免敏感信息（`.env` 里的密钥）被意外打进镜像。

## docker-compose 本地编排

本地开发环境用 compose 定义多容器依赖，一条命令拉起完整技术栈：

~~~yaml
services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DB_HOST=postgres
      - REDIS_ADDR=redis:6379
    depends_on:
      postgres:
        condition: service_healthy
    develop:
      watch:
        - action: rebuild
          path: ./src

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: devpassword
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s

  redis:
    image: redis:7-alpine

volumes:
  pgdata:
~~~

注意 `depends_on` 默认只保证启动顺序，不保证服务就绪，配 healthcheck + `condition: service_healthy` 才能解决"应用比数据库先起来导致连接失败"的经典问题。

## 生产环境部署

生产环境推荐使用 Kubernetes 或 Docker Swarm 进行编排。镜像标签不要用 latest，用 git commit hash 或语义化版本号，确保可追溯。

### CI/CD 流水线设计

一个可靠的最小流水线长这样：

~~~yaml
stages: [test, build, deploy]

test:
  stage: test
  script: go test ./... -race -cover

build:
  stage: build
  script:
    - docker build -t registry.example.com/myapp:$CI_COMMIT_SHORT_SHA .
    - docker push registry.example.com/myapp:$CI_COMMIT_SHORT_SHA

deploy:
  stage: deploy
  script:
    - kubectl set image deployment/myapp myapp=registry.example.com/myapp:$CI_COMMIT_SHORT_SHA
  environment: production
  when: manual   # 生产发布保留人工确认
~~~

关键设计点：

- **一次构建，多处部署**：test、staging、production 用同一个镜像，区别只在配置。避免"测试环境构建的镜像和生产不一致"
- **配置与镜像分离**：数据库地址、密钥等通过环境变量或配置中心注入，不烧进镜像
- **回滚即改标签**：`kubectl rollout undo` 或把 deployment 指回上一个镜像 tag，10 秒内完成

### 健康检查与优雅停机

容器化后的优雅停机常被忽略。收到 SIGTERM 后应用应该：停止接收新请求 → 处理完存量请求 → 关闭连接池 → 退出。配合编排系统的 `terminationGracePeriodSeconds`（默认 30s）：

~~~yaml
livenessProbe:
  httpGet: { path: /healthz, port: 8080 }
  initialDelaySeconds: 10
readinessProbe:
  httpGet: { path: /readyz, port: 8080 }
  initialDelaySeconds: 5
~~~

readiness 和 liveness 的语义要分清：readiness 失败只是暂时摘除流量（比如依赖的数据库抖动），liveness 失败则会触发容器重启。把数据库连通性放 liveness 里，会造成数据库一抖动所有实例连环重启的事故。

## 常用排查命令速查

~~~bash
docker stats --no-stream          # 容器资源占用
docker logs -f --tail 100 <cid>   # 跟踪日志
docker exec -it <cid> sh          # 进入容器
docker system df                  # 磁盘占用（镜像/卷/缓存）
docker system prune -f            # 清理悬空资源
dive registry.example.com/myapp:v1  # 逐层分析镜像体积（需安装 dive）
~~~

## 总结

容器化的目标是让整个流程自动化、可重复、可回滚。每次部署都应该是无感的、安全的。记住三条底线：镜像不可变（配置外置）、版本可追溯（tag 用 commit hash）、异常可自愈（探针 + 优雅停机）。先在本地用 compose 把开发环境标准化，再逐步演进到 K8s，不必一步到位。
