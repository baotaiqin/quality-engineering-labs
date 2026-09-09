# Postman 集合自动化回归

本项目使用 Postman Collection 组织注册、登录、鉴权和退出请求，并通过 Newman 在命令行中重复执行。运行脚本会自动启动本地 HTTP 服务，不依赖外部接口和账号。

## 验证内容

- 注册成功、重复注册和字段缺失。
- 错误密码登录与正确密码登录。
- 登录后提取 Bearer Token，并用于访问受保护接口。
- 退出后再次使用原 Token，确认服务端已经撤销会话。
- 生成 JSON、JUnit 和脱敏汇总结果。
- 断言失败时返回非零退出码。

完整集合包含 9 个请求和 19 条断言。

## 目录

```text
.
├─ postman/
│  ├─ auth-regression.postman_collection.json
│  ├─ auth-regression.failure.postman_collection.json
│  └─ local.postman_environment.json
├─ scripts/run-collection.mjs
├─ server/app.mjs
├─ reports/
│  ├─ summary.json
│  └─ failure-summary.json
├─ package.json
└─ pnpm-lock.yaml
```

## 安装依赖

需要 Node.js 16 或更高版本。使用 npm：

```bash
npm install
```

也可以使用 pnpm 锁定依赖：

```bash
pnpm install --frozen-lockfile
```

Newman 固定为 6.2.2。

## 运行回归

```bash
npm run test:api
```

脚本会选择一个本机空闲端口，启动接口服务并运行集合。正常结果为 9 个请求、19 条断言全部通过，退出码为 0。

单独运行错误预期：

```bash
npm run test:api:failure
```

该命令把“缺少密码”的状态码错误地写成 401，实际接口返回 422，因此预期产生 1 条断言失败并返回退出码 1。

原始 JSON 和 JUnit 报告保存在 `reports/`，其中可能包含请求和响应数据，默认不会提交。仓库只保留去除 Token 等动态值后的汇总文件。

## 在 Postman 中运行

先启动本地接口：

```bash
npm start
```

然后导入 `postman/` 中的正常集合和环境文件，选择 `Local Auth API` 环境后运行整个集合。环境中的 `baseUrl` 默认为 `http://127.0.0.1:3100`。

## 适用范围

Newman 适合运行已有的 Collection v2.1 JSON 文件。Postman 当前推荐使用 Postman CLI；Postman v12 Native Git 使用的 v3 格式不能由 Newman 运行。这个项目保留 v2.1 JSON，是为了演示现有集合的本地自动执行和失败退出机制。

本地服务使用内存保存账号和 Token，不包含生产鉴权所需的密码哈希、持久化、Token 签名、过期刷新、限流和审计。

## 相关文章
