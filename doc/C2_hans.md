# 智能座便器

## 自定义

- 设置最大烘干档位 (默认为3)
- 设置最大座温档位 (默认5)
- 设置最大水温档位 (默认为 5)

```json
{ "max_dry_level": 3, "max_water_temp_level": 5, "max_seat_temp_level": 5 }
```

## 实体

### 默认实体

无默认实体

### 扩展实体

| EntityID                              | Class         | Description               | 描述     |
| ------------------------------------- | ------------- | ------------------------- | -------- |
| binary_sensor.{DEVICEID}\_seat_status | binary_sensor | Seat Status               | 入座状态 |
| binary_sensor.{DEVICEID}\_lid_status  | binary_sensor | Lid Status                | 盖子状态 |
| sensor.{DEVICEID}\_water_temperature  | sensor        | Current Water Temperature | 当前水温 |
| sensor.{DEVICEID}\_seat_temperature   | sensor        | Current Heat Temperature  | 当前座温 |
| sensor.{DEVICEID}\_filter_life        | sensor        | Filter Life               | 滤芯寿命 |
| switch.{DEVICEID}\_child_lock         | lock          | Child Lock                | 童锁     |
| switch.{DEVICEID}\_power              | switch        | Power                     | 电源     |
| switch.{DEVICEID}\_sensor_light       | switch        | Sensor Light              | 感应夜灯 |
| switch.{DEVICEID}\_foam_shield        | switch        | Foam Shield               | 泡沫盾   |
| number.{DEVICEID}\_dry_level          | number        | Dry Level                 | 烘干档位 |
| number.{DEVICEID}\_water_temp_level   | number        | Water Temperature Level   | 水温档位 |
| number.{DEVICEID}\_seat_temp_level    | number        | Seat Temperature Level    | 座温档位 |

## Service

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                                        |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "child_lock"<br/>"power"<br/>"light"        |
| value     | true 或 false                               |

| 名称      | 描述                                                    |
| --------- | ------------------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance             |
| attribute | "dry_level"<br/>"water_temp_level"<br>"seat_temp_level" |
| value     | 0 到 最大档位                                           |

示例

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: child_lock
  value: true
```

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: max_dry_level
  value: 2
```
