# 壁挂炉

## 生成实体

### 默认实体

| 实体ID                                        | 类型         | 描述           |
| --------------------------------------------- | ------------ | -------------- |
| water_heater.{DEVICEID}\_water_heater_heating | water_heater | 取暖热水器实体 |
| water_heater.{DEVICEID}\_water_heater_bathing | water_heater | 淋浴热水器实体 |

### Extra entities

| 实体ID                                         | 类型          | 名称                              | 描述         |
| ---------------------------------------------- | ------------- | --------------------------------- | ------------ |
| binary_sensor.{DEVICEID}\_heating_working      | binary_sensor | Heating Working Status            | 取暖工作状态 |
| binary_sensor.{DEVICEID}\_bathing_working      | binary_sensor | Bathing Working Status            | 领域工作状态 |
| sensor.{DEVICEID}\_heating_leaving_temperature | sensor        | Heating Leaving Water Temperature | 取暖出水温度 |
| sensor.{DEVICEID}\_bathing_leaving_temperature | sensor        | Bathing Leaving Water Temperature | 淋浴出水温度 |
| switch.{DEVICEID}\_main_power                  | switch        | Main power                        | 主电源       |
| sensor.{DEVICEID}\_heating_power               | switch        | Heating power                     | 取暖电源     |

## 服务

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                              |
| --------- | --------------------------------- |
| device_id | 设备的编号(Device ID)             |
| attribute | "main_power"<br />"heating_power" |
| value     | true or false                     |

示例

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: main_power
  value: true
```
