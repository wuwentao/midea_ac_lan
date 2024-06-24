# 家用空调

## 特性

- 支持运行模式
- 支持风扇模式设定
- 支持摆风
- 支持湿度设定

## 生成实体

### 默认生成实体

| 实体ID                            | 类型       | 描述       |
| --------------------------------- | ---------- | ---------- |
| humidifier.{DEVICEID}\_humidifier | humidifier | 加湿器实体 |

### 额外生成实体

| EntityID                               | 类型          | 名称                | 描述             |
| -------------------------------------- | ------------- | ------------------- | ---------------- |
| sensor.{DEVICEID}\_tank_full           | binary_sensor | Tank Full           | 水箱已达设置水位 |
| sensor.{DEVICEID}\_tank                | sensor        | Tank                | 水箱水位         |
| sensor.{DEVICEID}\_current_humidity    | sensor        | Current Humidity    | 当前湿度         |
| sensor.{DEVICEID}\_current_temperature | sensor        | Current Temperature | 当前温度         |
| lock.{DEVICEID}\_child_lock            | lock          | Child Lock          | 童锁             |
| switch.{DEVICEID}\_anion               | switch        | Anion               | 负离子开关       |
| switch.{DEVICEID}\_prompt_tone         | switch        | Prompt Tone         | 提示音           |
| switch.{DEVICEID}\_power               | switch        | Power               | 电源开关         |
| switch.{DEVICEID}\_swing               | switch        | Swing               | 摆风开关         |
| select.{DEVICEID}\_fan_speed           | select        | Fan Speed           | 风速设定         |
| select.{DEVICEID}\_water_level_set     | select        | Water Level Setting | 水位设定         |

## 服务

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                                                               |
| --------- | ------------------------------------------------------------------ |
| device_id | 设备的编号(Device ID)                                              |
| attribute | "child_lock"<br/>"anion"<br/>"prompt_tone"<br/>"power"<br/>"swing" |
| value     | true 或 false                                                      |

| 名称      | 描述                                                            |
| --------- | --------------------------------------------------------------- |
| device_id | 设备的编号(Device ID)                                           |
| attribute | "fan_speed"                                                     |
| value     | "Lowest"<br/>"Low"<br/>"Medium"<br/>"High"<br/>"Auto"<br/>"Off" |

| 名称      | 描述                             |
| --------- | -------------------------------- |
| device_id | 设备的编号(Device ID)            |
| attribute | "water_level_set"                |
| value     | "25"<br/>"50"<br/>"75"<br/>"100" |

示例

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: prompt_tone
  value: true
```

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: fan_speed
  value: Medium
```
