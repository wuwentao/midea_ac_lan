# 洗碗机

## 生成实体

### 默认实体

| EntityID                                        | 类型   | 名称                         | 描述                                 |
| ----------------------------------------------- | ------ | ---------------------------- | ------------------------------------ |
| select.{DEVICEID}\_mode_select                  | select | Wash Mode                    | 洗涤模式 (选择后立即启动)            |
| select.{DEVICEID}\_program                      | select | Program                      | 下次启动的程序 (不会立即启动)        |
| number.{DEVICEID}\_delay_minutes                | number | Delay                        | 预约时间, 分钟 (1-1440)              |
| switch.{DEVICEID}\_door_auto_open_setting       | switch | Door Auto-Open               | 下次启动时自动开门                   |
| select.{DEVICEID}\_additional_setting           | select | Load                         | 满载/半载 (仅 `76000228` 型号)       |
| number.{DEVICEID}\_wash_region_setting          | number | Wash Region                  | 下次启动的洗涤区域 (0-255)           |
| number.{DEVICEID}\_water_level_setting          | number | Water Level                  | 下次启动的水位 (0-255)               |
| number.{DEVICEID}\_water_strong_level_setting   | number | Water Pressure Level         | 下次启动的水压档位 (0-255)           |
| button.{DEVICEID}\_start                        | button | Start                        | 启动                                 |
| button.{DEVICEID}\_start_delayed                | button | Start Delayed                | 预约启动                             |
| button.{DEVICEID}\_cancel                       | button | Cancel                       | 取消 (运行中的程序或预约)            |
| button.{DEVICEID}\_pause                        | button | Pause                        | 暂停                                 |
| button.{DEVICEID}\_resume                       | button | Resume                       | 继续                                 |
| sensor.{DEVICEID}\_estimated_energy_consumption | sensor | Estimated Energy Consumption | 预估能耗 (仅 `7600024L`, `76000228`) |
| sensor.{DEVICEID}\_estimated_water_consumption  | sensor | Estimated Water Consumption  | 预估水耗 (仅 `7600024L`, `76000228`) |

> 启动程序: 在 **Program** 中选择程序, 按需设置 **Door Auto-Open** 和 **Load**,
> 然后按 **Start**。预约启动: 再设置 **Delay** 并按 **Start Delayed**。未选择
> Program 时, Start 使用设备上报的程序 (上次使用的程序)。**Wash Mode** 保持原有
> 行为, 选择后立即启动。
>
> **Cancel** 停止正在运行的程序, 或取消预约。在 `76000228` 型号上, 关闭电源开关
> 不会停止正在运行的程序。
>
> Program、Delay、Door Auto-Open 和 Load 保存在内存中, Home Assistant 重启后重置。
> 关机时也可以修改 Delay、Door Auto-Open 和 Load; Program、Wash Mode 和各按钮仅在洗碗机开机时可用。
>
> 能耗/水耗预估值来自各型号的说明书, 在一次洗涤完成时累加为总量。`76000228` 型号仅 ECO
> 程序的数据按 EN 60436 测得, 说明书称其余数据仅供参考。
>
> 程序、模式、状态、进度和运行状态显示可读名称 (英文和西班牙文; 其他语言显示英文),
> `76000228` 型号使用其面板上的程序名称。实体状态值保持库中的原始值 (`eco_wash`、
> `running` 等), 自动化不受影响。

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
| sensor.{DEVICEID}\_wrong_operation       | sensor        | Wrong Operation             | 误操作 (诊断)                                 |
| sensor.{DEVICEID}\_dry_set_min           | sensor        | Dry Set Time                | 烘干设定时间 (分钟)                           |
| sensor.{DEVICEID}\_filter_wash_time      | sensor        | 滤网累计洗涤时长              | 清洁复位后的累计洗涤分钟数 (云端只读查询，默认不启用) |
| sensor.{DEVICEID}\_clean_left_hour       | sensor        | Clean Remaining             | 剩余清洁时间 (小时)                           |
| sensor.{DEVICEID}\_kitchenware_left_hour | sensor        | Kitchenware Remaining       | 剩余餐具时间 (小时)                           |
| sensor.{DEVICEID}\_device_version        | sensor        | Device Version              | 设备版本 (诊断)                               |
| sensor.{DEVICEID}\_throw_percent         | sensor        | Dispense Level              | 投放余量 (百分比)                             |
| binary_sensor.{DEVICEID}\_uv             | binary_sensor | UV                          | 紫外线                                        |
| binary_sensor.{DEVICEID}\_dry            | binary_sensor | Dry                         | 烘干                                          |
| binary_sensor.{DEVICEID}\_dry_status     | binary_sensor | Drying                      | 烘干中                                        |
| binary_sensor.{DEVICEID}\_storage_status | binary_sensor | Storage Running             | 存储运行中                                    |
| binary_sensor.{DEVICEID}\_waterswitch    | binary_sensor | Water Switch                | 水路开关                                      |
| binary_sensor.{DEVICEID}\_water_lack     | binary_sensor | Water Shortage              | 缺水                                          |
| binary_sensor.{DEVICEID}\_wifi_unabled   | binary_sensor | WiFi Disabled               | WiFi 已禁用 (诊断)                            |
| binary_sensor.{DEVICEID}\_auto_throw     | binary_sensor | Auto Dispense               | 自动投放                                      |
| binary_sensor.{DEVICEID}\_lock_power     | binary_sensor | Power Lock                  | 电源锁                                        |
| binary_sensor.{DEVICEID}\_beep_control   | binary_sensor | Beep                        | 提示音                                        |
| binary_sensor.{DEVICEID}\_light_btn_on   | binary_sensor | Button Light                | 按键灯                                        |
| binary_sensor.{DEVICEID}\_light_strip_on | binary_sensor | Light Strip                 | 灯带                                          |
| lock.{DEVICEID}\_child_lock              | lock          | Child Lock                  | 童锁                                          |
| switch.{DEVICEID}\_power                 | switch        | Power                       | 电源开关                                      |
| switch.{DEVICEID}\_storage               | switch        | Storage                     | 保管开关                                      |
| switch.{DEVICEID}\_dry_setting           | switch        | Drying Switch               | 下次洗涤后的烘干开关 (型号 `7600644C`、`7600002B`、`760001EC`、`760RX20S`) |
| number.{DEVICEID}\_storage_set_time      | number        | Storage Duration            | 保管时长, 0–72 小时 (同上四个型号)            |

