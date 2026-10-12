# 干衣机

## 生成实体

### 默认实体

无默认实体

### 额外生成实体

| EntityID                           | 类型   | 名称            | 描述     |
| ---------------------------------- | ------ | --------------- | -------- |
| sensor.{DEVICEID}\_progress        | sensor | Progress        | 进度     |
| sensor.{DEVICEID}\_time_remaining  | sensor | Time Remaining  | 剩余时间 |
| sensor.{DEVICEID}\_status          | sensor | Status          | 状态     |
| sensor.{DEVICEID}\_program         | sensor | Program         | 程序     |
| sensor.{DEVICEID}\_dryness_level   | sensor | Dryness Level   | 干燥档位 |
| sensor.{DEVICEID}\_dry_temperature | sensor | Dry Temperature | 干燥温度 |
| sensor.{DEVICEID}\_intensity       | sensor | Intensity       | 强度     |
| sensor.{DEVICEID}\_material        | sensor | Material        | 材质     |
| sensor.{DEVICEID}\_water_box       | sensor | Water Box       | 水箱     |
| sensor.{DEVICEID}\_door_warn       | sensor | Door Warn       | 开门警告 |
| sensor.{DEVICEID}\_ai_switch       | sensor | AI Switch       | AI开关   |
| sensor.{DEVICEID}\_error_code      | sensor | Error Code      | 错误码   |
| switch.{DEVICEID}\_power           | switch | Power           | 电源开关 |
| switch.{DEVICEID}\_start           | switch | Start           | 启动暂停 |

## 服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                  |
| --------- | --------------------- |
| device_id | 设备的编号(Device ID) |
| attribute | "power"<br/>"start"   |
| value     | true 或 false         |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: true
```

## 已验证型号的参数控制：38208801 / 子类型 13367

在集成“配置”中启用烘干程序、烘干度和烘干温度选择实体、多维除菌和智能防皱开关，以及定时加时数值实体。只有协议库识别到这个型号和子类型组合时，才提供新控件；原有传感器、电源和启停实体 ID 保持不变。

含本机确认的 36 个普通程序，包括校服、雪纺、摇粒绒、瑜伽服、萌宠除菌和各汉服™款式。暂不包含尚未确认写入协议的 DIY／花粉过敏烘。

开机并保持待机或暂停后调整参数；运行、预约和故障状态不能修改，调整参数不会启动烘干。显示以真实设备回报为准，不乐观赋值；当前程序不支持的字段保持不可用。

- 即穿＝2、储藏＝3；不支持烘干度的代码 0 不开放调整。
- 多维除菌同时设置模式与功能位，联动即穿，并限制烘干度菜单。加长时间由机器计算。
- 标准／低温使用独立的扩展温度字段；完整写入报文会保留防皱和季节参数。
- 定时烘（程序 26）提供 0–170 分钟加时，步长 10 分钟；机器总时长为 10–180 分钟。剩余时间仍读取设备回报。

需配套协议库功能合并发布，再由维护者更新集成的 `midea-lan` 依赖后才能使用。旧 SDK 下会跳过新控件，本功能 PR 不自行提升依赖版本。
