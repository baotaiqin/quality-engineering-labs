# Playwright 登录流程测试

这份代码用 Playwright Test 检查一个本地账户页面的登录、错误密码、未登录访问和退出流程。服务端随测试自动启动，不需要外部账号。

## 运行

需要 Node.js 20 或更新版本。进入本目录后执行：

```bash
npm ci
npx playwright install chromium --no-shell
npm run typecheck
npm test
```

测试使用 Playwright 配套的 Chromium。正常运行包含 4 条用例，已在 Node.js 22.23.2、Playwright 1.63.0 和 Windows 10 下验证通过。HTML 报告生成在 `playwright-report/`。

单独运行故意写错断言的诊断用例：

```bash
npm run test:diagnostic
```

这条用例预期退出码为 1。登录实际成功，但它要求页面出现“账户已冻结”。失败截图和 `trace.zip` 会生成在 `test-results/`；可以根据终端打印的路径执行 `npx playwright show-trace <trace.zip路径>` 查看。

## 文件

```text
server/                         本地账户页面与接口
tests/specs/login.spec.ts       正常流程测试
tests/diagnostic/               失败定位用例，不参加 npm test
playwright.config.ts            浏览器、服务启动和 Trace 配置
playwright.diagnostic.config.ts 诊断用例的独立入口
```

本地账号 `reader / local-pass-2026` 仅用于这份代码。服务端将会话保存在内存里，未涉及数据库、真实用户或生产鉴权；测试范围也仅限 Chromium。

## 相关文章

[用Playwright跑通登录流程：定位、断言与Trace定位失败](https://blog.csdn.net/m0_53047391/article/details/165897044)
