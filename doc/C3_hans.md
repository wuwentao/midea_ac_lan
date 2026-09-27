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
| binary_sensor.{DEVICEID}\_status_cool           | binary_sensor | Status - Cooling                              | 状态 - 制冷                                                         |
| binary_sensor.{DEVICEID}\_eco_function_state    | binary_sensor | Mode - ECO Function                           | 模式 - ECO 功能                                                     |
| binary_sensor.{DEVICEID}\_eco_timer_state       | binary_sensor | Mode - ECO Timer                              | 模式 - ECO 定时                                                     |
| binary_sensor.{DEVICEID}\_heat                  | binary_sensor | Capability - Heating                          | 功能 - 制热                                                         |
| binary_sensor.{DEVICEID}\_cool                  | binary_sensor | Capability - Cooling                          | 功能 - 制冷                                                         |
| binary_sensor.{DEVICEID}\_dhw                   | binary_sensor | Capability - DHW                              | 功能 - 生活热水                                                     |
| binary_sensor.{DEVICEID}\_double_zone           | binary_sensor | Capability - Double Zone                      | 功能 - 双区                                                         |
| binary_sensor.{DEVICEID}\_room_thermal_support  | binary_sensor | Capability - Room Thermostat                  | 功能 - 室内温控器                                                   |
| binary_sensor.{DEVICEID}\_room_thermal_state    | binary_sensor | Status - Room Thermostat                      | 状态 - 室内温控器                                                   |
| binary_sensor.{DEVICEID}\_time_set              | binary_sensor | Capability - Time Set                         | 功能 - 时间已设置                                                   |
| binary_sensor.{DEVICEID}\_disinfect_run         | binary_sensor | DHW - Disinfect Running                       | 生活热水 - 杀菌运行中                                               |
| binary_sensor.{DEVICEID}\_remote_onoff          | binary_sensor | Capability - Remote On/Off                    | 功能 - 远程开关                                                     |
| binary_sensor.{DEVICEID}\_tbh_control           | binary_sensor | Capability - TBH Control                      | 功能 - TBH 控制                                                     |
| binary_sensor.{DEVICEID}\_sys_energy_ana_en     | binary_sensor | Capability - Energy Analysis (System)         | 功能 - 能耗分析 (系统)                                              |
| binary_sensor.{DEVICEID}\_hmi_energy_ana_set_en | binary_sensor | Capability - Energy Analysis (HMI)            | 功能 - 能耗分析 (HMI)                                               |
| binary_sensor.{DEVICEID}\_pump_i_running        | binary_sensor | Pump_I - Internal                             | Pump_I - 内置                                                       |
| binary_sensor.{DEVICEID}\_pump_o_running        | binary_sensor | Pump_O - External                             | Pump_O - 外置                                                       |
| binary_sensor.{DEVICEID}\_pump_d_running        | binary_sensor | Pump_D - DHW                                  | Pump_D - 生活热水                                                   |
| binary_sensor.{DEVICEID}\_pump_c_running        | binary_sensor | Pump_C - Mixed Water Loop Zone 2              | Pump_C - 二区混水回路                                               |
| binary_sensor.{DEVICEID}\_pump_s_running        | binary_sensor | Pump_S - Solar                                | Pump_S - 太阳能（诊断，默认禁用）                                   |
| binary_sensor.{DEVICEID}\_sv1_open              | binary_sensor | SV1 - Valve (DHW)                             | SV1 - 阀门 (生活热水)                                               |
| binary_sensor.{DEVICEID}\_sv2_open              | binary_sensor | SV2 - Valve (Heating)                         | SV2 - 阀门 (制热)                                                   |
| binary_sensor.{DEVICEID}\_load_output_tbh       | binary_sensor | Heater - Tank Backup (TBH)                    | 电加热 - 水箱 (TBH)                                                 |
| binary_sensor.{DEVICEID}\_ibh1_on               | binary_sensor | Heater - IBH1                                 | 电加热 - IBH1                                                       |
| binary_sensor.{DEVICEID}\_ibh2_on               | binary_sensor | Heater - IBH2                                 | 电加热 - IBH2                                                       |
| binary_sensor.{DEVICEID}\_sv3_open              | binary_sensor | SV3 - Valve                                   | SV3 - 阀门（诊断，默认禁用）                                        |
| binary_sensor.{DEVICEID}\_crankcase_heater_on   | binary_sensor | Heater - Crankcase                            | 电加热 - 曲轴箱（诊断，默认禁用）                                   |
| binary_sensor.{DEVICEID}\_alarm_on              | binary_sensor | Error - Alarm                                 | 故障 - 报警（诊断，默认禁用）                                       |
| binary_sensor.{DEVICEID}\_aux_heat_on           | binary_sensor | Heater - Auxiliary Source                     | 电加热 - 辅助热源（诊断，默认禁用）                                 |
| binary_sensor.{DEVICEID}\_compressor_on         | binary_sensor | Compressor - Running                          | 压缩机 - 运行中                                                     |
| sensor.{DEVICEID}\_error_code                   | sensor        | Error Code                                    | 错误码                                                              |
| sensor.{DEVICEID}\_tank_actual_temperature      | sensor        | Tank Actual Temperature                       | 水箱实际温度                                                        |
| sensor.{DEVICEID}\_total_energy_consumption     | sensor        | Total Energy Consumption                      | 总能耗。</br>第一个值可能会延迟，因为更新仅在设备处于活动状态时发送 |
| sensor.{DEVICEID}\_total_produced_energy        | sensor        | Total Produced Energy                         | 总计产生能量                                                        |
| sensor.{DEVICEID}\_outdoor_temperature          | sensor        | Outdoor Temperature                           | 室外温度                                                            |
| sensor.{DEVICEID}\_temp_tw_in                   | sensor        | Temperature Tw_in - Water Inlet               | 温度 Tw_in - 进水                                                   |
| sensor.{DEVICEID}\_temp_tw_out                  | sensor        | Temperature Tw_out - Water Outlet             | 温度 Tw_out - 出水                                                  |
| sensor.{DEVICEID}\_instant_power0               | sensor        | Power - Heating Consumption                   | 功率 - 制热耗电                                                     |
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
| sensor.{DEVICEID}\_temp_t4                      | sensor        | Temperature T4 - Outdoor Ambient              | 温度 T4 - 室外环境                                                  |
| sensor.{DEVICEID}\_temp_t5                      | sensor        | Temperature T5 - Water Tank                   | 温度 T5 - 水箱                                                      |
| sensor.{DEVICEID}\_temp_ta                      | sensor        | Temperature Ta - Room Ambient                 | 温度 Ta - 室内环境                                                  |
| sensor.{DEVICEID}\_temp_tw2                     | sensor        | Temperature Tw2 - Zone 2 Water                | 温度 Tw2 - 二区水温                                                 |
| sensor.{DEVICEID}\_temp_tb_t1                   | sensor        | Temperature TB-T1 - Buffer Tank Top           | 温度 TB-T1 - 缓冲水箱上部                                           |
| sensor.{DEVICEID}\_temp_tb_t2                   | sensor        | Temperature TB-T2 - Buffer Tank Bottom        | 温度 TB-T2 - 缓冲水箱下部                                           |
| sensor.{DEVICEID}\_temp_tsolar                  | sensor        | Temperature Tsolar - Solar Panel              | 温度 Tsolar - 太阳能板                                              |
| sensor.{DEVICEID}\_water_flower                 | sensor        | Water - Flow Rate                             | 水 - 流量                                                           |
| sensor.{DEVICEID}\_water_pressure               | sensor        | Water - Pressure                              | 水 - 压力                                                           |
| sensor.{DEVICEID}\_dc_current                   | sensor        | ODU - DC Bus Current                          | 室外机 - 直流母线电流                                               |
| sensor.{DEVICEID}\_dc_bus_voltage               | sensor        | ODU - DC Bus Voltage                          | 室外机 - 直流母线电压                                               |
| sensor.{DEVICEID}\_current_unit_capacity        | sensor        | Current Unit Capacity (raw)                   | 当前机组能力（原始值）（诊断）                                      |
| sensor.{DEVICEID}\_instant_renew_power0         | sensor        | Power - Renewable Heating Capacity            | 功率 - 可再生制热能力                                               |
| sensor.{DEVICEID}\_room_rel_hum                 | sensor        | Room Relative Humidity                        | 室内相对湿度                                                        |
| sensor.{DEVICEID}\_comp_total_run_time          | sensor        | Energy - Compressor Run Time                  | 能耗 - 压缩机累计运行时间                                           |
| sensor.{DEVICEID}\_error_code_description       | sensor        | Error - Description                           | 故障 - 说明                                                         |
| sensor.{DEVICEID}\_hmi_sn_code                  | sensor        | HMI Serial                                    | 信息 - 线控器序列号                                                 |
| sensor.{DEVICEID}\_hydbox_subtype               | sensor        | Info - Hydraulic Box Subtype                  | 信息 - 水力模块子类型                                               |
| sensor.{DEVICEID}\_hydrobox_capacity            | sensor        | Info - Hydraulic Box Capacity                 | 信息 - 水力模块容量                                                 |
| sensor.{DEVICEID}\_idu_software_version_str     | sensor        | Info - IDU Software Version                   | 信息 - 室内机软件版本                                               |
| sensor.{DEVICEID}\_odu_software_version_str     | sensor        | Info - ODU Software Version                   | 信息 - 室外机软件版本                                               |
| sensor.{DEVICEID}\_machine_type                 | sensor        | Info - Machine Type                           | 信息 - 机型                                                         |
| sensor.{DEVICEID}\_odu_model                    | sensor        | Info - ODU Model Code                         | 信息 - 室外机型号代码                                               |
| sensor.{DEVICEID}\_t5s                          | sensor        | Temperature T5s - DHW Setpoint                | 温度 T5s - 生活热水设定值                                           |
| sensor.{DEVICEID}\_tas                          | sensor        | Temperature Tas - Air Setpoint                | 温度 Tas - 空气设定值                                               |
| sensor.{DEVICEID}\_idu_t1s1                     | sensor        | Temperature - Zone 1 Calculated (T1s)         | 温度 - 一区计算值 (T1s)                                             |
| sensor.{DEVICEID}\_idu_t1s2                     | sensor        | Temperature - Zone 2 Calculated (T1s)         | 温度 - 二区计算值 (T1s)                                             |
| sensor.{DEVICEID}\_zone1_temp_set               | sensor        | Temperature - Zone 1 Setpoint                 | 温度 - 一区设定值                                                   |
| sensor.{DEVICEID}\_zone2_temp_set               | sensor        | Temperature - Zone 2 Setpoint                 | 温度 - 二区设定值                                                   |
| sensor.{DEVICEID}\_disinfect_set_weekday        | sensor        | DHW - Disinfect Weekday                       | 生活热水 - 杀菌星期                                                 |
| sensor.{DEVICEID}\_disinfect_start_hour         | sensor        | DHW - Disinfect Start Hour                    | 生活热水 - 杀菌开始小时                                             |
| sensor.{DEVICEID}\_disinfect_start_minutes      | sensor        | DHW - Disinfect Start Minute                  | 生活热水 - 杀菌开始分钟                                             |
| switch.{DEVICEID}\_disinfect                    | switch        | DHW - Disinfect                               | 生活热水 - 杀菌                                                     |
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
| switch.{DEVICEID}\_holiday_on                   | switch        | Mode - Holiday                                | 模式 - 假期                                                         |

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
