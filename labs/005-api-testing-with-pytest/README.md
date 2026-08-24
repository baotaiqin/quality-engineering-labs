# Pytest + Requests登录接口测试

本项目启动一个本地HTTP接口服务，使用Requests发送真实网络请求，并通过Pytest验证注册、登录、Bearer Token鉴权、退出和超时行为。

## 验证内容

- 登录成功后返回可用的Bearer Token。
- 密码错误和大小写变化均返回`401`。
- 请求体缺少密码时返回`422`及字段级错误信息。
- 重复注册返回`409`。
- 未携带Token访问资料接口返回`401`。
- 退出后原Token立即失效。
- 慢响应超过客户端读取超时时抛出`requests.Timeout`。

## 目录

```text
.
├─ src/
│  ├─ auth_api/
│  │  ├─ app.py
│  │  └─ store.py
│  └─ api_client.py
├─ tests/test_auth_api.py
├─ examples/test_wrong_status_expectation.py
├─ tools/capture_responses.py
├─ outputs/response_samples.json
├─ conftest.py
├─ pyproject.toml
└─ requirements.txt
```

## 环境准备

需要Python 3.10及以上版本。先创建独立虚拟环境，再安装依赖：

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

## 运行测试

Windows：

```bash
.venv\Scripts\python -m pytest -v
```

默认测试集共8条，本地运行结果为全部通过。

单独查看“缺少密码却错误预期为401”的失败场景：

```bash
.venv\Scripts\python -m pytest examples/test_wrong_status_expectation.py -q
```

该文件预期产生1条失败，实际状态码为`422`。

采集脱敏后的请求结果：

```bash
set PYTHONPATH=src
.venv\Scripts\python tools\capture_responses.py
```

## 适用范围

本地接口服务使用内存保存账号和Token，密码未做加密，只用于验证HTTP接口测试的组织方式。生产鉴权还需要密码哈希、Token签名与过期、持久化、限流、审计和密钥管理等机制。

## 相关文章

- [登录接口自动化测试：会话、断言、数据隔离与超时](https://blog.csdn.net/m0_53047391/article/details/164036710)
