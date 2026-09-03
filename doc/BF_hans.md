# 微蒸烤一体机

## 实体

### 默认实体

无默认实体

### 扩展实体

#### 开关

| EntityID                         | 类型   | 名称          | 描述     |
| -------------------------------- | ------ | ------------- | -------- |
| switch.{DEVICEID}\_power         | switch | Power         | 电源开关 |
| switch.{DEVICEID}\_child_lock    | switch | Child Lock    | 童锁     |
| switch.{DEVICEID}\_furnace_light | switch | Furnace Light | 炉灯     |
| switch.{DEVICEID}\_hot_wind      | switch | Hot Wind      | 热风     |
| switch.{DEVICEID}\_ramadan       | switch | Ramadan       | 斋月模式 |
| switch.{DEVICEID}\_turntable     | switch | Turntable     | 转盘     |

#### 选择器

| EntityID                              | 类型   | 名称               | 描述     | 选项                          |
| ------------------------------------- | ------ | ------------------ | -------- | ----------------------------- |
| select.{DEVICEID}\_work_mode_select   | select | Work Mode          | 工作模式 | midea-lan BF 工作模式名称     |
| select.{DEVICEID}\_fire_power_select  | select | Fire Power         | 火力     | fire_power_0 到 fire_power_10 |
| select.{DEVICEID}\_temperature_select | select | Target Temperature | 目标温度 | 0 到 250 的整数温度值         |

#### 二元传感器

| EntityID                                        | 类型          | 名称                  | 描述     |
| ----------------------------------------------- | ------------- | --------------------- | -------- |
| binary_sensor.{DEVICEID}\_pre_heat              | binary_sensor | Pre Heat              | 预热     |
| binary_sensor.{DEVICEID}\_tank_ejected          | binary_sensor | Tank Ejected          | 水箱弹出 |
| binary_sensor.{DEVICEID}\_water_change_reminder | binary_sensor | Water Change Reminder | 换水提醒 |
| binary_sensor.{DEVICEID}\_door                  | binary_sensor | Door                  | 门状态   |
| binary_sensor.{DEVICEID}\_water_shortage        | binary_sensor | Water shortage        | 缺水提醒 |
| binary_sensor.{DEVICEID}\_error                 | binary_sensor | Error                 | 错误状态 |
| binary_sensor.{DEVICEID}\_flip_side             | binary_sensor | Flip Side             | 翻面提醒 |
| binary_sensor.{DEVICEID}\_reaction              | binary_sensor | Reaction              | 反应     |
| binary_sensor.{DEVICEID}\_high_temperature_lock | binary_sensor | High Temperature Lock | 高温锁   |
| binary_sensor.{DEVICEID}\_high_temperature_work | binary_sensor | High Temperature Work | 高温工作 |
| binary_sensor.{DEVICEID}\_high_temperature      | binary_sensor | High Temperature      | 高温     |
| binary_sensor.{DEVICEID}\_probe_mode            | binary_sensor | Probe Mode            | 探针模式 |
| binary_sensor.{DEVICEID}\_probe                 | binary_sensor | Probe                 | 探针     |
| binary_sensor.{DEVICEID}\_clean_scale           | binary_sensor | Clean Scale           | 除垢     |
| binary_sensor.{DEVICEID}\_clean_sink_ponding    | binary_sensor | Clean Sink Ponding    | 水槽积水 |
| binary_sensor.{DEVICEID}\_dissipate_heat        | binary_sensor | Dissipate Heat        | 散热     |

#### 传感器

| EntityID                                     | 类型   | 名称                          | 描述         |
| -------------------------------------------- | ------ | ----------------------------- | ------------ |
| sensor.{DEVICEID}\_status                    | sensor | Status                        | 当前状态     |
| sensor.{DEVICEID}\_work_mode                 | sensor | Work Mode                     | 工作模式     |
| sensor.{DEVICEID}\_fire_power                | sensor | Fire Power                    | 火力         |
| sensor.{DEVICEID}\_current_temperature       | sensor | Current Temperature           | 当前温度     |
| sensor.{DEVICEID}\_temperature               | sensor | Target Temperature            | 目标温度     |
| sensor.{DEVICEID}\_temperature_above         | sensor | Temperature Above             | 上管温度     |
| sensor.{DEVICEID}\_temperature_underside     | sensor | Temperature Underside         | 下管温度     |
| sensor.{DEVICEID}\_cur_temperature_above     | sensor | Current Temperature Above     | 当前上管温度 |
| sensor.{DEVICEID}\_cur_temperature_underside | sensor | Current Temperature Underside | 当前下管温度 |
| sensor.{DEVICEID}\_probe_temperature         | sensor | Probe Temperature             | 探针目标温度 |
| sensor.{DEVICEID}\_cur_probe_temperature     | sensor | Current Probe Temperature     | 探针当前温度 |
| sensor.{DEVICEID}\_time_remaining            | sensor | Time Remaining                | 剩余时间     |
| sensor.{DEVICEID}\_steam_quantity            | sensor | Steam Quantity                | 蒸汽量       |
| sensor.{DEVICEID}\_weight                    | sensor | Weight (g)                    | 重量（克）   |
| sensor.{DEVICEID}\_people_number             | sensor | People Number                 | 人数         |
| sensor.{DEVICEID}\_totalstep                 | sensor | Total Steps                   | 总步骤数     |
| sensor.{DEVICEID}\_stepnum                   | sensor | Current Step                  | 当前步骤     |
| sensor.{DEVICEID}\_cloudmenuid               | sensor | Cloud Menu ID                 | 云菜单 ID    |
| sensor.{DEVICEID}\_execute                   | sensor | Execute Status                | 执行状态     |

## 服务

无服务