洗碗机上报状态后，在集成的扩展控制中勾选 **烘干开关** 和 **保管时长**。
`7600644C` 的 App 把该开关称为 **消毒烘干**，因此该型号显示这一名称；
其他已验证型号显示 **烘干开关**。**烘干中** 仍表示设备正在烘干。
**保管时长** 显示设备设定的时长，不是保管剩余时间；调整它不会打开 **保管开关**。

这两个控制只对厂商 Lua 中确有相同命令的型号声明：`7600644C`（子类型 `3`，
已实机验证）以及 `7600002B`、`760001EC`、`760RX20S`（仅按各自型号 Lua 核对，
尚未实机验证）。其他型号（包括 `76000228`、`7600024L`）不会创建设两个实体。

**滤网累计洗涤时长** 默认不启用，所有 E1 洗碗机均可选。
如需使用，请在集成选项中勾选该传感器，并配置自己已绑定这台洗碗机的美的美居账号。
传感器通过 HTTPS 只读查询美的美居云端，不从局域网读取。数值单位为分钟，
累计洗涤时间，不含烘干及保管。清洗滤网后，在 App 中执行清洁复位会使该数值下降。
该云端查询目前仅在 `7600644C` 的 App 插件中确认；其他型号若云端返回缺失或非法值，
传感器保持不可用。

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

| attribute                  | value                                    |
| -------------------------- | ---------------------------------------- |
| child_lock                 | true 或 false                            |
| power                      | true 或 false                            |
| storage                    | true 或 false                            |
| dry_setting                | true 或 false (型号 `7600644C`、`7600002B`、`760001EC`、`760RX20S`) |
| storage_set_time            | 0 至 72 整数小时 (同上四个型号)          |
| mode_select                | 程序名, 如 `eco_wash`; 立即启动          |
| program                    | 程序名, 如 `eco_wash` (不会启动)         |
| delay_minutes              | 1 至 1440                                |
| door_auto_open_setting     | true 或 false                            |
| additional_setting         | 0 (满载) 或 2 (半载), 仅 `76000228` 型号 |
| wash_region_setting        | 0 至 255                                 |
| water_level_setting        | 0 至 255                                 |
| water_strong_level_setting | 0 至 255                                 |

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
