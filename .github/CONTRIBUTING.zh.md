# 贡献指南（中文版）

> [English Version](./CONTRIBUTING.md)

感谢你愿意为本项目贡献代码与想法！
本文档介绍如何使用 **VS Code + Dev Container** 构建开发环境、在 Windows（WSL2）下配置环境、如何提交代码以及规范要求。

GitHub 文件路径：`.github/CONTRIBUTING.zh.md`

---

## 目录

1. [开发环境概述](#一-开发环境概述)
2. [系统与工具要求](#二-系统与工具要求)
3. [推荐方式：在容器卷中克隆仓库](#三-推荐方式在容器卷中克隆仓库)
4. [备用方式：本地克隆后再在容器中打开（不推荐）](#四-备用方式本地克隆后再在容器中打开不推荐)
5. [Windows 用户指南（WSL2 必须）](#五-windows-用户指南wsl2-必须)
6. [中国大陆网络镜像配置](#六-中国大陆网络镜像配置)
7. [Dev Container 命令与问题排查](#七-dev-container-命令与问题排查)
8. [代码提交流程](#八-代码提交流程)
9. [代码风格与测试规范](#九-代码风格与测试规范)
10. [问题反馈与社区守则](#十-问题反馈与社区守则)

---

## 一、开发环境概述

本项目采用 **VS Code + Dev Container** 容器化开发环境，保证跨平台一致性。

> ✅ 推荐方式：在 VS Code 命令面板中执行 **“Dev Containers: Clone Repository in Container Volume...”**
> 所有依赖、权限与配置均在容器中完成。

---

## 二、系统与工具要求

- **操作系统**：Linux / macOS / Windows（需启用 WSL2）
- **Python**：最低版本 `3.11`（容器内已自动安装）
- **VS Code 插件**：
  - Dev Containers
  - Remote - WSL（仅 Windows 用户）
- **Docker**：Docker Desktop（启用 WSL2 backend）或原生 Docker
- **配置参考**：可查看 `.devcontainer/Dockerfile` 了解镜像构建逻辑

> ⚠️ Windows 用户 **无需** 在 WSL 中手动安装 Python、venv 或 pip，容器会自动配置完整环境。

---

## 三、推荐方式：在容器卷中克隆仓库

1. 打开 **VS Code**。
2. 打开命令面板：
   - **Windows/Linux**：`Ctrl + Shift + P`
   - **macOS**：`Cmd + Shift + P`
3. 输入 `Dev Containers: Clone Repository in Container Volume...`，按回车执行。
4. 输入仓库地址（如 `https://github.com/<org>/<repo>.git`）。
5. VS Code 将自动构建并打开容器化开发环境。

**优点：**

- 避免权限冲突；
- 环境与依赖完全由容器管理；
- 无需本地安装任何 Python 工具。

---

## 四、备用方式：本地克隆后再在容器中打开（不推荐）

```bash
git clone <仓库地址>
cd <仓库目录>
code .
```

然后执行命令：**Dev Containers: Open Folder in Container**

> ⚠️ 可能出现文件权限或 UID/GID 不一致问题，请自行调整或避免此方式。

---

## 五、Windows 用户指南（WSL2 必须）

1. 启用 WSL2：
   ```powershell
   wsl --install -d Ubuntu
   wsl --set-default-version 2
   ```
2. 无需在 Ubuntu 中安装 Python 或开发工具。
   只需确保 **Docker Desktop**（WSL2 backend）与 **VS Code Dev Containers** 插件已启用。
3. 推荐仓库存放路径：
   - `/home/<用户名>/<repo>`
   - 避免放在 `C:\` 驱动器下（性能差且易出权限问题）

---

## 六、中国大陆网络镜像配置

构建容器前可设置镜像变量：

```bash
export APT_MIRROR_DOMAIN="mirrors.tuna.tsinghua.edu.cn"
export PIP_MIRROR_DOMAIN="pypi.tuna.tsinghua.edu.cn"
```

这些变量在 `.devcontainer/Dockerfile` 中已支持。

---

## 七、Dev Container 命令与问题排查

| 命令                                     | 说明                 |
| ---------------------------------------- | -------------------- |
| **Reopen in Container**                  | 在容器中打开当前项目 |
| **Rebuild Container**                    | 重建开发容器         |
| **Clone Repository in Container Volume** | 推荐方式             |
| **Show Container Log**                   | 查看容器构建日志     |

> 构建错误可在命令面板执行：**Dev Containers: Show Container Log**

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
   GitHub Actions 会自动验证 commit message 格式。

---

## 九、代码风格与测试规范

- 容器内已预装 **pre-commit**，提交时会自动运行以下工具：
  - `ruff`：代码检查
  - `mypy`：类型检查
- 若 pre-commit 报错，请根据提示修复后重新提交。
- 测试推荐使用 `pytest`。

---

## 十、问题反馈与社区守则

- 提交 Issue 时请附带：重现步骤、环境说明、日志。
- 保持尊重、清晰、建设性的沟通。

---

**文件路径：**

- 中文版：`.github/CONTRIBUTING.zh.md`
- 英文版：`.github/CONTRIBUTING.md`
