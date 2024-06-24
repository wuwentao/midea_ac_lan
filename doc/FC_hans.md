# 空气净化器

## 自定义

设置自动打开或关闭待机模式的PM2.5检测数值

```json
{ "standby_detect": [50, 20] }
```

## 生成实体

### 默认生成实体

无默认实体

### 额外生成实体

| EntityID                          | 类型   | 名称               | 描述         |
| --------------------------------- | ------ | ------------------ | ------------ |
| sensor.{DEVICEID}\_pm25           | sensor | PM 2.5             | PM 2.5       |
| sensor.{DEVICEID}\_tvoc           | sensor | TVOC               | 可挥发有机物 |
| sensor.{DEVICEID}\_hcho           | sensor | Methanal           | 甲醛         |
| sensor.{DEVICEID}\_filter1_life   | sensor | Filter1 Life Level | 滤芯1寿命    |
| sensor.{DEVICEID}\_filter2_life   | sensor | Filter2 Life Level | 滤芯2寿命    |
| lock.{DEVICEID}\_child_lock       | lock   | Child Lock         | 童锁         |
| switch.{DEVICEID}\_anion          | switch | Anion              | 负离子       |
| switch.{DEVICEID}\_prompt_tone    | switch | Prompt Tone        | 提示音       |
| switch.{DEVICEID}\_power          | switch | Power              | 电源开关     |
| switch.{DEVICEID}\_standby        | switch | Standby            | 待机         |
| select.{DEVICEID}\_detect_mode    | select | Detect Mode        | 检测模式     |
| select.{DEVICEID}\_mode           | select | Mode               | 运行模式     |
| select.{DEVICEID}\_fan_speed      | select | Fan Speed          | 风速设定     |
| select.{DEVICEID}\_screen_display | select | Screen Display     | 屏显         |

## 服务

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                                                   |
| --------- | ------------------------------------------------------ |
| device_id | 设备的编号(Device ID)                                  |
| attribute | "child_lock"<br/>"anion"<br/>"prompt_tone"<br/>"power" |
| value     | true 或 false                                          |

| 名称      | 描述                              |
| --------- | --------------------------------- |
| device_id | 设备的编号(Device ID)             |
| attribute | "detect_mode"                     |
| value     | "Off"<br/>"PM 2.5"<br/>"Methanal" |

| 名称      | 描述                                                   |
| --------- | ------------------------------------------------------ |
| device_id | 设备的编号(Device ID)                                  |
| attribute | "mode"                                                 |
| value     | "Auto"<br/>"Manual"<br/>"Sleep"<br/>"Fast"<br/>"Smoke" |

| 名称      | 描述                                     |
| --------- | ---------------------------------------- |
| device_id | 设备的编号(Device ID)                    |
| attribute | "fan_speed"                              |
| value     | "Auto"<br/>"Low"<br/>"Medium"<br/>"High" |

| 名称      | 描述                         |
| --------- | ---------------------------- |
| device_id | 设备的编号(Device ID)        |
| attribute | "screen_display"             |
| value     | "Bright"<br/>"Dim"<br/>"Off" |

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
  value: Auto
```
