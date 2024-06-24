# 电风扇

## 特性

- 支持风速调节
- 支持预设模式
- 支持水平摆头
- 支持垂直摆头

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

| EntityID                             | 类型   | 名称              | 描述         |
| ------------------------------------ | ------ | ----------------- | ------------ |
| select.{DEVICEID}\_oscillation_mode  | select | Oscillation Mode  | 摆头模式     |
| select.{DEVICEID}\_oscillation_angle | select | Oscillation Angle | 水平摆头角度 |
| select.{DEVICEID}\_tilting_angle     | select | Tilting Angle     | 垂直摆头角度 |
| lock.{DEVICEID}\_child_lock          | lock   | Child Lock        | 童锁         |
| switch.{DEVICEID}\_oscillate         | switch | Oscillate         | 摆头开关     |
| switch.{DEVICEID}\_power             | switch | Power             | 电源开关     |

## 服务

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                         |
| --------- | ---------------------------- |
| device_id | 设备的编号(Device ID)        |
| attribute | "child_lock"<br/>"oscillate" |
| value     | true 或 false                |

| 名称      | 描述                                                                                        |
| --------- | ------------------------------------------------------------------------------------------- |
| device_id | 设备的编号(Device ID)                                                                       |
| attribute | "oscillation_mode"                                                                          |
| value     | "Off"<br/>"Oscillation"<br/>"Tilting"<br/>"Curve-W"<br/>"Curve-8"<br/>"Reserved"<br/>"Both" |

| 名称      | 描述                                                           |
| --------- | -------------------------------------------------------------- |
| device_id | 设备的编号(Device ID)                                          |
| attribute | "oscillation_angle"                                            |
| value     | "Off"<br/>"30"<br/>"60"<br/>"90"<br/>"120"<br/>"180"<br/>"360" |

| 名称      | 描述                                                                                        |
| --------- | ------------------------------------------------------------------------------------------- |
| device_id | 设备的编号(Device ID)                                                                       |
| attribute | "tilting_angle"                                                                             |
| value     | "Off"<br/>"30"<br/>"60"<br/>"90"<br/>"120"<br/>"180"<br/>"360"<br/>"+60"<br/>"-60"<br/>"40" |

示例

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: true
```

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: oscillation_angle
  value: "90"
```
