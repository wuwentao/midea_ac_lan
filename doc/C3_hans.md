# 热泵空调Wi-Fi线控器

## 特性

- 支持目标温度设定
- 支持运行模式设定

## 生成实体

### 默认生成实体

| 实体ID                                | 类型         | 描述            |
| ------------------------------------- | ------------ | --------------- |
| climate.{DEVICEID}\_climate_zone1     | climate      | 区域1恒温器实体 |
| climate.{DEVICEID}\_climate_zone2     | climate      | 区域2恒温器实体 |
| water_heater.{DEVICEID}\_water_heater | water_heater | 热水器实体      |

### 额外生成实体

| EntityID                                        | 类型          | 名称                         | 描述                                                                |
| ----------------------------------------------- | ------------- | ---------------------------- | ------------------------------------------------------------------- |
| binary_sensor.{DEVICEID}\_zone1_water_temp_mode | binary_sensor | Zone1 Water Temperature Mode | 区域1水温模式                                                       |
| binary_sensor.{DEVICEID}\_zone2_water_temp_mode | binary_sensor | Zone2 Water Temperature Mode | 区域2水温模式                                                       |
| binary_sensor.{DEVICEID}\_zone1_room_temp_mode  | binary_sensor | Zone1 Room Temperature Mode  | 区域1室温模式                                                       |
| binary_sensor.{DEVICEID}\_zone2_room_temp_mode  | binary_sensor | Zone2 Room Temperature Mode  | 区域2室温模式                                                       |
| binary_sensor.{DEVICEID}\_status_dhw            | binary_sensor | DHW Status                   | DHW状态                                                             |
| binary_sensor.{DEVICEID}\_status_tbh            | binary_sensor | TBH Status                   | TBH状态                                                             |
| binary_sensor.{DEVICEID}\_status_ibh            | binary_sensor | IBH Status                   | IBH状态                                                             |
| binary_sensor.{DEVICEID}\_status_heating        | binary_sensor | Heating Status               | 加热状态                                                            |
| sensor.{DEVICEID}\_error_code                   | sensor        | Error Code                   | 错误码                                                              |
| sensor.{DEVICEID}\_tank_actual_temperature      | sensor        | Tank Actual Temperature      | 水箱实际温度                                                        |
| sensor.{DEVICEID}\_total_energy_consumption     | sensor        | Total Energy Consumption     | 总能耗。</br>第一个值可能会延迟，因为更新仅在设备处于活动状态时发送 |
| sensor.{DEVICEID}\_total_produced_energy        | sensor        | Total Produced Energy        | 总计产生能量                                                        |
| sensor.{DEVICEID}\_outdoor_temperature          | sensor        | Outdoor Temperature          | 室外温度                                                            |
| switch.{DEVICEID}\_disinfect                    | switch        | Disinfect                    | 消毒                                                                |
| switch.{DEVICEID}\_dhw_power                    | switch        | DHW Power                    | 生活热水电源开关                                                    |
| switch.{DEVICEID}\_eco_mode                     | switch        | ECO Mode                     | ECO模式                                                             |
| switch.{DEVICEID}\_fast_dhw                     | switch        | Fast DHW                     | 快速生活热水                                                        |
| switch.{DEVICEID}\_silent_mode                  | switch        | Silent Mode                  | 静音模式                                                            |
| switch.{DEVICEID}\_tbh                          | switch        | TBH                          | TBH                                                                 |
| switch.{DEVICEID}\_zone1_curve                  | switch        | Zone1 Curve                  | 区域1曲线                                                           |
| switch.{DEVICEID}\_zone2_curve                  | switch        | Zone2 Curve                  | 区域2曲线                                                           |
| switch.{DEVICEID}\_zone1_power                  | switch        | Zone1 Power                  | 区域1恒温器开关                                                     |
| switch.{DEVICEID}\_zone2_power                  | switch        | Zone2 Power                  | 区域2恒温器开关                                                     |

## 服务

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                                                                                                               |
| --------- | ------------------------------------------------------------------------------------------------------------------ |
| device_id | 设备的编号(Device ID)                                                                                              |
| attribute | "disinfect"<br/>"dhw_power"<br/>"fast_dhw"<br/>"zone1_curve"<br/>"zone2_curve"<br/>"zone1_power"<br/>"zone2_power" |
| value     | true 或 false                                                                                                      |

示例

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: zone1_curve
  value: true
```
