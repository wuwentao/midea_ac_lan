# 贡献指南（中文版）

> [English Version](./CONTRIBUTING.md)

感谢你愿意为本项目贡献代码与想法！
本文档介绍如何使用 **[uv](https://docs.astral.sh/uv/)** 构建本地开发环境，以及如何提交代码与规范要求。

GitHub 文件路径：`.github/CONTRIBUTING.zh.md`

---

## 目录

1. [开发环境概述](#一-开发环境概述)
2. [前置条件：安装 uv](#二-前置条件安装-uv)
3. [初始化项目](#三-初始化项目)
4. [本地运行 Home Assistant](#四-本地运行-home-assistant)
5. [测试多个 Python 版本](#五-测试多个-python-版本)
6. [中国大陆网络镜像配置](#六-中国大陆网络镜像配置)
7. [代码风格、Pre-commit 与检查](#七-代码风格pre-commit-与检查)
8. [代码提交流程](#八-代码提交流程)
9. [问题反馈与社区守则](#九-问题反馈与社区守则)

---

## 一、开发环境概述

本项目使用 **[uv](https://docs.astral.sh/uv/)**（一个极快的 Python 包与项目管理器）来搭建简单、可复现的本地开发环境，**无需 Docker 或 Dev Container**。

`uv` 会自动：

- 创建并管理虚拟环境（`.venv`）；
- **自动下载所需的 Python 版本**（在 `.python-version` 中固定为 `3.12`）——你**无需**自己安装 Python；
- 根据 `pyproject.toml` / `uv.lock` 安装全部依赖。

支持的 Python 版本：**3.12、3.13、3.14**。

---

## 二、前置条件：安装 uv

只需安装一次 uv，按你的操作系统选择方式。完整文档：<https://docs.astral.sh/uv/getting-started/installation/>。

**macOS / Linux / WSL2：**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows（PowerShell）：**

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**其他方式（任意系统）：**

```bash
# 使用 Homebrew（macOS/Linux）
brew install uv
# 或使用 pipx
pipx install uv
```

安装后验证（必要时重启终端）：

```bash
uv --version
```

> 💡 **Windows 提示：** 你可以在 Windows 原生环境开发，也可以在 **WSL2**（Ubuntu）中开发，二者皆可——只需在你使用的环境中安装 uv 即可。

---

## 三、初始化项目

克隆仓库并运行初始化脚本：

```bash
git clone https://github.com/wuwentao/midea_ac_lan.git
cd midea_ac_lan
./scripts/setup.sh
```

`scripts/setup.sh` 会执行 `uv sync`（创建 `.venv` 并安装项目及 `dev` 依赖组）并安装 git 钩子。

想手动执行？以下两步等价：

```bash
uv sync
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

> 在没有 bash 的 Windows 环境下，请直接运行上面的手动命令，而不是 `scripts/setup.sh`。

---

## 四、本地运行 Home Assistant

启动本地 Home Assistant 实例（已加载本集成），地址 <http://localhost:8123>：

```bash
./scripts/run.sh
```

或直接运行：

```bash
uv run hass --config config --debug
```

首次运行会在 `./config` 下创建配置。在 VS Code 中也可使用 **“Run Home Assistant on port 8123”** 任务或 **“Python Debugger: Launch Home Assistant”** 调试配置。

---

## 五、测试多个 Python 版本

每个受支持的 Python 版本对应其必须兼容的最低 Home Assistant 版本。`uv` 会通过 `pyproject.toml` 中的环境标记自动选择对应的 Home Assistant：

| Python | Home Assistant |
| ------ | -------------- |
| 3.12   | 2024.4.1       |
| 3.13   | 2024.12.1      |
| 3.14   | 2026.3.1       |

随时切换到其他版本：

```bash
uv sync --python 3.13   # 或 3.14
```

若本地没有对应解释器，uv 会自动下载。

---

## 六、中国大陆网络镜像配置

如果依赖或 Python 下载缓慢，可在运行 uv **之前**设置以下环境变量（可写入 `~/.bashrc` / `~/.zshrc` / PowerShell 配置文件以持久化）：

```bash
# PyPI 镜像（清华）
export UV_DEFAULT_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple"

# Python 解释器下载镜像
export UV_PYTHON_INSTALL_MIRROR="https://mirror.nju.edu.cn/github-release/astral-sh/python-build-standalone"
```

Windows PowerShell：

```powershell
$env:UV_DEFAULT_INDEX = "https://pypi.tuna.tsinghua.edu.cn/simple"
$env:UV_PYTHON_INSTALL_MIRROR = "https://mirror.nju.edu.cn/github-release/astral-sh/python-build-standalone"
```

---

## 七、代码风格、Pre-commit 与检查

所有检查都通过 uv 环境中的 **pre-commit** 运行：

```bash
uv run pre-commit run --all-files
```

其中包括：

- `ruff` → 代码检查 + 自动修复与格式化（配置见 `pyproject.toml` 的 `[tool.ruff]`）
- `mypy` → 静态类型检查（配置见 `mypy.ini`）
- `pylint` → 额外的代码检查（配置见 `pylintrc`）
- `codespell`、`prettier`、`commitizen` / `commitlint`

提交前请修复所有报错。CI 会在每个 Pull Request 上运行相同的检查。

> 若你修改了 `pyproject.toml` 中的依赖，请运行 `uv lock`（或由 `uv-lock` 这个 pre-commit 钩子自动完成）并提交更新后的 `uv.lock`。

---

## 八、代码提交流程

1. 新建分支：
   ```bash
   git checkout -b feat/功能描述
   ```
2. 提交信息需遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：
   - `feat:` 新功能
   - `fix:` 修复问题
   - `chore:` 工具/配置调整（如 CI/CD、pre-commit 等）
   - `docs:` 文档修改
   - `refactor:` 重构代码
   - `test:` 测试相关修改

3. 示例：

   ```bash
   feat: 增加登录接口
   chore: 更新 pre-commit 配置
   fix: 修复配置路径错误
   ```

4. 推送并创建 Pull Request。
   GitHub Actions 会自动验证 commit message 格式并运行检查。

> ℹ️ pre-commit 钩子会阻止直接向 `main` 分支提交——请始终在分支上开发。

---

## 九、问题反馈与社区守则

- 提交 Issue 时请附带：重现步骤、环境说明、日志。
- 保持尊重、清晰、建设性的沟通。

---

**文件路径：**

- 中文版：`.github/CONTRIBUTING.zh.md`
- 英文版：`.github/CONTRIBUTING.md`
