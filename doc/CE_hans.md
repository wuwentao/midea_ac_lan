# 新风机

**_注意:部分美的的"中央新风机"产品，其实使用了空调的协议。如果你的新风机被识别为空调，参阅[内置新风系统](AC_hans.md#%E5%86%85%E7%BD%AE%E6%96%B0%E9%A3%8E%E7%B3%BB%E7%BB%9F)_**

## 特性

- 支持风速调节
- 支持预设模式

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

| EntityID                                           | 类型          | 名称                     | 描述         |
| -------------------------------------------------- | ------------- | ------------------------ | ------------ |
| binary_sensor.{DEVICEID}\_filter_cleaning_reminder | binary_sensor | Filter Cleaning Reminder | 滤芯清洁提醒 |
| binary_sensor.{DEVICEID}\_filter_change_reminder   | binary_sensor | Filter Change Reminder   | 滤芯更换提醒 |
| sensor.{DEVICEID}\_current_humidity                | sensor        | Current Humidity         | 当前湿度     |
| sensor.{DEVICEID}\_current_temperature             | sensor        | Current Temperature      | 当前温度     |
| sensor.{DEVICEID}\_co2                             | sensor        | Carbon Dioxide           | 二氧化碳     |
| sensor.{DEVICEID}\_hcho                            | sensor        | Methanal                 | 甲醛         |
| sensor.{DEVICEID}\_pm25                            | sensor        | PM 2.5                   | PM 2.5       |
| lock.{DEVICEID}\_child_lock                        | lock          | Child Lock               | 童锁         |
| switch.{DEVICEID}\_aux_heating                     | switch        | Aux Heating              | 电辅热开关   |
| switch.{DEVICEID}\_eco_mode                        | switch        | ECO Mode                 | 节能模式开关 |
| switch.{DEVICEID}\_link_to_ac                      | switch        | Link to AC               | 空调联动开关 |
| switch.{DEVICEID}\_power                           | switch        | Power                    | 电源开关     |
| switch.{DEVICEID}\_powerful_purify                 | switch        | Powerful Purification    | 强净开关     |
| switch.{DEVICEID}\_sleep_mode                      | switch        | Sleep Mode               | 睡眠模式开关 |

## 服务

生成以下扩展服务

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                                                                                                              |
| --------- | ----------------------------------------------------------------------------------------------------------------- |
| device_id | 设备的编号(Device ID)                                                                                             |
| attribute | "child_lock"<br/>"aux_heating"<br/>"eco_mode"<br/>"link_to_ac"<br/>"power"<br/>"powerful_purify"<br/>"sleep_mode" |
| value     | true 或 false                                                                                                     |

示例

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: true
```
