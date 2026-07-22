# Contributing Guide (English Version)

> [中文版点这里 / Chinese Version](./CONTRIBUTING.zh.md)

Thank you for contributing to this project!
This guide explains how to set up your development environment with **[uv](https://docs.astral.sh/uv/)** and how to contribute code following our workflow and style rules.

GitHub Path: `.github/CONTRIBUTING.md`

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisite: Install uv](#2-prerequisite-install-uv)
3. [Set Up the Project](#3-set-up-the-project)
4. [Run Home Assistant Locally](#4-run-home-assistant-locally)
5. [Testing Multiple Python Versions](#5-testing-multiple-python-versions)
6. [China Mainland Network Mirrors](#6-china-mainland-network-mirrors)
7. [Code Style, Pre-commit & Linting](#7-code-style-pre-commit--linting)
8. [Commit & Pull Request Workflow](#8-commit--pull-request-workflow)
9. [Issues & Community Conduct](#9-issues--community-conduct)

---

## 1. Overview

This project uses **[uv](https://docs.astral.sh/uv/)**, an extremely fast Python package and project manager, to provide a simple and reproducible local development environment. No Docker or Dev Container is required.

`uv` will:

- Create and manage a virtual environment (`.venv`) for you.
- **Automatically download the correct Python version** (pinned to `3.12` in `.python-version`) — you do **not** need to install Python yourself.
- Install all dependencies from `pyproject.toml` / `uv.lock`.

Supported Python versions: **3.12, 3.13, 3.14**.

---

## 2. Prerequisite: Install uv

Install uv once, using the method for your OS. Full docs: <https://docs.astral.sh/uv/getting-started/installation/>.

**macOS / Linux / WSL2:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternatives (any OS):**

```bash
# with Homebrew (macOS/Linux)
brew install uv
# or with pipx
pipx install uv
```

Verify the install and restart your shell if needed:

```bash
uv --version
```

> 💡 **Windows tip:** you can develop natively on Windows, or inside **WSL2** (Ubuntu). Either works — just install uv in whichever environment you use.

---

## 3. Set Up the Project

Clone the repository and run the setup script:

```bash
git clone https://github.com/wuwentao/midea_ac_lan.git
cd midea_ac_lan
./scripts/setup.sh
```

`scripts/setup.sh` runs `uv sync` (creating `.venv` and installing the project plus the `dev` dependency group) and installs the git hooks.

Prefer to do it manually? These two steps are equivalent:

```bash
uv sync
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

> On Windows without a bash shell, run the manual commands above instead of `scripts/setup.sh`.

---

## 4. Run Home Assistant Locally

Start a local Home Assistant instance with this integration loaded on <http://localhost:8123>:

```bash
./scripts/run.sh
```

Or run it directly:

```bash
uv run hass --config config --debug
```

The config is created under `./config` on first run. In VS Code you can also use the **"Run Home Assistant on port 8123"** task or the **"Python Debugger: Launch Home Assistant"** launch configuration.

---

## 5. Testing Multiple Python Versions

Each supported Python version targets the minimum Home Assistant version it must work with. `uv` selects the right Home Assistant automatically (via environment markers in `pyproject.toml`):

| Python | Home Assistant |
| ------ | -------------- |
| 3.12   | 2024.4.1       |
| 3.13   | 2024.12.1      |
| 3.14   | 2026.3.1       |

Switch the active environment to another version at any time:

```bash
uv sync --python 3.13   # or 3.14
```

uv downloads the interpreter if it is not already present.

---

## 6. China Mainland Network Mirrors

If package or Python downloads are slow, set these environment variables **before** running uv (put them in your `~/.bashrc` / `~/.zshrc` / PowerShell profile to persist):

```bash
# PyPI mirror (Tsinghua)
export UV_DEFAULT_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple"

# Python interpreter download mirror
export UV_PYTHON_INSTALL_MIRROR="https://mirror.nju.edu.cn/github-release/astral-sh/python-build-standalone"
```

On Windows PowerShell:

```powershell
$env:UV_DEFAULT_INDEX = "https://pypi.tuna.tsinghua.edu.cn/simple"
$env:UV_PYTHON_INSTALL_MIRROR = "https://mirror.nju.edu.cn/github-release/astral-sh/python-build-standalone"
```

---

## 7. Code Style, Pre-commit & Linting

All checks run through **pre-commit** inside the uv environment:

```bash
uv run pre-commit run --all-files
```

This runs, among others:

- `ruff` → linting + auto-fix and formatting (config in `pyproject.toml` `[tool.ruff]`)
- `mypy` → static type checking (config in `mypy.ini`)
- `pylint` → additional linting (config in `pylintrc`)
- `codespell`, `prettier`, `commitizen` / `commitlint`

Fix all reported issues before committing. The same checks run in CI on every pull request.

> If you change dependencies in `pyproject.toml`, run `uv lock` (or let the `uv-lock` pre-commit hook do it) and commit the updated `uv.lock`.

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
   GitHub Actions will validate your commit messages and run the linters automatically.

> ℹ️ Commits directly to `main` are blocked by a pre-commit hook — always work on a branch.

---

## 9. Issues & Community Conduct

When opening Issues:

- Include steps to reproduce, logs, and your environment info.
- Be respectful, concise, and follow community guidelines.

---

**File Path:**

- English: `.github/CONTRIBUTING.md`
- Chinese: `.github/CONTRIBUTING.zh.md`
