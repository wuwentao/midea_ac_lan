# 浴霸

## 特性

- 支持模式设定
- 支持风向调整

## 实体

### 默认实体

无默认实体

### 扩展实体

| 实体ID                                  | 类型          | 名称                | 描述       |
| --------------------------------------- | ------------- | ------------------- | ---------- |
| sensor.{DEVICEID}\_current_temperature  | sensor        | Current Temperature | 当前温度   |
| sensor.{DEVICEID}\_current_humidity     | sensor        | Current Humidity    | 当前湿度   |
| binary_sensor.{DEVICEID}\_current_radar | binary_sensor | Occupancy Status    | 人体传感器 |
| switch.{DEVICEID}\_main_light           | switch        | Main Light          | 主灯       |
| switch.{DEVICEID}\_night_light          | switch        | Night Light         | 夜灯       |
| select.{DEVICEID}\_mode                 | select        | Mode                | 模式       |
| select.{DEVICEID}\_direction            | select        | Fan direction       | 风向       |

## 服务

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                           |
| --------- | ------------------------------ |
| device_id | 设备的编号(Device ID)          |
| attribute | "main_light"<br/>"night_light" |
| value     | true 或 false                  |

| 名称      | 描述                                                                                     |
| --------- | ---------------------------------------------------------------------------------------- |
| device_id | 设备的编号(Device ID)                                                                    |
| attribute | "mode"                                                                                   |
| value     | "Off"<br/>"Heat(high)"<br/>"Heat(low)"<br/>"Bath"<br/>"Blow"<br/>"Ventilation"<br/>"Dry" |

| 名称      | 描述                                                    |
| --------- | ------------------------------------------------------- |
| device_id | 设备的编号(Device ID)                                   |
| attribute | "direction"                                             |
| value     | 60<br/>70<br/>80<br/>90<br/>100<br/>110<br/>"Oscillate" |

示例

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: main_light
  value: true
```

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: mode
  value: Bath
```

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: direction
  value: 70
```
