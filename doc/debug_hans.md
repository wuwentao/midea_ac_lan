# 调试日志和测试方法

本文档说明如何在 Home Assistant OS（HAOS）上开启调试日志，以及如何临时修改 / 测试自定义集成 `midea_ac_lan` 及其依赖库 `midea-lan`（包名：`midealan`）。

> **重要提醒**
>
> 1. **调试结束后请务必关闭 debug 日志。**
>    长时间开启 `debug` 级别会产生大量日志，占用磁盘空间并影响性能。
>    如果通过修改 `configuration.yaml` 开启，**必须**删除或注释掉相关配置后**再次重启 Home Assistant** 才能真正生效。
> 2. **测试完成后请恢复所有源码 / manifest 修改。**
>    临时修改的 `manifest.json` 或 Python 源文件在收集完调试数据后应还原。

---

## 1. 开启 SSH 访问

1. 在 Home Assistant 中进入 **设置 → 加载项 → 加载项商店**。
2. 搜索并安装 **Advanced SSH & Web Terminal**。
3. 打开加载项配置：
   - 设置强密码（或配置 SSH 密钥）。
   - **关闭「保护模式」（Protected Mode）**（必须关闭才能使用 `docker` 命令并进入 HA Core 容器）。
4. 启动加载项，并可选择启用「在侧边栏中显示」。
5. 使用任意 SSH 客户端（或加载项自带的 Web 终端）连接到 HAOS 主机 IP（默认端口 22）。

> 关闭保护模式后，才能在 HAOS 中使用 `docker` 命令查看并操作 `homeassistant` 容器。

---

## 2. 开启调试日志（Debug Log）

有两种方法可用。**强烈推荐方法 1（修改 `configuration.yaml` 并重启）**，因为它能捕获启动阶段的错误。

### 方法 1：修改 `configuration.yaml`（推荐）

1. SSH 登录 HAOS。
2. `cd /config`
3. 编辑 `configuration.yaml`（可用 `vi` 或 File Editor 加载项），添加以下内容：

```yaml
logger:
  default: warn
  logs:
    custom_components.midea_ac_lan: debug
    midealan: debug
```

> 必须同时开启 `custom_components.midea_ac_lan` **和** `midealan`。

4. 完整重启 Home Assistant。
5. 执行会触发 bug / error 的操作。
6. 通过 **设置 → 系统 → 日志** 下载完整 debug 日志文件。

**测试结束后：** 删除（或注释）上述 `logger` 配置段，并再次重启 Home Assistant，确保 debug 日志已关闭。

### 方法 2：使用动作（Action）调用（无需重启）

1. 登录 Home Assistant Web UI。
2. 进入 **开发者工具 → 动作**。
3. 选择 **Logger: 设置级别**，切换到 YAML 模式。
4. 粘贴并执行以下内容：

```yaml
action: logger.set_level
data:
  custom_components.midea_ac_lan: debug
  midealan: debug
```

5. 执行会触发问题的操作。
6. 通过 **设置 → 系统 → 日志** 下载完整日志。

> 此方法**无法**捕获 Home Assistant 启动阶段的错误。建议调试时优先使用方法 1。

---

## 3. 临时修改源码进行测试

### 3.1 修改自定义集成（`midea_ac_lan`）

集成本身位于 `/config/custom_components/midea_ac_lan`，直接编辑即可。

1. SSH 登录 HAOS。
2. `cd /config/custom_components/midea_ac_lan`
3. 使用 `vi` 直接修改，或通过 `scp`/`SFTP` 上传，或用 `wget` 下载 GitHub raw 文件，例如：

```bash
wget https://github.com/wuwentao/midea_ac_lan/raw/<commit-or-branch>/custom_components/midea_ac_lan/light.py -O light.py
```

4. 完整重启 Home Assistant 以加载修改。

**测试结束后：** 恢复原始文件（或通过 HACS 重新安装集成）。

### 3.2 修改依赖库（`midea-lan` / `midealan`）

`midealan` 是安装在 Home Assistant Core Docker 容器内的 pip 包。以下提供多种方法，请按需选择。

#### 方法 A：修改 `manifest.json` 指向指定 Git 提交 / 分支（推荐大多数用户使用）

