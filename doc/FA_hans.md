# 电风扇

## 特性

- 支持风速调节
- 支持预设模式
- 支持水平摆头
- 支持垂直摆头
- 支持加湿、水离子、负离子和驱蚊
- 支持显示屏、自动关机和体感扫描
- 上报湿度、目标温度和故障代码

## 自定义

设置风扇的挡位, 不包括"Off"在内(默认为3)。

```json
{ "speed_count": 5 }
```

## 生成实体

### 默认生成实体

| 实体ID              | 类型 | 描述     |
| ------------------- | ---- | -------- |
| fan.{DEVICEID}\_fan | fan  | 风扇实体 |

### 额外生成实体

| EntityID                                | 类型   | 名称                 | 描述         |
| --------------------------------------- | ------ | -------------------- | ------------ |
| select.{DEVICEID}\_oscillation_mode     | select | Oscillation Mode     | 摆头模式     |
| select.{DEVICEID}\_oscillation_angle    | select | Oscillation Angle    | 水平摆头角度 |
| select.{DEVICEID}\_tilting_angle        | select | Tilting Angle        | 垂直摆头角度 |
| lock.{DEVICEID}\_child_lock             | lock   | Child Lock           | 童锁         |
| switch.{DEVICEID}\_oscillate            | switch | Oscillate            | 摆头开关     |
| switch.{DEVICEID}\_power                | switch | Power                | 电源开关     |
| switch.{DEVICEID}\_humidify             | switch | Humidify             | 加湿         |
| switch.{DEVICEID}\_waterions            | switch | Water Ions           | 水离子       |
| switch.{DEVICEID}\_anion                | switch | Anion                | 负离子       |
| switch.{DEVICEID}\_anophelifuge         | switch | Anti-Mosquito        | 驱蚊         |
| switch.{DEVICEID}\_display_on_off       | switch | Display              | 显示屏       |
| switch.{DEVICEID}\_auto_power_off       | switch | Auto Power Off       | 自动关机     |
| switch.{DEVICEID}\_body_feeling_scan    | switch | Body Feeling Scan    | 体感扫描     |
| sensor.{DEVICEID}\_humidity             | sensor | Humidity             | 湿度         |
| sensor.{DEVICEID}\_target_temperature   | sensor | Target Temperature   | 目标温度     |
| sensor.{DEVICEID}\_humidify_feedback    | sensor | Humidity Feedback    | 湿度反馈     |
| sensor.{DEVICEID}\_temperature_feedback | sensor | Temperature Feedback | 温度反馈     |
| sensor.{DEVICEID}\_humidify_mode        | sensor | Humidify Mode        | 加湿模式     |
| sensor.{DEVICEID}\_error_code           | sensor | Error Code           | 故障代码     |

## 服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                                                                                                                                                         |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| device_id | 设备的编号(Device ID)                                                                                                                                        |
| attribute | "child_lock"<br/>"oscillate"<br/>"humidify"<br/>"waterions"<br/>"anion"<br/>"anophelifuge"<br/>"display_on_off"<br/>"auto_power_off"<br/>"body_feeling_scan" |
| value     | true 或 false                                                                                                                                                |

| 名称      | 描述                                                                                                     |
| --------- | -------------------------------------------------------------------------------------------------------- |
| device_id | 设备的编号(Device ID)                                                                                    |
| attribute | "oscillation_mode"                                                                                       |
| value     | "off"<br/>"oscillation"<br/>"tilting"<br/>"curve_w"<br/>"curve_8"<br/>"reserved"<br/>"both"<br/>"custom" |

| 名称      | 描述                                                           |
| --------- | -------------------------------------------------------------- |
| device_id | 设备的编号(Device ID)                                          |
| attribute | "oscillation_angle"                                            |
| value     | "off"<br/>"30"<br/>"60"<br/>"90"<br/>"120"<br/>"180"<br/>"360" |

| 名称      | 描述                                                                                        |
| --------- | ------------------------------------------------------------------------------------------- |
| device_id | 设备的编号(Device ID)                                                                       |
| attribute | "tilting_angle"                                                                             |
| value     | "off"<br/>"30"<br/>"60"<br/>"90"<br/>"120"<br/>"180"<br/>"360"<br/>"+60"<br/>"-60"<br/>"40" |

| 名称      | 描述                  |
| --------- | --------------------- |
| device_id | 设备的编号(Device ID) |
| attribute | "target_temperature"  |
| value     | 目标温度(°C)          |

| 名称      | 描述                  |
| --------- | --------------------- |
| device_id | 设备的编号(Device ID) |
| attribute | "humidity"            |
| value     | 目标湿度(% 1-100)     |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: true
```

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: oscillation_angle
  value: "90"
```
