# 电动窗帘

电动窗帘 / 卷帘电机 (设备类型 0x14)。

## 特性

- 支持窗帘控制 (打开 / 关闭 / 停止)
- 支持位置 (0-100%)
- 支持方向 (正向 / 反向)

## 自定义

无自定义

## 实体

### 默认实体

无默认实体

### 扩展传感器

| 实体ID                               | 类型   | 描述               |
| ------------------------------------ | ------ | ------------------ |
| select.{DEVICEID}\_curtain_status    | select | 打开 / 关闭 / 停止 |
| number.{DEVICEID}\_curtain_position  | number | 目标位置 (0-100%)  |
| select.{DEVICEID}\_curtain_direction | select | 电机方向           |
| sensor.{DEVICEID}\_software_version  | sensor | 设备软件版本       |
| sensor.{DEVICEID}\_error_code        | sensor | 错误代码           |

## 服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性。服务数据:

| 名称      | 描述                                                              |
| --------- | ----------------------------------------------------------------- |
| device_id | 设备的 Appliance code (设备 ID)                                   |
| attribute | "curtain_status"<br />"curtain_position"<br />"curtain_direction" |
| value     | "open" / "close" / "stop"; 0-100; "positive" / "reverse"          |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: curtain_position
  value: 50
```
