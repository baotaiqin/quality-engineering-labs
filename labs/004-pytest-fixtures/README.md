# Pytest fixture登录状态管理

本项目使用账号存储和登录会话说明Pytest fixture的依赖关系、作用域与资源清理。测试通过函数参数显式声明所需状态，公共fixture集中放在`conftest.py`中。

## 主要内容

- `password_policy`使用`session`作用域，整次测试只创建一次。
- `account_store`使用默认的`function`作用域，每条测试获得独立状态。
- `registered_user`负责创建和删除测试账号。
- `authenticated_client`依赖账号数据，负责登录和退出。
- `examples/test_scope_mismatch.py`保留一处作用域不兼容场景，默认测试不会收集该文件。

## 目录

```text
.
├─ src/account_service.py
├─ tests/test_account_access.py
├─ examples/test_scope_mismatch.py
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

查看一条测试的fixture准备与清理顺序：

```bash
.venv\Scripts\python -m pytest tests/test_account_access.py::test_logged_in_user_can_view_profile --setup-show -q
```

查看作用域不兼容错误：

```bash
.venv\Scripts\python -m pytest examples/test_scope_mismatch.py -q
```

默认测试集共5条，本地运行结果为全部通过。作用域错误场景预期产生1条`ScopeMismatch`。

## 适用范围

当前代码使用内存存储和本地会话对象，重点验证fixture的组织方式。真实接口、数据库或浏览器资源仍需要处理连接失败、并发数据隔离和进程异常退出等情况。

## 相关文章

- [用登录状态讲清Pytest fixture：依赖、scope与yield](https://blog.csdn.net/m0_53047391/article/details/163735797)
