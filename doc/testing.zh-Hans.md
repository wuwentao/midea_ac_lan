# 集成测试

集成测试遵循 Home Assistant 的测试方法：使用真实的 `hass` fixture 和
`MockConfigEntry`，通过 `hass.config_entries.async_setup` 加载配置项，通过
`hass.services.async_call` 调用服务，并检查 `hass.states` 和实体、设备注册表。
只模拟设备连接、局域网发现和 Cloud 请求。测试不得访问真实设备或账号；pytest
会阻止网络 socket。

## 本地命令

将测试环境与包含 lint 和开发工具的 `.venv` 分开：

```sh
UV_PROJECT_ENVIRONMENT=.venv-test312 uv sync --locked --no-default-groups --group test --python 3.12
UV_PROJECT_ENVIRONMENT=.venv-test312 uv run --no-sync pytest
UV_PROJECT_ENVIRONMENT=.venv-test312 uv run --no-sync pytest --cov=custom_components.midea_ac_lan --cov-report=term-missing --cov-report=html --cov-report=xml
```

打开 `htmlcov/index.html` 查看未覆盖的行和分支。覆盖率统计包含整个集成及兼容性
分支，不得通过排除生产代码提高百分比。`.coveragerc` 会在每个受支持的矩阵环境中
强制执行 100% 行覆盖率和分支覆盖率门禁。

## 兼容性矩阵

| Python | Home Assistant        | 测试组         | 测试插件                                          |
| ------ | --------------------- | -------------- | ------------------------------------------------- |
| 3.12   | 2024.4.1              | `test`         | `pytest-homeassistant-custom-component==0.13.112` |
| 3.13   | 2024.12.1             | `test`         | `pytest-homeassistant-custom-component==0.13.191` |
| 3.14   | 2026.3.1              | `test`         | `pytest-homeassistant-custom-component==0.13.317` |
| 3.14   | 2026.11.0b4（预览版） | `test-current` | `pytest-homeassistant==2026.11.0b4`               |

验证其他基线时，修改上方命令中的环境目录和 `--python`。预览版还需选择
`--group test-current`。目前官方统一维护的插件从 Python 3.14 和 HA 2026.11
预发布版开始提供；历史 HA 版本需要匹配的提取版插件。不得同时安装两种插件。
`tests/ha.py` 提供统一的辅助类导入。HA 和测试插件必须配套更新，并运行完整矩阵。

这些组与 `dev`、`run` 互斥，因为历史插件也固定了 pytest、pydantic、numpy 和
lint 工具版本。最旧插件声明的 `mypy-dev` 预发布版已无法获取，因此将其排除；
类型检查使用开发环境中的 `scripts/mypy.sh`。

## 新增测试

导入和 patch 目标使用 `custom_components.midea_ac_lan`，与 HA 加载器保持一致。
使用第二个包名导入同一集成会创建独立模块状态，可能掩盖注册和生命周期问题。
为独立转换和边界条件保留小型单元测试，但平台服务、配置及选项流程、更新、加载
失败、卸载和迁移应通过 HA 的公开管理器验证。设备标识和凭据必须使用虚构数据。

Tests workflow 运行所有矩阵组合、发布 Markdown 覆盖率摘要，并上传 XML、HTML、
Markdown 和 JUnit 报告。最低版本环境的报告还会上传到 Codecov，用于 PR 报告和
README 徽章。只有所有矩阵环境都达到 100% 且标准报告上传完成后，`Coverage gate`
检查才会成功。由于上游 OIDC 凭据不会提供给 fork，来自 fork 的 PR 会以尽力而为
方式上传 Codecov；本地 100% 门禁仍然生效。Lint 检查继续由独立的 Lint workflow
执行。
