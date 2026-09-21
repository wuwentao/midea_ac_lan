# Debug Log and Test Steps

This document describes how to enable debug logging and how to temporarily modify / test the `midea_ac_lan` custom component and its dependency library `midea-lan` (package name: `midealan`) on Home Assistant OS (HAOS).

> **Important reminders**
>
> 1. **Always disable debug logging after you finish testing.**
>    Leaving `logger` at `debug` level for a long time generates large log files, consumes disk space and can impact performance.
>    If you enabled debug via `configuration.yaml`, you **must** remove or comment out the logger section and **restart Home Assistant** again for the change to take effect.
> 2. **Always restore source-code / manifest changes after testing.**
>    Temporary modifications to `manifest.json` or Python source files should be reverted once you have collected the needed debug data.

---

## 1. Enable SSH Access

1. In Home Assistant go to **Settings → Add-ons → Add-on Store**.
2. Search for and install **Advanced SSH & Web Terminal**.
3. Open the add-on configuration:
   - Set a strong password (or configure SSH keys).
   - **Disable “Protected Mode”** (required to run `docker` commands and access the HA Core container).
4. Start the add-on and (optionally) enable “Show in sidebar”.
5. Connect with any SSH client (or use the add-on’s web terminal) to your HAOS host IP on the configured port (default 22).

> Disabling Protected Mode allows the `docker` command to see and enter the `homeassistant` container.

---

## 2. Enable Debug Logging

Two methods are available. **Method 1 (edit `configuration.yaml` + restart) is strongly recommended** because it also captures startup errors.

### Method 1 – Edit `configuration.yaml` (recommended)

1. SSH into HAOS.
2. `cd /config`
3. Edit `configuration.yaml` (e.g. with `vi` or the File Editor add-on) and add:

```yaml
logger:
  default: warn
  logs:
    custom_components.midea_ac_lan: debug
    midealan: debug
```

> Both `custom_components.midea_ac_lan` **and** `midealan` must be set to `debug`.

4. Fully restart Home Assistant.
5. Perform the actions that trigger the bug / error.
6. Download the complete log via **Settings → System → Logs**.

**After testing:** remove (or comment out) the `logger` section above and restart Home Assistant again so that debug logging is turned off.

### Method 2 – Logger service call (no restart)

1. Open Home Assistant Web UI.
2. Go to **Developer Tools → Actions**.
3. Select **Logger: Set level** and switch to YAML mode.
4. Paste and run:

```yaml
action: logger.set_level
data:
  custom_components.midea_ac_lan: debug
  midealan: debug
```

5. Trigger the problematic action.
6. Download the log via **Settings → System → Logs**.

> This method does **not** capture errors that occur during Home Assistant startup. Prefer Method 1 for debugging.

---

## 3. Temporarily Modify Source Code for Testing

### 3.1 Modify the custom component (`midea_ac_lan`)

The integration itself lives under `/config/custom_components/midea_ac_lan` and is easy to edit.

1. SSH into HAOS.
2. `cd /config/custom_components/midea_ac_lan`
3. Edit files with `vi`, upload via `scp`/`SFTP`, or download a raw GitHub file, e.g.:

```bash
wget https://github.com/wuwentao/midea_ac_lan/raw/<commit-or-branch>/custom_components/midea_ac_lan/light.py -O light.py
```

4. Fully restart Home Assistant to load the changes.

**After testing:** restore the original files (or reinstall the integration via HACS).

### 3.2 Modify the library (`midea-lan` / `midealan`)

`midealan` is a pip package installed inside the Home Assistant Core Docker container. Several approaches exist; choose the one that best fits your needs.

#### Method A – Point `manifest.json` to a specific Git commit / branch (recommended for most users)

This is the cleanest way when the change already exists on GitHub (a PR, a branch or a commit).

1. SSH into HAOS.
2. Edit `/config/custom_components/midea_ac_lan/manifest.json`.
3. Temporarily change the `requirements` entry, for example:

```json
"requirements": [
  "midea-lan @ git+https://github.com/wuwentao/midea-lan.git@b59cfbc"
]
```

(Replace `b59cfbc` with the desired commit hash, branch name or tag.)

4. Fully restart Home Assistant. Home Assistant will install the specified version of the library.

**After testing:** restore the original `requirements` line in `manifest.json` and restart again (or reinstall the integration via HACS).

#### Method B – Edit the installed package inside the container

Useful for quick local experiments when you do not want to push a Git commit yet.

1. SSH into HAOS.
2. Enter the HA Core container:

```bash
docker exec -it homeassistant /bin/bash
```

3. Locate the package:

```bash
pip show midea-lan
```

Typical location (Python version may differ):

```
Location: /usr/local/lib/python3.13/site-packages
```

4. Change into the package directory:

```bash
cd /usr/local/lib/python3.13/site-packages/midealan/
```

5. Edit files with `vi`, or download a raw file, e.g.:

```bash
wget https://github.com/wuwentao/midea-lan/raw/<commit>/midealan/devices/cd/message.py -O devices/cd/message.py
```

> Tip: `/config` is mounted inside the container, so you can copy files to/from `/config` to transfer them easily.

6. Exit the container and **fully restart Home Assistant**.

**After testing:** the next HA Core upgrade or a reinstall of the requirement will overwrite your changes. You can also manually restore the original files or reinstall the package.

#### Method C – Other convenient options

- **Copy a whole modified tree into `/config` and adjust imports** (advanced): place a local copy of `midealan` under `/config` and change the import paths inside the custom component. This is more work but survives container restarts until you clean it up.
- **Use a development environment** (VS Code + Remote SSH / Dev Container, or a full HA Core development setup) when you plan to contribute many changes. This is the most comfortable long-term workflow.
- **HACS reinstall / “Re-download”** after you have pushed a temporary branch can also force a fresh library install when combined with Method A.

---

## 4. Obtain Device JSON Configuration

When a device is successfully added, `midea_ac_lan` stores its configuration under `/config/.storage/midea_ac_lan/`.

1. SSH into HAOS.
2. `cd /config/.storage/midea_ac_lan`
3. `ls` to list files; `cat <device_id>.json` to view a specific device.

> Do **not** delete or edit these files unless you know what you are doing. Rename/backup them first if you need to experiment.

---

## 5. Obtain Device Type and SN

1. SSH into HAOS.
2. Enter the HA Core container:

```bash
docker exec -it homeassistant /bin/bash
```

3. Run (replace the IP with your device’s address):

```bash
python3 -m midealan.cli discover --get_sn --host 192.168.2.127
```

Example output:

```
2025-01-21 18:06:33.552 INFO (MainThread) [cli] Found 1 devices.
2025-01-21 18:06:33.552 INFO (MainThread) [cli] Found devices: {193514046726897: {'device_id': 193514046726897, 'type': 176, 'ip_address': '192.168.2.127', 'port': 6444, 'model': '0TG025JG', 'sn': 'xxxx', 'protocol': 3}}
```

Please share this output when reporting issues – it contains the device type, SN and protocol needed for debugging.

---

## Quick Checklist After Testing

- [ ] Disable debug logging (remove logger section from `configuration.yaml` + restart, or set level back to `warn`/`info`).
- [ ] Restore any changes made to `manifest.json`.
- [ ] Restore any manually edited source files (or reinstall the integration / library).
- [ ] Confirm that Home Assistant starts cleanly and the integration works with the official package again.
