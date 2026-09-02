---
title: MySQL 索引优化：从 B+ 树到执行计划分析
description: 慢查询是后端最常遇到的问题之一。理解索引的底层原理，学会看 EXPLAIN 执行计划，是解决慢查询的基本功。
pubDate: 2026-08-10
category: database
readTime: 18 分钟
tags:
  - MySQL
  - 索引
  - SQL优化
draft: false
---

## B+ 树索引结构

MySQL InnoDB 引擎使用 B+ 树作为索引结构。B+ 树的特点是：非叶子节点只存键值，所有数据都在叶子节点，叶子节点之间通过链表相连。

这意味着范围查询非常高效，找到起始叶子节点后，顺着链表遍历即可。

一棵 3 层的 B+ 树通常可以支撑千万级数据量：根节点常驻内存，一次主键查询最多只需要 3 次磁盘 IO（根页 + 中间页 + 叶子页）。这也解释了为什么 InnoDB 页大小是 16KB——保证单次 IO 读取的数据量与树的高度匹配。

InnoDB 有两类索引：

- **聚簇索引（主键索引）**：叶子节点存储完整的行数据，一张表只有一棵
- **二级索引（辅助索引）**：叶子节点存储索引列 + 主键值，查询时可能需要回表

~~~sql
-- name 上有二级索引时，下面两条 SQL 的执行路径完全不同
SELECT id, name FROM users WHERE name = 'alice';  -- 覆盖索引，无需回表
SELECT * FROM users WHERE name = 'alice';          -- 拿到 id 后回聚簇索引取整行
~~~

### 为什么推荐自增主键

主键的有序性直接影响写入性能。自增主键保证新数据总是追加到 B+ 树最右侧，页写满才分裂；而随机主键（如 UUID）会导致数据插入到已满的页中间，频繁触发页分裂和碎片，写入性能可能下降数倍。

## 联合索引与最左前缀原则

联合索引 a、b、c 实际上建立了 a、ab、abc 三个索引。查询时必须从最左列开始使用。

~~~sql
SELECT * FROM t WHERE a = 1;
SELECT * FROM t WHERE a = 1 AND b = 2;
SELECT * FROM t WHERE a = 1 AND b = 2 AND c = 3;
~~~

下面这些查询则无法完整使用索引 idx(a, b, c)：

~~~sql
SELECT * FROM t WHERE b = 2;                 -- 跳过了 a，无法走索引
SELECT * FROM t WHERE a = 1 ORDER BY c;      -- 只能用 a 过滤，排序需要 filesort
SELECT * FROM t WHERE a > 1 AND b = 2;       -- a 是范围查询，b 用不上索引
~~~

范围查询会导致其后的列失效，这也是"等值条件放前面、范围条件放后面"这条建索引经验的由来。

### 索引下推（ICP）

MySQL 5.6 引入的 Index Condition Pushdown 允许在存储引擎层使用索引中已有的列做过滤，减少回表次数。对于 `WHERE a = 1 AND c = 3`，虽然 c 无法用于定位，但可以在索引层先过滤 c，只把同时满足的记录回表。

## 索引失效的常见场景

排查慢查询时优先检查这些"索引杀手"：

~~~sql
-- 1. 对索引列使用函数或表达式
SELECT * FROM users WHERE DATE(created_at) = '2026-08-10';
-- 改写为范围查询
SELECT * FROM users
WHERE created_at >= '2026-08-10 00:00:00'
  AND created_at <  '2026-08-11 00:00:00';

-- 2. 隐式类型转换（phone 是 varchar）
SELECT * FROM users WHERE phone = 13800001111;

-- 3. 前缀模糊匹配
SELECT * FROM users WHERE name LIKE '%alice%';
-- 后缀匹配可以走索引
SELECT * FROM users WHERE name LIKE 'alice%';

-- 4. OR 连接了无索引的列
SELECT * FROM users WHERE name = 'alice' OR age = 20;  -- age 无索引则全表扫描
~~~

## EXPLAIN 执行计划

用 EXPLAIN 查看查询的执行计划，重点关注 type、key、rows 和 Extra 等字段。

~~~sql
EXPLAIN SELECT * FROM orders WHERE user_id = 42 AND status = 'PAID';
~~~

### type 字段：访问类型的好坏

性能从好到差依次是：

| type | 含义 | 说明 |
| --- | --- | --- |
| system / const | 主键或唯一索引等值查询 | 最多一条记录，性能最优 |
| eq_ref | 关联查询时用主键或唯一索引 | JOIN 场景的最优情况 |
| ref | 普通二级索引等值查询 | 常见且可接受 |
| range | 索引范围扫描 | BETWEEN、>、< 等 |
| index | 扫描整棵索引树 | 比 ALL 略好，但仍需优化 |
| ALL | 全表扫描 | 必须优化 |

看到 ALL 和 index 就应该警惕，除非表数据量本身很小。

### Extra 字段的关键信号

- **Using index**：覆盖索引，无需回表，好信号
- **Using index condition**：索引下推生效
- **Using where**：服务层过滤，通常配合回表发生
- **Using filesort**：排序无法利用索引，数据量大时是性能隐患
- **Using temporary**：使用了临时表，常见于 GROUP BY / DISTINCT 未走索引

出现 filesort 和 temporary 时，考虑为 ORDER BY / GROUP BY 的列建立合适的联合索引。

### rows 与 filtered

rows 是预估扫描行数，filtered 是经过条件过滤后剩余的百分比。两者相乘就是预估返回行数。如果 rows 远大于实际返回行数，说明统计信息过期（可 `ANALYZE TABLE` 更新）或索引选择性差。

## 实战优化案例

一个真实场景：订单列表页查询从 800ms 优化到 15ms。

~~~sql
-- 原始查询：按用户查最近订单
SELECT * FROM orders
WHERE user_id = 42
ORDER BY created_at DESC
LIMIT 20;

-- EXPLAIN 显示 type=ref，Extra=Using filesort
-- 建立联合索引，让排序也走索引
ALTER TABLE orders ADD INDEX idx_user_created (user_id, created_at DESC);

-- 优化后：type=ref，Extra=Using index condition，无 filesort
~~~

再看深分页问题，`LIMIT 1000000, 20` 会扫描并丢弃前 100 万行：

~~~sql
-- 优化：基于游标的翻页，利用索引直接定位起点
SELECT * FROM orders
WHERE user_id = 42 AND id < 上一页最后一条的id
ORDER BY id DESC
LIMIT 20;
~~~

## 写索引时的权衡

索引不是越多越好。每个索引都是一棵需要维护的 B+ 树：

- 写入时所有索引都要更新，索引过多会拖慢 INSERT / UPDATE / DELETE
- 空间成本：二级索引可能占数据本身的 20%~50%
- 选择性低的列（如性别、状态）单独建索引意义不大，但作为联合索引的一部分配合高选择性列是合理的

定期用 `sys.schema_unused_indexes` 和 `information_schema.INDEX_STATISTICS`（或慢查询日志）审视冗余索引，该删就删。

## 总结

索引优化不是玄学，理解 B+ 树结构和最左前缀原则，掌握 EXPLAIN 的使用方法，绝大多数慢查询问题都能迎刃而解。记住三步法：先用慢查询日志定位问题 SQL，再用 EXPLAIN 分析访问路径，最后通过改写 SQL 或调整索引解决，并验证优化效果，非常棒的文章，大力支持，点赞点赞。
