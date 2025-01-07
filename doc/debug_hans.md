# 调试日志和测试方法

## 开启SSH

1. 安装 Add-on `[Advanced SSH & Web Terminal]` ，并禁用保护模式 `[Protected Mode]`
2. 使用任意SSH终端软件(或者HA Web UI中使用 `[Advanced SSH & Web Terminal]` add-on)

## 调试日志Debug Log

以下二种方法都可以打开调试日志Debug Log, 推荐使用修改`configuration.yaml`并重启HA的方法.

### 方法1: 修改`configuration.yaml`

1. SSH登录HAOS设备IP地址
2. `cd /config/`
3. 将以下内容加入 `configuration.yaml`中, 例如`vi configuration.yaml`

   ```yaml
   logger:
     default: warn
     logs:
       custom_components.midea_ac_lan: debug
       midealocal: debug
   ```

   > 需要同时开启 `midea_ac_lan` 和 `midealocal`

4. 重启HA
5. 执行有bug或error的操作，触发debug log
6. 通过HA web UI ( `设置 --> 系统 --> 日志` )， 下载完整debug log文件

### 方法2： 使用 Action 动作

1. 登录HA Web UI
2. 进入 `开发者工具` -> `动作` -> 选择 `Logger: 设置级别` -> `进入YAML模式`
3. 粘贴以下YAML内容到输入框中，并执行动作

   ```yaml
   action: logger.set_level
   data:
     custom_components.midea_ac_lan: debug
     midealocal: debug
   ```

   > 说明：此方法不需要重启HA，但是不能捕获开启启动以后的很多错误日志, 强烈推荐使用编辑`configuration.yaml`的方法。

4. 支持有bug或者error产生的动作，触发debug log
5. 进入`设置 --> 系统 --> 日志`， 点击下载按钮，下载完整debug log

## 修改源代码进行测试

### 修改 `midea_ac_lan`源代码

如果需要修改`midea_ac_lan`进行测试, 请按以下流程操作:

1. SSH登录HAOS
2. 切换到`midea_ac_lan`根目录：`cd /config/custom_components/midea_ac_lan`
3. 使用`vi`直接修改, 或者使用`scp`上传文件, 或者使用`wget`下载github raw文件.
4. 用上传或下载的文件替换同名的旧文件即可.
5. 重启HA重新加载修改后的源码.

   > 例如: 有一个github的PR, 需要修改`light.py`,
   > 首先获取github PR中对应文件的raw file URL, 然后使用 `wget` 命令带上 `-O light.py` 去下载文件并覆盖已经存在的`light.py`即可
   > `wget https://github.com/wuwentao/midea_ac_lan/raw/xxxx/custom_components/midea_ac_lan/light.py -O light.py`

### 修改`midealocal`源代码

`midealocal`是python3的pip package, 安装是HA core 中，(属于HAOS里面运行的一个docker container).

1. SSH登录HAOS
2. 在HAOS中执行如下命令进入HA Core所在的docker: `docker exec -it homeassistant /bin/bash`
3. 使用`pip show midea-local`来获取`midealocal`, 例如, 我的Path为: `/usr/local/lib/python3.13/site-packages`
4. 使用`cd /usr/local/lib/python3.13/site-packages/midealocal/`切换到 `midealocal`根目录
5. 使用`vi`直接修改, 或者使用`scp`上传文件, 或者使用`wget`下载github raw文件.
6. 用上传或下载的文件替换同名的旧文件即可.
7. 重启HA重新加载修改后的源码.

> `/config` 目录在HAOS和HA core中均存在, 可以将文件保持至此目录.

例如: 有一个github的PR, 需要修改`devices/cd/message.py`,

> 首先获取github PR中对应文件的raw file URL, 然后使用 `wget` 命令带上 `-O devices/cd/message.py` 去下载文件并覆盖已经存在的`devices/cd/message.py`即可
> `wget https://github.com/midea-lan/midea-local/raw/xxxx/midealocal/devices/cd/message.py -O devices/cd/message.py`

## 获取设备json配置文件

每个设备添加成功以后，`midea_ac_lan`会将设备基本信息保存至HA中，下次重复添加时无需连接服务器，同时用于去重，避免重复添加同一台设备。

可以使用以下命令获取某台设备的配置文件:

1. SSH登录HAOS设备IP地址
2. 切换至配置文件根目录：`cd /config/.storage/midea_ac_lan`
3. 可以使用`ls`命令查看所有文件，可以使用`cat xxx.json`查看某个设备的配置信息，xxx为设备虚拟ID.

> 如无特殊或者异常情况，一般不建议操作该文件。如需操作，可重命名备份该文件配置文件
