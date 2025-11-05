# Contributing Guide (English Version)

> [中文版点这里 / Chinese Version](./CONTRIBUTING.zh.md)

Thank you for contributing to this project!
This guide explains how to set up your development environment (recommended: **VS Code + Dev Container**) and how to contribute code following our workflow and style rules.

GitHub Path: `.github/CONTRIBUTING.md`

---

## Table of Contents

1. [Overview](#1-overview)
2. [System Requirements](#2-system-requirements)
3. [Recommended Setup: Clone in Container Volume](#3-recommended-setup-clone-in-container-volume)
4. [Alternative Setup: Local Clone (Not Recommended)](#4-alternative-setup-local-clone-not-recommended)
5. [Windows Users (WSL2 Required)](#5-windows-users-wsl2-required)
6. [China Mainland Network Mirrors](#6-china-mainland-network-mirrors)
7. [Dev Container Commands & Debugging](#7-dev-container-commands--debugging)
8. [Commit & Pull Request Workflow](#8-commit--pull-request-workflow)
9. [Code Style, Pre-commit & Testing](#9-code-style-pre-commit--testing)
10. [Issues & Community Conduct](#10-issues--community-conduct)

---

## 1. Overview

This project uses **VS Code + Dev Container** to provide a consistent, containerized development environment.

> ✅ Recommended: Use **“Dev Containers: Clone Repository in Container Volume...”** directly from VS Code to avoid permission issues.

---

## 2. System Requirements

- **OS:** Linux / macOS / Windows (with WSL2)
- **Python:** ≥ 3.11 (for runtime inside container)
- **VS Code Extensions:**
  - [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
  - [Remote - WSL](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl) (Windows only)
- **Docker:** Docker Desktop (with WSL2 backend) or native Docker
- **Reference:** See `.devcontainer/Dockerfile` for the environment build details.

> ⚠️ On Windows, you **do not need** to install Python or any build tools inside WSL manually. The container environment handles everything.

---

## 3. Recommended Setup: Clone in Container Volume

1. Open **VS Code**.
2. Press:
   - **Windows/Linux:** `Ctrl + Shift + P`
   - **macOS:** `Cmd + Shift + P`
3. Type `Dev Containers: Clone Repository in Container Volume...` and press Enter.
4. Enter your repository URL (e.g., `https://github.com/<org>/<repo>.git`).
5. VS Code will automatically:
   - Clone the repository into a Docker-managed volume.
   - Build and open the containerized environment.

**Advantages:**

- Avoids UID/GID conflicts.
- All dependencies and configs remain inside the container.

---

## 4. Alternative Setup: Local Clone (Not Recommended)

If you prefer cloning locally:

```bash
git clone <repo-url>
cd <repo>
code .
```

Then open via command:

> `Dev Containers: Open Folder in Container`

⚠️ May cause permission issues if your host user differs from the container user.
Use at your own risk.

---

## 5. Windows Users (WSL2 Required)

1. Enable WSL2:
   ```powershell
   wsl --install -d Ubuntu
   wsl --set-default-version 2
   ```
2. No need to install Python or compilers manually.
   Just ensure Docker Desktop (WSL2 backend) and VS Code Dev Container extensions are installed.
3. Clone or open repositories **inside WSL’s Linux filesystem**:
   - Example path: `/home/<user>/<repo>`
   - Avoid using `C:\` drives to prevent performance and permission issues.

---

## 6. China Mainland Network Mirrors

For users in China Mainland, set mirrors before building:

```bash
export APT_MIRROR_DOMAIN="mirrors.tuna.tsinghua.edu.cn"
export PIP_MIRROR_DOMAIN="pypi.tuna.tsinghua.edu.cn"
```

These variables are supported inside `devcontainer/Dockerfile`.

---

## 7. Dev Container Commands & Debugging

| Command                                  | Description                          |
| ---------------------------------------- | ------------------------------------ |
| **Reopen in Container**                  | Open current folder inside container |
| **Rebuild Container**                    | Rebuild environment                  |
| **Clone Repository in Container Volume** | Recommended workflow                 |
| **Show Container Log**                   | View build logs and errors           |

---

## 8. Commit & Pull Request Workflow

1. Create a branch:
   ```bash
   git checkout -b feat/add-feature
   ```
2. Follow [Conventional Commits](https://www.conventionalcommits.org/) message format:
   - `feat:` → New feature
   - `fix:` → Bug fix
   - `chore:` → Tooling, configs, or non-functional updates
   - `docs:` → Documentation only
   - `refactor:` → Code restructure
   - `test:` → Test-only changes

3. Example:

   ```bash
   feat: add user authentication
   chore: update pre-commit hooks
   fix: correct API endpoint error
   ```

4. Push and open a Pull Request.
   GitHub Actions will validate your commit messages automatically.

---

## 9. Code Style, Pre-commit & Testing

- **Pre-commit** is preinstalled inside the container.
- It automatically runs:
  - `ruff` → Linting and static analysis
  - `mypy` → Type checking
- Fix all reported issues before committing.
- Tests use `pytest` (unless specified otherwise).

---

## 10. Issues & Community Conduct

When opening Issues:

- Include steps to reproduce, logs, and your environment info.
- Be respectful, concise, and follow community guidelines.

---

**File Path:**

- English: `.github/CONTRIBUTING.md`
- Chinese: `.github/CONTRIBUTING.zh.md`
