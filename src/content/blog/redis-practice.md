---
title: Redis 实战：缓存策略、数据结构与性能调优
description: Redis 几乎是所有高并发系统的标配。但用好 Redis 不仅仅是会 SET/GET，选对数据结构、设计好缓存策略才是关键。
pubDate: 2026-07-28
category: database
readTime: 16 分钟
tags:
  - Redis
  - 缓存
  - 性能调优
draft: false
---

## 缓存策略

最常见的缓存策略是 Cache-Aside Pattern：

1. 读请求先查缓存，命中则返回
2. 未命中则查数据库，写入缓存，返回
3. 写请求先更新数据库，再删除缓存

> 注意是删除缓存而不是更新缓存。删除是幂等的，而更新可能产生数据不一致。

### 为什么是"先更新数据库，再删缓存"

先删缓存再更新数据库存在明显竞态：删除后、数据库更新完成前，另一个读请求未命中缓存，把旧数据写入缓存，此后一直是脏数据。而"先更新数据库，再删缓存"的窗口期极短（要求读请求恰好读到旧库数据、又恰好没命中旧缓存），概率低得多，但没有绝对安全的方案。

更进一步，如果删除缓存这一步失败，数据依然不一致。可以引入消息队列做删除重试，或使用 Canal 订阅 binlog 异步删除，把"最终一致"做扎实。

## 缓存问题与解决方案

- 缓存穿透：查询不存在的数据，可使用布隆过滤器或空值缓存
- 缓存击穿：热点 key 过期，可使用互斥锁或永不过期策略
- 缓存雪崩：大量 key 同时过期，可在过期时间上增加随机值

三种问题容易混淆，一个记忆方法：穿透是"查不存在的数据"（请求穿过了缓存和数据库两层防线），击穿是"单个热点 key 失效"（被高并发流量击穿一点），雪崩是"大面积同时失效"（整体崩塌）。

~~~bash
# 空值缓存防穿透：短 TTL 防止被恶意 key 撑爆内存
SET user:404 "" EX 30

# 互斥锁防击穿：拿不到锁的请求短暂等待后重试
SET lock:hotkey 1 NX EX 3
~~~

## 数据结构选择

Redis 有丰富的数据结构，选对结构能极大提升效率。

~~~bash
ZADD leaderboard 100 "user1"
ZADD leaderboard 200 "user2"
ZRANGE leaderboard 0 9 REV
INCR page:views:home
LPUSH queue "task1"
BRPOP queue 0
~~~

### 各数据结构的典型场景

- **String**：缓存对象 JSON、计数器（INCR/INCRBY 原子自增）、分布式锁
- **Hash**：对象的多字段读写，可以只更新单个字段而不用序列化整个对象
- **List**：消息队列、最新动态列表，LPUSH + BRPOP 实现简单阻塞队列
- **Set**：去重、共同关注（SINTER 交集）、抽奖（SPOP 随机弹出）
- **ZSet**：排行榜、延迟队列（score 存执行时间戳，定时 ZRANGEBYSCORE 捞任务）

### 延迟队列的实现示例

~~~bash
# 订单 30 分钟未支付自动取消：score 为到期时间戳
ZADD order:delay 1735689600 "order:1001"
ZADD order:delay 1735691400 "order:1002"

# 消费者每秒轮询，只取已到期的任务
ZRANGEBYSCORE order:delay 0 1735689700 LIMIT 0 10
# 处理成功后移除
ZREM order:delay "order:1001"
~~~

### 一个容易忽视的坑：bigkey

String 超过 10KB、集合类型元素超过 5000 个就算 bigkey。危害包括：

- 操作耗时上升，阻塞单线程的 Redis
- 集群模式下数据倾斜
- 删除大 key 时（尤其 4.0 之前）同步阻塞主线程

~~~bash
# 线上排查 bigkey，只扫描从库
redis-cli --bigkeys -i 0.1

# 4.0+ 用 UNLINK 异步删除替代 DEL
UNLINK huge:list:key
~~~

## 分布式锁的正确姿势

Redis 实现分布式锁看似简单，细节却很多：

~~~bash
# 加锁：NX 保证互斥，EX 设置过期防止死锁
SET lock:order:1001 "unique-token-abc" NX EX 10
~~~

两个关键细节：

1. **value 必须是唯一标识**（如 UUID）：防止 A 的锁超时自动释放后，B 拿到锁，A 执行 DEL 时误删 B 的锁。删除前要用 Lua 脚本校验 value
2. **锁的续期**：业务执行超过锁的 TTL 时，需要看门狗机制自动续期，这正是 Redisson 的 watchDog 做的事

~~~lua
-- 释放锁：校验持有者再删除，必须原子执行
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
~~~

如果业务对锁的正确性要求极高（丢失锁会造成资损），考虑 RedLock 或改用 etcd/ZooKeeper 这类强一致组件，Redis 单实例锁在主从切换时可能同时被两个客户端持有。

## 持久化与高可用

- **RDB**：定时快照，文件小恢复快，但会丢最后一次快照之后的数据。适合容忍分钟级丢失的场景
- **AOF**：追加写命令，`appendfsync everysec` 是常见的折中配置，最多丢 1 秒数据
- **混合持久化**（4.0+）：RDB 做全量 + AOF 做增量，兼顾恢复速度和数据安全，推荐开启

~~~bash
# redis.conf 关键配置
appendonly yes
appendfsync everysec
aof-use-rdb-preamble yes
~~~

高可用部署上，**哨兵（Sentinel）** 负责主从自动故障转移，**Cluster** 则解决容量和写性能的水平扩展（16384 个 slot 分布到多节点）。集群模式下注意：多 key 操作（MGET、事务、Lua）要求 key 落在同一个 slot，需要用 hash tag `{user:1001}:profile` 强制路由。

## 性能调优清单

线上 Redis 变慢时按这个顺序排查：

1. **慢查询日志**：`SLOWLOG GET 10` 找出耗时命令，优先处理 KEYS、SMEMBERS 这类 O(N) 命令，禁用 KEYS *
2. **持久化阻塞**：AOF 的 fsync、RDB 的 fork 都可能阻塞主线程，关注 `latest_fork_usec` 指标
3. **内存与淘汰**：`maxmemory` 配合 `allkeys-lru` 淘汰策略，避免用默认的 `noeviction` 导致写入报错
4. **网络与连接数**：`INFO clients` 关注 blocked_clients，避免大量 BRPOP 空等占满连接池
5. **避免热点 key**：单 key 压到单核上限（约 10 万 QPS）时，考虑本地缓存兜底或 key 打散多副本

~~~bash
# 实时监控命令耗时
redis-cli --latency
redis-cli --latency-history
~~~

## 总结

Redis 是一个工具箱，每一类问题都有对应的数据结构和策略。不要只用 String 类型，学会用合适的数据结构解决具体问题，避开 bigkey、热点 key、分布式锁这些常见的坑，才能真正发挥 Redis 的价值。缓存层面的所有设计，最终都围绕一个目标：让数据库不被打死，同时让用户看到的数据"足够新"。
