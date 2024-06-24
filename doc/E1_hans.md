# 洗碗机

## 生成实体

### 默认实体

无默认实体

### 额外生成实体

| EntityID                             | 类型          | 名称                   | 描述         |
| ------------------------------------ | ------------- | ---------------------- | ------------ |
| binary_sensor.{DEVICEID}\_door       | binary_sensor | Door                   | 门状态       |
| binary_sensor.{DEVICEID}\_rinse_aid  | binary_sensor | Rinse Aid Shortage     | 漂洗剂不足   |
| binary_sensor.{DEVICEID}\_salt       | binary_sensor | Salt Shortage          | 软水盐不足   |
| sensor.{DEVICEID}\_humidity          | sensor        | Humidity               | 湿度         |
| sensor.{DEVICEID}\_progress          | sensor        | Progress               | 当前程序     |
| sensor.{DEVICEID}\_status            | sensor        | Status                 | 状态         |
| sensor.{DEVICEID}\_storage_remaining | sensor        | Storage Time Remaining | 保管剩余时间 |
| sensor.{DEVICEID}\_time_remaining    | sensor        | Time Remaining         | 剩余时间     |
| sensor.{DEVICEID}\_temperature       | sensor        | Temperature            | 温度         |
| sensor.{DEVICEID}\_mode              | sensor        | Working Mode           | 工作模式     |
| sensor.{DEVICEID}\_error_code        | sensor        | Error Code             | 错误码       |
| sensor.{DEVICEID}\_softwater         | sensor        | Softwater Level        | 软水盐档位   |
| sensor.{DEVICEID}\_bright            | sensor        | Bright Level           | 亮碟剂档位   |
| lock.{DEVICEID}\_child_lock          | lock          | Child Lock             | 童锁         |
| switch.{DEVICEID}\_power             | switch        | Power                  | 电源开关     |
| switch.{DEVICEID}\_storage           | switch        | Storage                | 保管开关     |

## 服务

生成以下扩展服务

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                                      |
| --------- | ----------------------------------------- |
| device_id | 设备的编号(Device ID)                     |
| attribute | "child_lock"<br />"power"<br /> "storage" |
| value     | true 或 false                             |

示例

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: true
```
