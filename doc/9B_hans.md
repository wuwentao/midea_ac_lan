# 微波蒸汽热风一体机

## 实体

### 默认实体

无默认实体

### 扩展实体

#### 开关

| EntityID                         | 类型   | 名称          | 描述   |
| -------------------------------- | ------ | ------------- | ------ |
| switch.{DEVICEID}\_power         | switch | Power         | 电源   |
| switch.{DEVICEID}\_lock          | switch | Child Lock    | 童锁   |
| switch.{DEVICEID}\_furnace_light | switch | Furnace Light | 炉灯   |
| switch.{DEVICEID}\_hot_wind      | switch | Hot Wind      | 热风   |
| switch.{DEVICEID}\_camera        | switch | Camera        | 摄像头 |

#### 选择器

| EntityID                              | 类型   | 名称        | 描述     | 选项                                                                     |
| ------------------------------------- | ------ | ----------- | -------- | ------------------------------------------------------------------------ |
| select.{DEVICEID}\_work_status_select | select | Work Status | 工作状态 | save_power, standby, work, pause                                         |
| select.{DEVICEID}\_fire_power_select  | select | Fire Power  | 火力     | high_power, medium_high_power, medium_power, medium_low_power, low_power |
| select.{DEVICEID}\_door_select        | select | Door        | 开关门   | open, close                                                              |

#### 数字

| EntityID                                        | 类型   | 名称                         | 描述         | 范围    |
| ----------------------------------------------- | ------ | ---------------------------- | ------------ | ------- |
| number.{DEVICEID}\_screen_luminance             | number | Screen Luminance             | 屏幕亮度     | 0 - 100 |
| number.{DEVICEID}\_volume                       | number | Volume                       | 音量         | 0 - 100 |
| number.{DEVICEID}\_temperature_number           | number | Target Temperature           | 目标温度     | 0 - 300 |
| number.{DEVICEID}\_temperature_above_number     | number | Target Temperature Above     | 目标上部温度 | 0 - 300 |
| number.{DEVICEID}\_temperature_underside_number | number | Target Temperature Underside | 目标下部温度 | 0 - 300 |
| number.{DEVICEID}\_probe_temperature_number     | number | Target Probe Temperature     | 目标探针温度 | 0 - 100 |
| number.{DEVICEID}\_steam_quantity_number        | number | Steam Quantity               | 蒸汽量       | 0 - 100 |
| number.{DEVICEID}\_hour_set                     | number | Hour Set                     | 小时设置     | 0 - 23  |
| number.{DEVICEID}\_minute_set                   | number | Minute Set                   | 分钟设置     | 0 - 59  |
| number.{DEVICEID}\_second_set                   | number | Second Set                   | 秒设置       | 0 - 59  |

#### 二元传感器

| EntityID                                        | 类型          | 名称                  | 描述     |
| ----------------------------------------------- | ------------- | --------------------- | -------- |
| binary_sensor.{DEVICEID}\_door_open             | binary_sensor | Door Open             | 门已打开 |
| binary_sensor.{DEVICEID}\_probe                 | binary_sensor | Probe                 | 探针     |
| binary_sensor.{DEVICEID}\_turntable             | binary_sensor | Turntable             | 转盘     |
| binary_sensor.{DEVICEID}\_lack_box              | binary_sensor | Lack Box              | 缺水盒   |
| binary_sensor.{DEVICEID}\_lack_water            | binary_sensor | Lack Water            | 缺水     |
| binary_sensor.{DEVICEID}\_change_water          | binary_sensor | Change Water Reminder | 换水提醒 |
| binary_sensor.{DEVICEID}\_error_code            | binary_sensor | Error Code            | 故障代码 |
| binary_sensor.{DEVICEID}\_flip_side             | binary_sensor | Flip Side             | 翻面     |
| binary_sensor.{DEVICEID}\_reaction              | binary_sensor | Reaction              | 交互提醒 |
| binary_sensor.{DEVICEID}\_high_temperature_lock | binary_sensor | High Temperature Lock | 高温锁   |
| binary_sensor.{DEVICEID}\_high_temperature_work | binary_sensor | High Temperature Work | 高温工作 |
| binary_sensor.{DEVICEID}\_high_temperature      | binary_sensor | High Temperature      | 高温     |
| binary_sensor.{DEVICEID}\_probe_mode            | binary_sensor | Probe Mode            | 探针模式 |
| binary_sensor.{DEVICEID}\_ramadan               | binary_sensor | Ramadan               | 斋月     |
| binary_sensor.{DEVICEID}\_clean_scale           | binary_sensor | Descaling             | 除垢     |
| binary_sensor.{DEVICEID}\_clean_sink_ponding    | binary_sensor | Clean Sink Ponding    | 水槽积水 |
| binary_sensor.{DEVICEID}\_ota                   | binary_sensor | OTA                   | 固件升级 |

