# Pytest运费规则测试

本项目围绕订单运费计算规则，提供一套可直接运行的Pytest测试代码，包含普通断言、参数化用例、异常断言和HTML测试报告。

## 目录

- `src/shipping.py`：运费计算逻辑。
- `tests/test_shipping.py`：默认执行的7条测试。
- `examples/test_shipping_failure.py`：故意写错预期值的失败场景，不属于默认测试集。
- `outputs/report.html`：一次真实运行生成的自包含HTML报告。
- `pyproject.toml`：Pytest配置。

## 环境准备

需要Python 3.10及以上版本。先在当前目录创建独立虚拟环境，再安装依赖：

```bash
python -m venv .venv
```

Windows：

```bash
.venv\Scripts\python -m pip install -r requirements.txt
```

macOS或Linux：

```bash
.venv/bin/python -m pip install -r requirements.txt
```

`.venv`只用于本地运行，不提交到仓库。

## 运行测试

Windows：

```bash
.venv\Scripts\python -m pytest -v
```

生成单文件HTML报告：

```bash
.venv\Scripts\python -m pytest --html=outputs/report.html --self-contained-html
```

查看故意失败的场景：

```bash
.venv\Scripts\python -m pytest examples/test_shipping_failure.py -q
```

默认测试集共7条，本地验证结果为全部通过。失败场景预期返回1条失败，用于观察断言差异。

## 说明

- 金额使用`Decimal`，避免用二进制浮点数直接表示费用。
- 参数化用例使用可读的`id`，方便从终端和报告中定位场景。
- 当前代码只验证运费计算函数，不包含数据库、接口或页面测试。

## 相关文章

- [Pytest入门实战：从第一条断言到参数化与HTML报告](https://blog.csdn.net/m0_53047391/article/details/163617989)