当改动已经存在于 GitHub（PR、分支或 commit）时，这是最干净的方式。

1. SSH 登录 HAOS。
2. 编辑 `/config/custom_components/midea_ac_lan/manifest.json`。
3. 临时修改 `requirements` 条目，例如：

```json
"requirements": [
  "midea-lan @ git+https://github.com/wuwentao/midea-lan.git@b59cfbc"
]
```

（将 `b59cfbc` 替换为所需的 commit hash、分支名或标签。）

4. 完整重启 Home Assistant。Home Assistant 会安装指定版本的库。

**测试结束后：** 恢复 `manifest.json` 中原来的 `requirements` 行并再次重启（或通过 HACS 重新安装集成）。

#### 方法 B：进入容器直接编辑已安装的包

适合快速本地实验，且暂时不想推送 Git 提交的情况。

1. SSH 登录 HAOS。
2. 进入 HA Core 容器：

```bash
docker exec -it homeassistant /bin/bash
```

3. 查看包安装路径：

```bash
pip show midea-lan
```

典型路径（Python 版本可能不同）：

```
Location: /usr/local/lib/python3.13/site-packages
```

4. 进入包目录：

```bash
cd /usr/local/lib/python3.13/site-packages/midealan/
```

5. 使用 `vi` 直接修改，或下载 raw 文件，例如：

```bash
wget https://github.com/wuwentao/midea-lan/raw/<commit>/midealan/devices/cd/message.py -O devices/cd/message.py
```

> 提示：`/config` 目录在容器内外均可访问，可将文件复制到 `/config` 方便传输。

6. 退出容器后**完整重启 Home Assistant**。

**测试结束后：** 下次 HA Core 升级或重新安装依赖时修改会被覆盖。也可手动恢复原文件或重新安装包。

#### 方法 C：其他便捷选项

- **将完整修改后的库复制到 `/config` 并调整导入路径**（进阶）：把本地 `midealan` 放到 `/config` 下，并修改自定义集成中的 import 路径。工作量较大，但可在容器重启后继续保留，直到手动清理。
- **使用开发环境**（VS Code + Remote SSH / Dev Container，或完整 HA Core 开发环境）：适合需要频繁修改并贡献代码的场景，长期最舒适。
- **结合方法 A 使用 HACS 重新下载**：推送临时分支后，通过 HACS 重新安装可强制拉取新库。

---

## 4. 获取设备 JSON 配置文件

设备成功添加后，`midea_ac_lan` 会将配置保存在 `/config/.storage/midea_ac_lan/` 下。

1. SSH 登录 HAOS。
2. `cd /config/.storage/midea_ac_lan`
3. 使用 `ls` 查看文件列表；使用 `cat <device_id>.json` 查看具体设备配置。

> 无特殊情况请勿删除或编辑这些文件。如需操作，请先重命名备份。

---

## 5. 获取设备类型和 SN

1. SSH 登录 HAOS。
2. 进入 HA Core 容器：

```bash
docker exec -it homeassistant /bin/bash
```

3. 执行以下命令（请将 IP 替换为你的设备地址）：

```bash
python3 -m midealan.cli discover --get_sn --host 192.168.2.127
```

示例输出：

```
2025-01-21 18:06:33.552 INFO (MainThread) [cli] Found 1 devices.
2025-01-21 18:06:33.552 INFO (MainThread) [cli] Found devices: {193514046726897: {'device_id': 193514046726897, 'type': 176, 'ip_address': '192.168.2.127', 'port': 6444, 'model': '0TG025JG', 'sn': 'xxxx', 'protocol': 3}}
```

反馈问题时请提供实际输出内容，其中包含设备类型、SN 和协议等关键调试信息。

---

## 测试结束后检查清单

- [ ] 关闭 debug 日志（从 `configuration.yaml` 中删除 logger 配置并重启，或将级别改回 `warn`/`info`）。
- [ ] 恢复对 `manifest.json` 的任何修改。
- [ ] 恢复手动编辑过的源文件（或重新安装集成 / 库）。
- [ ] 确认 Home Assistant 能干净启动，且集成已恢复使用官方包正常工作。
