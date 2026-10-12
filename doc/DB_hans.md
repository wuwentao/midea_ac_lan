# 滚筒洗衣机

## 生成实体

### 默认实体

无默认实体

### 额外生成实体

| EntityID                                  | 类型   | 名称                   | 描述             |
| ----------------------------------------- | ------ | ---------------------- | ---------------- |
| sensor.{DEVICEID}\_status                 | sensor | Status                 | 状态             |
| sensor.{DEVICEID}\_mode                   | sensor | Mode                   | 模式             |
| sensor.{DEVICEID}\_progress               | sensor | Progress               | 进度             |
| sensor.{DEVICEID}\_program                | sensor | Program                | 程序             |
| sensor.{DEVICEID}\_water_level            | sensor | Water Level            | 水位             |
| sensor.{DEVICEID}\_temperature            | sensor | Temperature            | 温度             |
| sensor.{DEVICEID}\_dehydration_speed      | sensor | Dehydration Speed      | 脱水速度         |
| sensor.{DEVICEID}\_dehydration_time       | sensor | dehydration Time       | 脱水时间档位     |
| sensor.{DEVICEID}\_dehydration_time_value | sensor | Dehydration Time Value | 脱水时间值       |
| sensor.{DEVICEID}\_wash_time              | sensor | Wash Time              | 洗涤时间档位     |
| sensor.{DEVICEID}\_wash_time_value        | sensor | Wash Time Value        | 洗涤时间值       |
| sensor.{DEVICEID}\_time_remaining         | sensor | Time Remaining         | 剩余时间         |
| sensor.{DEVICEID}\_detergent              | sensor | Detergent              | 洗涤剂           |
| sensor.{DEVICEID}\_softener               | sensor | Softener               | 柔顺剂           |
| sensor.{DEVICEID}\_stains                 | sensor | Stains                 | 污渍             |
| sensor.{DEVICEID}\_dirty_degree           | sensor | Dirty Degree           | 脏度             |
| switch.{DEVICEID}\_power                  | switch | Power                  | 电源开关         |
| switch.{DEVICEID}\_start                  | switch | Start                  | 启动暂停         |
| select.{DEVICEID}\_program_control        | select | Washer program         | 洗衣程序         |
| select.{DEVICEID}\_temperature_control    | select | Water temperature      | 水温             |
| select.{DEVICEID}\_spin_speed_control     | select | Spin speed             | 转速             |
| select.{DEVICEID}\_rinse_count            | select | Rinse count            | 漂洗次数         |
| select.{DEVICEID}\_water_level_control    | select | Water level            | 水位             |
| select.{DEVICEID}\_detergent_control      | select | Detergent dosing       | 洗衣液           |
| select.{DEVICEID}\_wash_time_control      | select | Wash time (min)        | 洗涤时间（分钟） |
| select.{DEVICEID}\_spin_time_control      | select | Spin time (min)        | 脱水时间（分钟） |
| switch.{DEVICEID}\_forget_free            | switch | Forget-free care       | 忘取无忧         |

参数实体需要已验证的型号／子类型和支持该功能的 SDK。可用性还取决于当前程序和设备状态，详见下方已验证型号的参数控制说明。

## 服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                  |
| --------- | --------------------- |
| device_id | 设备的编号(Device ID) |
| attribute | 下表列出的可写属性    |
| value     | 下表中该属性的值      |

| 可写属性              | 可用值                                                         |
| --------------------- | -------------------------------------------------------------- |
| `power`, `start`      | `true` 或 `false`                                              |
| `program_control`     | 程序选择实体当前 `options` 中的程序选项键                      |
| `temperature_control` | `"cold"`、`"20"`、`"30"`、`"40"`、`"60"`、`"95"`               |
| `spin_speed_control`  | `"0"`、`"400"`、`"600"`、`"800"`、`"1000"`、`"1200"`、`"1400"` |
| `rinse_count`         | `"1"`、`"2"`、`"3"`、`"4"`                                     |
| `water_level_control` | `"auto"`、`"l1"`、`"l2"`、`"l3"`、`"l4"`                       |
| `detergent_control`   | `"smart"`、`"off"`、`"l1"`、`"l2"`、`"l3"`、`"l4"`             |
| `wash_time_control`   | 选择实体当前 `options` 中的实际分钟数，使用字符串              |
| `spin_time_control`   | 选择实体当前 `options` 中的实际分钟数，使用字符串              |
| `forget_free`         | `true` 或 `false`                                              |

选择参数时使用选项键，不使用界面翻译后的名称，并且只能选择对应实体当前提供的选项。例如 `wash_time_control: "45"` 表示实际洗涤 45 分钟，不是写入请求码 45。服务写入与实体有相同的型号、SDK、程序和状态限制。

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: true
```

## 已验证型号的参数控制：38131140 / 子类型 13145

在集成“配置”中启用程序、水温、转速、漂洗次数、水位、洗衣液、洗涤时间和脱水时间选择实体，以及“忘取无忧”开关。只有协议库识别到这个型号和子类型组合时，才提供这些控件；原有传感器、电源和启停实体 ID 保持不变。

程序菜单含本机确认的 30 个程序，包括深度筒自洁、瑜伽服和速干衣。开机并保持待机后调整参数；运行、预约、故障及维修模式不能修改。调整参数不会启动洗衣。

时间控件以实际分钟显示，选项根据当前实际时间和请求等级更新。例如混合洗冷水时为 42／45／50／55／60 分钟，30℃时为 11／14／19／24／29。脱水 8／9／10／11／12 分钟对应请求码 3／4／0／1／2，不能直接写分钟数。洗衣液智能和 L4 分别为 4 和 5。缺失或不支持的参数保持不可用，不补成默认值。

忘取无忧使用该型号 V2 新风开关，保留当前完整程序设置，包括自定义洗涤／脱水时间。显示以真实机器回报为准；这些参数控制无需云端连接。

需配套协议库功能合并发布，再由维护者更新集成的 `midea-lan` 依赖后才能使用。旧 SDK 下会跳过新控件，本功能 PR 不自行提升依赖版本。
