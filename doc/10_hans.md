# 电源电器

通用单开关电源电器 (设备类型 0x10)。

## 特性

- 支持开关

## 自定义

无自定义

## 实体

### 默认实体

| 实体ID                   | 类型   | 描述     |
| ------------------------ | ------ | -------- |
| switch.{DEVICEID}\_power | switch | 开关实体 |

### 扩展传感器

无扩展传感器

## 服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性。服务数据:

| 名称      | 描述                            |
| --------- | ------------------------------- |
| device_id | 设备的 Appliance code (设备 ID) |
| attribute | "power"                         |
| value     | true 或 false                   |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: true
```
