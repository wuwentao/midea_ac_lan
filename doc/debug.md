# Debug log and Test steps

## Enable SSH

1. Install Add-on `[Advanced SSH & Web Terminal]` and disable `[Protected Mode]` once it done, you can ssh to your HAOS
2. Use any SSH Terminal software (or HA `[Advanced SSH & Web Terminal]` add-on web UI)

## Debug log

you can use below two methods to enable debug log.

edit `configuration.yaml` and reboot HA is therecommended method.

### method 1: edit `configuration.yaml`

1. SSH Login to your HA device
2. `cd /config/`
3. Add below lines to your `configuration.yaml`, for example `vi configuration.yaml`

   ```yaml
   logger:
     default: warn
     logs:
       custom_components.midea_ac_lan: debug
       midealocal: debug
   ```

   > we should enable `midea_ac_lan` and `midealocal`

4. Restart HA
5. Trigger debug log with some action with bug or error
6. Download full debug log file via HA web UI ( `Settings --> System --> Logs` )

### Method 2: use Action call without restart HA

1. Login to your HA Web UI
2. Goto `Developer Tools` -> `Actions` -> select `Logger: Set Log Level` -> `GO TO YAML MODE`
3. Paste below yaml content to the form，and run

   ```yaml
   action: logger.set_level
   data:
     custom_components.midea_ac_lan: debug
     midealocal: debug
   ```

   > Tips: this mode not required reboot, but it can't capture device startup error log, recommend to edit `configuration.yaml` file to enable debug mode.

4. Trigger debug log with some action with bug or error
5. Download full debug log file via HA web UI ( `Settings --> System --> Logs` )

## Test with manual edit source code

### edit `midea_ac_lan` source code

if you need to manual edit or change source code in `midea_ac_lan` for test purpose, follow below steps:

1. SSH login to your HAOS
2. switch to `midea_ac_lan` root directory with command: `cd /config/custom_components/midea_ac_lan`
3. now you can manual edit source code with `vi` , or `scp` to upload file, or `wget` to download github raw file.
4. once you upload or download a new file to HA, replace the old source code to new one.
5. reboot HA to load it.

   > for example: there is a github PR exist, and we should manual update `light.py`,
   > we can got github raw file URL, and use below `wget` command with `-O light.py` to download latest file and overwrite exist `light.py` > `wget https://github.com/wuwentao/midea_ac_lan/raw/xxxx/custom_components/midea_ac_lan/light.py -O light.py`

### edit `midealocal` source code

`midealocal` is a python3 pip package, and it will be installed in HA core (a docker container in HAOS).

1. ssh login to your HAOS
2. enter HA Core docker in HAOS: `docker exec -it homeassistant /bin/bash`
3. get `midealocal` install path with `pip show midea-local`, it will show path info to you, for example, my location is Location: `/usr/local/lib/python3.13/site-packages`
4. switch to `midealocal` root path with `cd /usr/local/lib/python3.13/site-packages/midealocal/`
5. now you can manual edit all the source code with `vi` , or `scp` to upload file, or `wget` to download file.
6. once you upload or download a new file to HA, replace the old source code file to new file.
7. reboot HA to load it

> `/config` path will be available in both HAOS and HA Core, you can transfer/share file with it.

for example: there is a github PR exist, and we should manual update `devices/cd/message.py`

> got github raw file URL, and use below `wget` command with `-O devices/cd/message.py` to download latest file and overwrite exist `devices/cd/message.py` > `wget https://github.com/midea-lan/midea-local/raw/xxxx/midealocal/devices/cd/message.py -O devices/cd/message.py`

## Get Device json config

When a device is added successfully, `midea_ac_lan` will save this device config to HA storage.
we will use this config file to prevent add this device for multiple times.
in addition, if you removed this device from Web UI, we still can use this config file for future device add with cloud login.

you can use below command to get a device json config:

1. SSH login to your HAOS
2. switch to json config root dir：`cd /config/.storage/midea_ac_lan`
3. use`ls` to check file list，and use `cat xxx.json`to show a device json config，`xxx` is device id.

> if there is no any error exist, please don't remove or edit this file.
> if you want to change it, you can rename and backup it.
