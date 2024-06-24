# 干衣机

## 生成实体

### 默认实体

无默认实体

### 额外生成实体

| EntityID                          | 类型   | 名称           | 描述     |
| --------------------------------- | ------ | -------------- | -------- |
| sensor.{DEVICEID}\_progress       | sensor | Progress       | 当前程序 |
| sensor.{DEVICEID}\_time_remaining | sensor | Time Remaining | 剩余时间 |
| switch.{DEVICEID}\_power          | switch | Power          | 电源开关 |
| switch.{DEVICEID}\_start          | switch | Start          | 启动暂停 |

## 服务

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                  |
| --------- | --------------------- |
| device_id | 设备的编号(Device ID) |
| attribute | "power"<br/>"start"   |
| value     | true 或 false         |

示例

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: true
```
