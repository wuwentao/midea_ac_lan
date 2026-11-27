# 电热水器

## 特性

- 支持温度设定
- 支持杀菌(sterilization)、增容(E+)、智能省电和 Memo U(记忆模式)开关
- 可选显示内胆、进水、水量、加热管状态和水流等遥测数据

在官方 Lua 协议中，增容、智能省电和 Memo U 是互斥模式。请只启用美居中该型号实际提供的可选控制。不要关闭本来就未启用的模式开关：协议的关闭命令会清除当前正在使用的模式，而不区分由哪个模式开关发出。需要切换模式时应直接打开目标模式；需要退出附加模式时，只关闭当前已启用的模式。

全胆速热开关打开时选择全胆，关闭时选择半胆；半胆加热二进制传感器显示设备确认后的选择状态。

## 自定义

- 设置设备控制协议 (默认为"auto").
  美的使用了两种不同的协议来控制电热水器，"旧协议" 或 "新协议".
  如果你无法控制你的热水器，可以尝试改变此项的值试试看。
  可选值包括true,false,"auto"

```json
{ "old_protocol": true }
```

增容、智能省电和 Memo U 需要使用新协议。对于 `5100077J` 等 subtype `0` 设备，测试这些控制前必须明确选择新协议：

```json
{ "old_protocol": false }
```

- 设置热水器温度基数为整度还是半度 (false 为整度 true 为半度, 默认为 false)

  如果你的热水器显示的温度为实际温度的两倍，请将该值设为true。

```json
{ "precision_halves": true }
```

- 设置温度调整步长(默认为1).

```json
{ "temperature_step": 0.5 }
```

- 设置加热功率倍率(默认为1).

  部分电热水器型号上报的是额定加热功率，可能与实际测量功耗不一致。可以使用 `heating_power_multiplier` 校准 `sensor.{DEVICEID}_heating_power` 的数值；未配置时保持默认行为不变。

  例如，如果设备上报 `2000 W`，但实际测量功耗为 `1500 W`，可以使用 `0.75` 作为倍率：

```json
{ "heating_power_multiplier": 0.75 }
```

## 生成实体

### 默认生成实体

| 实体ID                                | 类型         | 描述       |
| ------------------------------------- | ------------ | ---------- |
| water_heater.{DEVICEID}\_water_heater | water_heater | 热水器实体 |

### 额外生成实体

| EntityID                                  | 类型          | 名称                    | 描述         |
| ----------------------------------------- | ------------- | ----------------------- | ------------ |
| binary_sensor.{DEVICEID}\_heating         | binary_sensor | Heating                 | 加热         |
| binary_sensor.{DEVICEID}\_keep_warm       | binary_sensor | Keep Warm               | 保温         |
| binary_sensor.{DEVICEID}\_protection      | binary_sensor | Protection              | 安全防护     |
| binary_sensor.{DEVICEID}\_half_heat       | binary_sensor | Half Tank Heating       | 半胆加热     |
| binary_sensor.{DEVICEID}\_bottom_heat     | binary_sensor | Bottom Tank Heating     | 下胆加热     |
| binary_sensor.{DEVICEID}\_top_heat        | binary_sensor | Top Tank Heating        | 上胆加热     |
| binary_sensor.{DEVICEID}\_fast_hot_power  | binary_sensor | Fast Heating            | 快速加热     |
| binary_sensor.{DEVICEID}\_water_flow      | binary_sensor | Water Flow              | 水流         |
| sensor.{DEVICEID}\_current_temperature    | sensor        | Current Temperature     | 当前温度     |
| sensor.{DEVICEID}\_top_temp               | sensor        | Top Temperature         | 顶部温度     |
| sensor.{DEVICEID}\_in_temperature         | sensor        | Inlet Temperature       | 进水温度     |
| sensor.{DEVICEID}\_heating_time_remaining | sensor        | Heating Time Remaining  | 剩余加热时间 |
| sensor.{DEVICEID}\_heating_power          | sensor        | Heating Power           | 加热功率     |
| sensor.{DEVICEID}\_rate                   | sensor        | Rated Power             | 额定功率     |
| sensor.{DEVICEID}\_heat_water_level       | sensor        | Heated Water Level      | 热水量       |
| sensor.{DEVICEID}\_water_consumption      | sensor        | Water Consumption       | 累计用水量   |
| sensor.{DEVICEID}\_day_water_consumption  | sensor        | Daily Water Consumption | 当日用水量   |
| sensor.{DEVICEID}\_volume                 | sensor        | Tank Volume             | 内胆容量     |
| switch.{DEVICEID}\_eplus                  | switch        | Capacity Plus           | 增容         |
| switch.{DEVICEID}\_efficient              | switch        | Smart Power Saving      | 智能省电     |
| switch.{DEVICEID}\_memory                 | switch        | Memo U                  | 记忆模式     |
| switch.{DEVICEID}\_power                  | switch        | Power                   | 电源开关     |
| switch.{DEVICEID}\_sterilization          | switch        | Sterilization           | 杀菌         |
| switch.{DEVICEID}\_variable_heating       | switch        | Variable Heating        | 变频加热     |
| switch.{DEVICEID}\_whole_tank_heating     | switch        | Whole Tank Heating      | 全胆速热     |

## 服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                                                                                                                      |
| --------- | ------------------------------------------------------------------------------------------------------------------------- |
| device_id | 设备的编号(Device ID)                                                                                                     |
| attribute | "efficient"<br />"eplus"<br />"memory"<br />"power"<br />"sterilization"<br />"variable_heating"<br/>"whole_tank_heating" |
| value     | true 或 false                                                                                                             |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: variable_heating
  value: true
```
