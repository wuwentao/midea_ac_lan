# 热泵空调Wi-Fi线控器

## 特性

- 支持目标温度设定
- 支持运行模式设定

## 自定义

- 设置温度调整步长(默认为0.5).

```json
{ "temperature_step": 1 }
```

## 生成实体

### 默认生成实体

| 实体ID                                | 类型         | 描述            |
| ------------------------------------- | ------------ | --------------- |
| climate.{DEVICEID}\_climate_zone1     | climate      | 区域1恒温器实体 |
| climate.{DEVICEID}\_climate_zone2     | climate      | 区域2恒温器实体 |
| water_heater.{DEVICEID}\_water_heater | water_heater | 热水器实体      |

### 额外生成实体

| EntityID                                        | 类型          | 名称                                          | 描述                                                                |
| ----------------------------------------------- | ------------- | --------------------------------------------- | ------------------------------------------------------------------- |
| binary_sensor.{DEVICEID}\_zone1_water_temp_mode | binary_sensor | Zone1 Water Temperature Mode                  | 区域1水温模式                                                       |
| binary_sensor.{DEVICEID}\_zone2_water_temp_mode | binary_sensor | Zone2 Water Temperature Mode                  | 区域2水温模式                                                       |
| binary_sensor.{DEVICEID}\_zone1_room_temp_mode  | binary_sensor | Zone1 Room Temperature Mode                   | 区域1室温模式                                                       |
| binary_sensor.{DEVICEID}\_zone2_room_temp_mode  | binary_sensor | Zone2 Room Temperature Mode                   | 区域2室温模式                                                       |
| binary_sensor.{DEVICEID}\_status_dhw            | binary_sensor | DHW Status                                    | DHW状态                                                             |
| binary_sensor.{DEVICEID}\_status_tbh            | binary_sensor | TBH Status                                    | TBH状态                                                             |
| binary_sensor.{DEVICEID}\_status_ibh            | binary_sensor | IBH Status                                    | IBH状态                                                             |
| binary_sensor.{DEVICEID}\_status_heating        | binary_sensor | Heating Status                                | 加热状态                                                            |
| sensor.{DEVICEID}\_error_code                   | sensor        | Error Code                                    | 错误码                                                              |
| sensor.{DEVICEID}\_tank_actual_temperature      | sensor        | Tank Actual Temperature                       | 水箱实际温度                                                        |
| sensor.{DEVICEID}\_total_energy_consumption     | sensor        | Total Energy Consumption                      | 总能耗。</br>第一个值可能会延迟，因为更新仅在设备处于活动状态时发送 |
| sensor.{DEVICEID}\_total_produced_energy        | sensor        | Total Produced Energy                         | 总计产生能量                                                        |
| sensor.{DEVICEID}\_outdoor_temperature          | sensor        | Outdoor Temperature                           | 室外温度                                                            |
| sensor.{DEVICEID}\_temp_tw_in                   | sensor        | Water Inlet Temperature                       | 进水温度                                                            |
| sensor.{DEVICEID}\_temp_tw_out                  | sensor        | Water Outlet Temperature                      | 出水温度                                                            |
| sensor.{DEVICEID}\_instant_power0               | sensor        | Current Power                                 | 当前功率                                                            |
| sensor.{DEVICEID}\_comp_run_freq                | sensor        | Compressor Frequency                          | 压缩机运行频率                                                      |
| sensor.{DEVICEID}\_fan_speed                    | sensor        | Outdoor Fan Speed                             | 室外风机转速                                                        |
| sensor.{DEVICEID}\_unit_mode_run                | sensor        | Unit Run Mode                                 | 机组运行模式                                                        |
| sensor.{DEVICEID}\_odu_target_fre               | sensor        | Target Compressor Frequency                   | 目标压缩机频率                                                      |
| sensor.{DEVICEID}\_odu_voltage                  | sensor        | Outdoor Unit Voltage                          | 室外机电压                                                          |
| sensor.{DEVICEID}\_odu_comp_current             | sensor        | Compressor Current                            | 压缩机电流                                                          |
| sensor.{DEVICEID}\_exv_current                  | sensor        | Electronic Expansion Valve Opening            | 电子膨胀阀开度                                                      |
| sensor.{DEVICEID}\_fg_capacity_need             | sensor        | Capacity Demand                               | 能力需求                                                            |
| sensor.{DEVICEID}\_pressure_high                | sensor        | Refrigerant Pressure (High Side)              | 排气压力                                                            |
| sensor.{DEVICEID}\_pressure_low                 | sensor        | Refrigerant Pressure (Low Side)               | 吸气压力                                                            |
| sensor.{DEVICEID}\_temp_t1                      | sensor        | Temperature Sensor T1                         | 温度传感器 T1                                                       |
| sensor.{DEVICEID}\_temp_t2                      | sensor        | Plate Heat Exchanger Temperature (T2)         | 板换温度 (T2)                                                       |
| sensor.{DEVICEID}\_temp_t2b                     | sensor        | Plate Heat Exchanger Outlet Temperature (T2B) | 板换出口温度 (T2B)                                                  |
| sensor.{DEVICEID}\_temp_t3                      | sensor        | Outdoor Coil Temperature (T3)                 | 室外盘管温度 (T3)                                                   |
| sensor.{DEVICEID}\_temp_tp                      | sensor        | Discharge Pipe Temperature (TP)               | 排气管温度 (TP)                                                     |
| sensor.{DEVICEID}\_temp_th                      | sensor        | Suction Temperature (TH)                      | 吸气温度 (TH)                                                       |
| sensor.{DEVICEID}\_temp_tf                      | sensor        | Power Module Temperature (TF)                 | 功率模块温度 (TF)                                                   |
| switch.{DEVICEID}\_disinfect                    | switch        | Disinfect                                     | 消毒                                                                |
| switch.{DEVICEID}\_dhw_power                    | switch        | DHW Power                                     | 生活热水电源开关                                                    |
| switch.{DEVICEID}\_eco_mode                     | switch        | ECO Mode                                      | ECO模式                                                             |
| switch.{DEVICEID}\_fast_dhw                     | switch        | Fast DHW                                      | 快速生活热水                                                        |
| switch.{DEVICEID}\_silent_mode                  | switch        | Silent Mode                                   | 静音模式                                                            |
| switch.{DEVICEID}\_silent_level                 | select        | Silent Level                                  | 静音级别                                                            |
| switch.{DEVICEID}\_tbh                          | switch        | TBH                                           | TBH                                                                 |
| switch.{DEVICEID}\_zone1_curve                  | switch        | Zone1 Curve                                   | 区域1曲线                                                           |
| switch.{DEVICEID}\_zone2_curve                  | switch        | Zone2 Curve                                   | 区域2曲线                                                           |
| switch.{DEVICEID}\_zone1_power                  | switch        | Zone1 Power                                   | 区域1恒温器开关                                                     |
| switch.{DEVICEID}\_zone2_power                  | switch        | Zone2 Power                                   | 区域2恒温器开关                                                     |

## 服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                                                                                                               |
| --------- | ------------------------------------------------------------------------------------------------------------------ |
| device_id | 设备的编号(Device ID)                                                                                              |
| attribute | "disinfect"<br/>"dhw_power"<br/>"fast_dhw"<br/>"zone1_curve"<br/>"zone2_curve"<br/>"zone1_power"<br/>"zone2_power" |
| value     | true 或 false                                                                                                      |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: zone1_curve
  value: true
```
