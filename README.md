# 质量工程实践

这个仓库整理软件测试、测试开发和 AI 测试相关的配套代码。每个目录围绕一个具体技术问题，保留可运行实现、自动化测试、必要数据和结果说明。

## 内容索引

| 编号 | 内容 | 主要技术 | 状态 |
|---|---|---|---|
| 001 | [27届测试岗位要求分析](labs/001-job-requirements-analysis/) | Python、Pillow、unittest | 已完成 |
| 002 | [登录功能测试设计](labs/002-login-test-design/) | Python、CSV、Pillow、unittest | 已完成 |
| 003 | [Pytest运费规则测试](labs/003-pytest-basics/) | Python、pytest、pytest-html | 已完成 |

## 目录结构

```text
quality-engineering-labs/
├─ labs/                 # 按主题组织的代码与测试
└─ README.md
```

每个目录都有单独的说明文档，可以独立安装依赖、运行代码和执行测试。

## 说明

- 博客配套代码统一放在 `labs/` 下，完整项目会单独建仓库。
- 数据和结论只针对各目录说明的范围，不做过度外推。
- 不提交账号凭据、个人隐私、未脱敏日志和写作草稿。

## 文章链接

- [拆解18个27届测试岗位：测试开发需要哪些能力？](https://blog.csdn.net/m0_53047391/article/details/163417663)
- [从一个登录功能开始：需求、状态和风险如何落到测试用例](https://blog.csdn.net/m0_53047391/article/details/163514975)
- [Pytest入门实战：从第一条断言到参数化与HTML报告](https://blog.csdn.net/m0_53047391/article/details/163617989)
