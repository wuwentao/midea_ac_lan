# 电壁挂炉

## 实体

### 默认实体

| EntityID                                      | Class   | Description                | 描述         |
| --------------------------------------------- | ------- | -------------------------- | ------------ |
| climate.{DEVICEID}\_climate                   | climate | Climate                    | 气候         |
| switch.{DEVICEID}\_power                      | switch  | Power                      | 电源         |
| number.{DEVICEID}\_heating_target_temperature | number  | Heating Target Temperature | 采暖目标温度 |
| select.{DEVICEID}\_heating_mode               | select  | Heating Mode               | 采暖模式     |

### 扩展实体

| EntityID                                            | Class         | Description                      | 描述             |
| --------------------------------------------------- | ------------- | -------------------------------- | ---------------- |
| sensor.{DEVICEID}\_status                           | sensor        | Status                           | 运行状态         |
| sensor.{DEVICEID}\_error_code                       | sensor        | Error Code                       | 故障码           |
| sensor.{DEVICEID}\_three_way_mode                   | sensor        | Three-way Mode                   | 三通模式         |
| sensor.{DEVICEID}\_heating_unit_type                | sensor        | Heating Unit Type                | 末端类型         |
| sensor.{DEVICEID}\_return_temperature               | sensor        | Return Temperature               | 回水温度         |
| sensor.{DEVICEID}\_current_temperature              | sensor        | Current Temperature              | 当前温度         |
| sensor.{DEVICEID}\_heating_temperature              | sensor        | Heating Temperature              | 采暖温度         |
| sensor.{DEVICEID}\_heating_gap_temperature          | sensor        | Heating Gap Temperature          | 采暖回差温度     |
| sensor.{DEVICEID}\_user_mode_target_temperature     | sensor        | User Mode Target Temperature     | 用户模式目标温度 |
| sensor.{DEVICEID}\_activity_mode_target_temperature | sensor        | Activity Mode Target Temperature | 活动模式目标温度 |
| sensor.{DEVICEID}\_sleep_mode_target_temperature    | sensor        | Sleep Mode Target Temperature    | 睡眠模式目标温度 |
| sensor.{DEVICEID}\_last_time                        | sensor        | Last Time                        | 持续时间         |
| sensor.{DEVICEID}\_flow_volume                      | sensor        | Flow Volume                      | 水流量           |
| binary_sensor.{DEVICEID}\_standby                   | binary_sensor | Standby                          | 待机             |
| binary_sensor.{DEVICEID}\_heating                   | binary_sensor | Heating                          | 采暖中           |
| binary_sensor.{DEVICEID}\_warm_power                | binary_sensor | Warm Power                       | 制热运行         |
| binary_sensor.{DEVICEID}\_cold_power                | binary_sensor | Cold Power                       | 制冷运行         |
| binary_sensor.{DEVICEID}\_sleep_power               | binary_sensor | Sleep Power                      | 睡眠运行         |
| binary_sensor.{DEVICEID}\_pump_on                   | binary_sensor | Pump On                          | 水泵运行         |
| binary_sensor.{DEVICEID}\_fault                     | binary_sensor | Fault                            | 故障             |

## Service

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                                        |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "power"                                     |
| value     | true 或 false                               |

| 名称      | 描述                                        |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "heating_target_temperature"                |
| value     | 25 到 60                                    |

| 名称      | 描述                                        |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "heating_mode"                              |
| value     | "user"<br/>"activity"<br/>"sleep"           |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: true
```

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: heating_target_temperature
  value: 45
```