#### 传感器

| EntityID                                     | 类型   | 名称                          | 描述         |
| -------------------------------------------- | ------ | ----------------------------- | ------------ |
| sensor.{DEVICEID}\_work_mode                 | sensor | Work Mode                     | 工作模式     |
| sensor.{DEVICEID}\_work_status               | sensor | Work Status                   | 工作状态     |
| sensor.{DEVICEID}\_fire_power                | sensor | Fire Power                    | 火力         |
| sensor.{DEVICEID}\_pre_heat                  | sensor | Pre Heat                      | 预热         |
| sensor.{DEVICEID}\_water_status              | sensor | Water Status                  | 水状态       |
| sensor.{DEVICEID}\_dissipate_heat            | sensor | Dissipate Heat                | 散热         |
| sensor.{DEVICEID}\_cur_temperature           | sensor | Current Temperature           | 当前温度     |
| sensor.{DEVICEID}\_cur_temperature_above     | sensor | Current Temperature Above     | 当前上部温度 |
| sensor.{DEVICEID}\_cur_temperature_underside | sensor | Current Temperature Underside | 当前下部温度 |
| sensor.{DEVICEID}\_cur_probe_temperature     | sensor | Current Probe Temperature     | 当前探针温度 |
| sensor.{DEVICEID}\_temperature               | sensor | Target Temperature            | 目标温度     |
| sensor.{DEVICEID}\_temperature_above         | sensor | Target Temperature Above      | 目标上部温度 |
| sensor.{DEVICEID}\_temperature_underside     | sensor | Target Temperature Underside  | 目标下部温度 |
| sensor.{DEVICEID}\_probe_temperature         | sensor | Target Probe Temperature      | 目标探针温度 |
| sensor.{DEVICEID}\_steam_quantity            | sensor | Steam Quantity                | 蒸汽量       |
| sensor.{DEVICEID}\_weight                    | sensor | Weight (g)                    | 重量（克）   |
| sensor.{DEVICEID}\_people_number             | sensor | People Number                 | 用餐人数     |
| sensor.{DEVICEID}\_work_hour                 | sensor | Work Hour                     | 工作小时     |
| sensor.{DEVICEID}\_work_minute               | sensor | Work Minute                   | 工作分钟     |
| sensor.{DEVICEID}\_work_second               | sensor | Work Second                   | 工作秒       |
| sensor.{DEVICEID}\_totalstep                 | sensor | Total Steps                   | 总步数       |
| sensor.{DEVICEID}\_stepnum                   | sensor | Current Step                  | 当前步数     |
| sensor.{DEVICEID}\_cloudmenuid               | sensor | Cloud Menu ID                 | 云菜单ID     |
| sensor.{DEVICEID}\_execute                   | sensor | Execute Status                | 执行状态     |
| sensor.{DEVICEID}\_cbs_version               | sensor | CBS Version                   | CBS版本      |
| sensor.{DEVICEID}\_sys_time_src              | sensor | System Time Source            | 系统时间源   |

## 服务

无服务
