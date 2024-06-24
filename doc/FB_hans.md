# 电取暖器

## Features

- 支持目标温度设定
- 支持预设模式设定

## 生成实体

### 默认生成实体

| 实体ID                      | 类型    | 描述       |
| --------------------------- | ------- | ---------- |
| climate.{DEVICEID}\_climate | climate | 恒温器实体 |

### 额外生成实体

| EntityID                               | 类型   | 名称                | 描述     |
| -------------------------------------- | ------ | ------------------- | -------- |
| sensor.{DEVICEID}\_current_temperature | sensor | Current Temperature | 当前温度 |
| lock.{DEVICEID}\_child_lock            | lock   | 童锁                |          |
| number.{DEVICEID}\_heating_level       | number | 加热档位            |          |
| switch.{DEVICEID}\_power               | switch | 电源开关            |          |

## 服务

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                     |
| --------- | ------------------------ |
| device_id | 设备的编号(Device ID)    |
| attribute | "child_lock"<br/>"power" |
| value     | true 或 false            |

| 名称      | 描述                  |
| --------- | --------------------- |
| device_id | 设备的编号(Device ID) |
| attribute | "heating_level"       |
| value     | 1 - 10                |

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
  attribute: heating_level
  value: 9
```
