---
title: Go 并发编程：Goroutine、Channel 与 Context 深入解析
description: Go 的并发模型是其最大的特色之一。CSP 模型通过 Channel 传递数据而非共享内存，让并发编程更安全更直观。
pubDate: 2026-08-05
category: backend
readTime: 15 分钟
tags:
  - Go
  - 并发
  - Context
draft: false
---

## Goroutine 基础

Goroutine 是 Go 的轻量级线程，由 Go runtime 调度而非操作系统。创建一个 goroutine 只需 go 关键字。

~~~go
go func() {
    fmt.Println("Hello from goroutine")
}()
~~~

goroutine 的初始栈只有 2KB（可动态增长到 1GB），而操作系统线程通常需要 1MB 以上的栈空间。这意味着单机上创建数十万个 goroutine 也不会造成太大压力。Go runtime 使用 GMP 模型（Goroutine、Machine、Processor）将大量 goroutine 复用到少量操作系统线程上， goroutine 的切换成本远低于线程上下文切换。

使用 goroutine 时需要注意主函数退出的问题：

~~~go
func main() {
    go func() {
        time.Sleep(1 * time.Second)
        fmt.Println("done") // 很可能永远不会执行
    }()
    // main 退出时所有 goroutine 都会被直接终止
}
~~~

正确的做法是用同步机制（WaitGroup、Channel）等待 goroutine 完成：

~~~go
var wg sync.WaitGroup

for i := 0; i < 5; i++ {
    wg.Add(1)
    go func(id int) {
        defer wg.Done()
        fmt.Println("worker", id)
    }(i)
}

wg.Wait()
~~~

> 经典陷阱：在循环变量上直接启动 goroutine。Go 1.22 之前，循环变量会被复用，所有 goroutine 可能拿到同一个值。老代码需要通过参数传递 `go func(id int)` 来规避，Go 1.22 起循环变量每次迭代都是新变量，这个问题已被修复。

## Channel 通信

Channel 是 goroutine 之间通信的管道。Go 推崇通过通信共享内存的理念。

~~~go
ch := make(chan string)

go func() {
    ch <- "hello"
}()

msg := <-ch
fmt.Println(msg)
~~~

无缓冲 channel 的发送和接收必须同时就绪，天然形成了同步点；带缓冲的 channel 则允许生产者和消费者解耦：

~~~go
// 缓冲为 3，写入 3 个以内不会阻塞
ch := make(chan int, 3)
ch <- 1
ch <- 2
fmt.Println(len(ch), cap(ch)) // 2 3
~~~

关于 channel 有几条重要规则：

- 向 nil channel 发送或接收会永久阻塞
- 向已关闭的 channel 发送会 panic
- 从已关闭的 channel 接收会立即返回零值，可通过 `v, ok := <-ch` 判断是否关闭
- 关闭 channel 的责任应该由发送方承担，且不应重复关闭

一个优雅的关闭模式是用单独的 done channel 通知退出：

~~~go
func worker(ch <-chan int, done <-chan struct{}) {
    for {
        select {
        case v := <-ch:
            fmt.Println("received:", v)
        case <-done:
            fmt.Println("worker exit")
            return
        }
    }
}
~~~

## select 多路复用

当需要同时监听多个 channel 时，用 select。

~~~go
select {
case msg := <-ch1:
    fmt.Println("ch1:", msg)
case msg := <-ch2:
    fmt.Println("ch2:", msg)
case <-time.After(5 * time.Second):
    fmt.Println("timeout")
}
~~~

select 有几个实用技巧：

- `default` 分支让 select 变成非阻塞操作，常用于尝试性发送或接收
- 空 `select{}` 会永久阻塞
- `time.After` 每次调用都会创建新的 timer，在高频循环中应使用 `time.NewTimer` 复用，避免内存压力

~~~go
// 非阻塞发送
select {
case ch <- task:
    // 提交成功
default:
    // 队列已满，降级处理
    fmt.Println("queue full, drop task")
}
~~~

## 常见并发模式

### worker pool 模式

用固定数量的 goroutine 处理任务队列，避免无限制地创建 goroutine 把下游打挂：

~~~go
func workerPool(jobs <-chan Job, results chan<- Result, workers int) {
    var wg sync.WaitGroup
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobs {
                results <- process(job)
            }
        }()
    }
    wg.Wait()
    close(results)
}
~~~

### pipeline 模式

把处理流程拆成多个 stage，每个 stage 一组 goroutine，通过 channel 串联：

~~~go
nums := make(chan int)
squared := make(chan int)

go func() {
    defer close(nums)
    for i := 1; i <= 5; i++ {
        nums <- i
    }
}()

go func() {
    defer close(squared)
    for n := range nums {
        squared <- n * n
    }
}()

for s := range squared {
    fmt.Println(s)
}
~~~

### errgroup 并发编排

标准库 `golang.org/x/sync/errgroup` 提供了带错误传播和取消的并发控制，是手动管理 goroutine 的现代化替代：

~~~go
g, ctx := errgroup.WithContext(ctx)

for _, url := range urls {
    url := url
    g.Go(func() error {
        return fetch(ctx, url)
    })
}

if err := g.Wait(); err != nil {
    // 任意一个失败，ctx 会被取消，其余任务提前退出
    return err
}
~~~

## Context 控制生命周期

context.Context 用于控制 goroutine 的生命周期，实现超时和取消传播。几乎所有接受 ctx 的函数都应该把它作为第一个参数，并持续向下传递。

~~~go
ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
defer cancel()

req, _ := http.NewRequestWithContext(ctx, "GET", "https://example.com", nil)
resp, err := http.DefaultClient.Do(req)
if err != nil {
    // 超时或被取消
    log.Fatal(err)
}
defer resp.Body.Close()
~~~

~~~go
func handler(ctx context.Context) error {
    select {
    case <-ctx.Done():
        return ctx.Err() // context.DeadlineExceeded 或 context.Canceled
    case result := <-doWork(ctx):
        return result
    }
}
~~~

使用 Context 的几条最佳实践：

- `cancel` 必须 defer 调用，否则会造成 context 泄漏
- 不要把 Context 存在结构体里，显式传参更清晰
- 不要传递 nil context，不确定时用 `context.TODO()`
- ctx.Value 只用来传递请求级别的元数据（traceID 等），不要当参数传递的万能容器

## 并发安全与竞态检测

多个 goroutine 访问共享数据时必须保证同步。除了 mutex，`sync/atomic` 和 `sync.Map` 在特定场景下性能更好：

~~~go
var (
    mu    sync.Mutex
    count int
)

func inc() {
    mu.Lock()
    count++
    mu.Unlock()
}

// 只读多写少的场景可用 sync.Map
var sm sync.Map
sm.Store("key", "value")
v, ok := sm.Load("key")
~~~

养成用 `go test -race` 和 `go run -race` 的习惯，race detector 能在运行时捕获大多数数据竞争，成本只是 2~10 倍的运行时开销和 5~10 倍的内存开销。

## 总结

Go 的并发模型简洁但强大。理解 Channel 和 Context 的设计思想，掌握 worker pool、pipeline、errgroup 这些常见并发模式，配合 race detector 兜底，能让你写出高性能且安全的并发程序。核心心法只有一条：**通过通信共享内存，而不是通过共享内存实现通信**。
