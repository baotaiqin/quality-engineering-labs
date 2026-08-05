# 登录功能测试设计

## 项目说明

这个项目以一个普通Web站点的账号密码登录为例，整理可追踪的测试需求、决策表和27条核心测试用例，并使用Python检查用例质量。

示例需求包含输入边界、统一失败提示、连续失败锁定、会话更新、重复提交和弱网恢复。具体数值只服务于本次设计演示，不代表所有系统都应该使用相同规则。

## 内容

- `data/login_test_cases.csv`：27条核心登录测试用例。
- `data/login_decision_table.csv`：账号、密码、状态和锁定条件的决策表。
- `src/validate_cases.py`：检查字段完整性、编号唯一性、关键场景和预期结果。
- `src/generate_charts.py`：生成测试范围、边界值、状态迁移和用例分布图。
- `tests/test_validate_cases.py`：校验脚本和绘图代码的自动化测试。
- `outputs/`：用例摘要、需求覆盖统计和生成图表。

## 环境

- Python 3.10及以上
- Pillow 10.0至12.x

```bash
python -m pip install -r requirements.txt
```

## 运行校验

```bash
python src/validate_cases.py --input data/login_test_cases.csv --output-dir outputs
```

校验通过时输出：

```text
PASS: 27条用例校验通过
```

## 生成图表

```bash
python src/generate_charts.py --cases data/login_test_cases.csv --output-dir outputs/charts
```

## 运行测试

```bash
python -m unittest discover -s tests -v
```

当前测试覆盖重复编号、关键边界遗漏、模糊预期结果、账号枚举提示、摘要输出和图表生成。

## 局限

- 这是测试设计示例，没有连接真实登录服务，不能替代系统级执行结果。
- 27条用例只覆盖当前明确的账号密码登录范围，不代表完整认证系统的全部用例。
- 锁定阈值、响应时间等数值是示例需求，真实项目需要根据业务风险和容量目标确定。
- 短信验证码、第三方登录、MFA和跨地域容灾不在本次范围内。

## 相关文章
