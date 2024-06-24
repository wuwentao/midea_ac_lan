# 凉霸

## Features

- 支持风速调整
- 支持摇摆设定

## 实体

### 默认实体

| 实体ID              | 类型 | 描述     |
| ------------------- | ---- | -------- |
| fan.{DEVICEID}\_fan | fan  | Fan 实体 |

### 扩展实体

| 实体ID                                 | 类型   | 名称                | 描述       |
| -------------------------------------- | ------ | ------------------- | ---------- |
| sensor.{DEVICEID}\_current_temperature | select | Current Temperature | 当前温度   |
| switch.{DEVICEID}\_light               | switch | Light               | 灯         |
| select.{DEVICEID}\_ventilation         | switch | Ventilation         | 通风       |
| select.{DEVICEID}\_smelly_sensor       | switch | smelly Sensor       | 异味传感器 |
| select.{DEVICEID}\_direction           | select | Direction           | 摇摆方向   |

## 服务

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                                          |
| --------- | --------------------------------------------- |
| device_id | 设备的编号(Device ID)                         |
| attribute | "light"<br/>"ventilation"<br/>"smelly_sensor" |
| value     | true or false                                 |

| 名称      | 描述                                            |
| --------- | ----------------------------------------------- |
| device_id | 设备的编号(Device ID)                           |
| attribute | "directions"                                    |
| value     | 60<br/>70<br/>80<br/>90<br/>100<br/>"Oscillate" |

示例

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: light
  value: true
```

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: directions
  value: 100
```
