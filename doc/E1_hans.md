# 洗碗机

## 生成实体

### 默认实体

| EntityID                                        | 类型   | 名称                         | 描述                           |
| ----------------------------------------------- | ------ | ---------------------------- | ------------------------------ |
| select.{DEVICEID}\_mode_select                  | select | Wash Mode                    | 洗涤模式 (选择后立即启动)      |
| select.{DEVICEID}\_program                      | select | Program                      | 下次启动的程序 (不会立即启动)  |
| number.{DEVICEID}\_delay_minutes                | number | Delay                        | 预约时间, 分钟 (1-1440)        |
| switch.{DEVICEID}\_door_auto_open_setting       | switch | Door Auto-Open               | 下次启动时自动开门             |
| select.{DEVICEID}\_additional_setting           | select | Load                         | 满载/半载 (仅 `76000228` 型号) |
| button.{DEVICEID}\_start                        | button | Start                        | 启动                           |
| button.{DEVICEID}\_start_delayed                | button | Start Delayed                | 预约启动                       |
| button.{DEVICEID}\_cancel                       | button | Cancel                       | 取消 (运行中的程序或预约)      |
| button.{DEVICEID}\_pause                        | button | Pause                        | 暂停                           |
| button.{DEVICEID}\_resume                       | button | Resume                       | 继续                           |
| sensor.{DEVICEID}\_estimated_energy_consumption | sensor | Estimated Energy Consumption | 预估能耗 (仅 `7600024L`)       |
| sensor.{DEVICEID}\_estimated_water_consumption  | sensor | Estimated Water Consumption  | 预估水耗 (仅 `7600024L`)       |

> 启动程序: 在 **Program** 中选择程序, 按需设置 **Door Auto-Open** 和 **Load**,
> 然后按 **Start**。预约启动: 再设置 **Delay** 并按 **Start Delayed**。未选择
> Program 时, Start 使用设备上报的程序 (上次使用的程序)。**Wash Mode** 保持原有
> 行为, 选择后立即启动。
>
> **Cancel** 停止正在运行的程序, 或取消预约。在 `76000228` 型号上, 关闭电源开关
> 不会停止正在运行的程序。
>
> Program、Delay、Door Auto-Open 和 Load 保存在内存中, Home Assistant 重启后重置。
> 关机时也可以修改这些设置; Program、Wash Mode 和各按钮仅在洗碗机开机时可用。

### 额外生成实体

| EntityID                                 | 类型          | 名称                        | 描述                                          |
| ---------------------------------------- | ------------- | --------------------------- | --------------------------------------------- |
| binary_sensor.{DEVICEID}\_door           | binary_sensor | Door                        | 门状态                                        |
| binary_sensor.{DEVICEID}\_rinse_aid      | binary_sensor | Rinse Aid Shortage          | 漂洗剂不足                                    |
| binary_sensor.{DEVICEID}\_salt           | binary_sensor | Salt Shortage               | 软水盐不足                                    |
| sensor.{DEVICEID}\_humidity              | sensor        | Humidity                    | 湿度                                          |
| sensor.{DEVICEID}\_progress              | sensor        | Progress                    | 当前程序                                      |
| sensor.{DEVICEID}\_status                | sensor        | Status                      | 状态                                          |
| sensor.{DEVICEID}\_storage_remaining     | sensor        | Storage Time Remaining      | 保管剩余时间                                  |
| sensor.{DEVICEID}\_time_remaining        | sensor        | Time Remaining              | 剩余时间                                      |
| sensor.{DEVICEID}\_delay_remaining       | sensor        | Delayed Start Remaining     | 预约剩余时间 (分钟)                           |
| sensor.{DEVICEID}\_operator              | sensor        | Run State                   | 运行状态 (start 或 pause)                     |
| binary_sensor.{DEVICEID}\_door_auto_open | binary_sensor | Last Program Door Auto-Open | 上一程序是否自动开门 (断电或新程序启动前保持) |
| sensor.{DEVICEID}\_temperature           | sensor        | Temperature                 | 温度                                          |
| sensor.{DEVICEID}\_mode                  | sensor        | Working Mode                | 工作模式                                      |
| sensor.{DEVICEID}\_error_code            | sensor        | Error Code                  | 错误码                                        |
| sensor.{DEVICEID}\_softwater             | sensor        | Softwater Level             | 软水盐档位                                    |
| sensor.{DEVICEID}\_bright                | sensor        | Bright Level                | 亮碟剂档位                                    |
| lock.{DEVICEID}\_child_lock              | lock          | Child Lock                  | 童锁                                          |
| switch.{DEVICEID}\_power                 | switch        | Power                       | 电源开关                                      |
| switch.{DEVICEID}\_storage               | switch        | Storage                     | 保管开关                                      |

## 服务

生成以下扩展服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                  |
| --------- | --------------------- |
| device_id | 设备的编号(Device ID) |
| attribute | 见下表                |
| value     | 见下表                |

| attribute              | value                                    |
| ---------------------- | ---------------------------------------- |
| child_lock             | true 或 false                            |
| power                  | true 或 false                            |
| storage                | true 或 false                            |
| mode_select            | 程序名, 如 `eco_wash`; 立即启动          |
| program                | 程序名, 如 `eco_wash` (不会启动)         |
| delay_minutes          | 1 至 1440                                |
| door_auto_open_setting | true 或 false                            |
| additional_setting     | 0 (满载) 或 2 (半载), 仅 `76000228` 型号 |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: true
```

示例: ECO 程序, 自动开门, 2 小时后启动

```yaml
- service: midea_ac_lan.set_attribute
  data:
    device_id: XXXXXXXXXXXX
    attribute: program
    value: eco_wash
- service: midea_ac_lan.set_attribute
  data:
    device_id: XXXXXXXXXXXX
    attribute: door_auto_open_setting
    value: true
- service: midea_ac_lan.set_attribute
  data:
    device_id: XXXXXXXXXXXX
    attribute: delay_minutes
    value: 120
- service: button.press
  target:
    entity_id: button.XXXXXXXXXXXX_start_delayed
```
