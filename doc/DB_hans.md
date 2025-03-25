# 滚筒洗衣机

## 生成实体

### 默认实体

无默认实体

### 额外生成实体

| EntityID                                  | 类型   | 名称                   | 描述         |
| ----------------------------------------- | ------ | ---------------------- | ------------ |
| sensor.{DEVICEID}\_status                 | sensor | Status                 | 状态         |
| sensor.{DEVICEID}\_mode                   | sensor | Mode                   | 模式         |
| sensor.{DEVICEID}\_progress               | sensor | Progress               | 进度         |
| sensor.{DEVICEID}\_program                | sensor | Program                | 程序         |
| sensor.{DEVICEID}\_water_level            | sensor | Water Level            | 水位         |
| sensor.{DEVICEID}\_temperature            | sensor | Temperature            | 温度         |
| sensor.{DEVICEID}\_dehydration_speed      | sensor | Dehydration Speed      | 脱水速度     |
| sensor.{DEVICEID}\_dehydration_time       | sensor | dehydration Time       | 脱水时间档位 |
| sensor.{DEVICEID}\_dehydration_time_value | sensor | Dehydration Time Value | 脱水时间值   |
| sensor.{DEVICEID}\_wash_time              | sensor | Wash Time              | 洗涤时间档位 |
| sensor.{DEVICEID}\_wash_time_value        | sensor | Wash Time Value        | 洗涤时间值   |
| sensor.{DEVICEID}\_time_remaining         | sensor | Time Remaining         | 剩余时间     |
| sensor.{DEVICEID}\_detergent              | sensor | Detergent              | 洗涤剂       |
| sensor.{DEVICEID}\_softener               | sensor | Softener               | 柔顺剂       |
| sensor.{DEVICEID}\_stains                 | sensor | Stains                 | 污渍         |
| sensor.{DEVICEID}\_dirty_degree           | sensor | Dirty Degree           | 脏度         |
| switch.{DEVICEID}\_power                  | switch | Power                  | 电源开关     |
| switch.{DEVICEID}\_start                  | switch | Start                  | 启动暂停     |

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
