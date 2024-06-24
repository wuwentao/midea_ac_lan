# 中央空调Wi-Fi线控器

## 特性

- 支持目标温度设定
- 支持运行模式设定
- 支持风扇模式设定
- 支持摆风模式设定
- 支持电辅热

### 支持的模式

- 睡眠模式
- 节能模式

## 生成实体

### 默认生成实体

| 实体ID                      | 类型    | 描述       |
| --------------------------- | ------- | ---------- |
| climate.{DEVICEID}\_climate | climate | 恒温器实体 |

### 额外生成实体

| EntityID                              | 类型   | 名称               | 描述     |
| ------------------------------------- | ------ | ------------------ | -------- |
| sensor.{DEVICEID}\_indoor_temperature | sensor | Indoor Temperature | 室内温度 |
| switch.{DEVICEID}\_aux_heating        | switch | Aux Heating        | 电辅热   |
| switch.{DEVICEID}\_eco_mode           | switch | ECO Mode           | ECO模式  |
| switch.{DEVICEID}\_night_light        | switch | Night Light        | 夜灯     |
| switch.{DEVICEID}\_power              | switch | Power              | 电源开关 |
| switch.{DEVICEID}\_sleep_mode         | switch | Sleep Mode         | 睡眠模式 |
| switch.{DEVICEID}\_swing              | switch | Swing              | 摆风     |

## 服务

生成以下扩展服务

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                                                                                     |
| --------- | ---------------------------------------------------------------------------------------- |
| device_id | 设备的编号(Device ID)                                                                    |
| attribute | "aux_heating"<br/>"eco_mode"<br/>"night_light"<br/>"power"<br />"sleep_mode"<br/>"swing" |
| value     | true 或 false                                                                            |

示例

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: eco_mode
  value: true
```
