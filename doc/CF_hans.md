# 中央空调暖家

## 特性

- 支持目标温度设定
- 支持运行模式设定
- 支持电辅热

## 生成实体

### 默认生成实体

| 实体ID                      | 类型    | 描述       |
| --------------------------- | ------- | ---------- |
| climate.{DEVICEID}\_climate | climate | 恒温器实体 |

### 额外生成实体

| EntityID                               | 类型   | 名称                | 描述     |
| -------------------------------------- | ------ | ------------------- | -------- |
| sensor.{DEVICEID}\_current_temperature | sensor | Current Temperature | 当前温度 |
| switch.{DEVICEID}\_aux_heating         | switch | Aux Heating         | 电辅热   |
| switch.{DEVICEID}\_power               | switch | Power               | 电源开关 |

## Service

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                      |
| --------- | ------------------------- |
| device_id | 设备的编号(Device ID)     |
| attribute | "aux_heating"<br/>"power" |
| value     | true 或 false             |

示例

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: aux_heating
  value: true
```
