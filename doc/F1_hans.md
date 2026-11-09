# 泡茶机

自动泡茶 / 饮品机 (设备类型 0xF1)。

## 特性

- 支持开关
- 支持速度
- 支持工作 / 保温温度
- 支持工作 / 保温 / 预约时间
- 支持配方编号与工作模式
- 上报响应、工作状态 / 步骤 / 阶段、杯盖与杯子状态、当前时间与温度

## 自定义

无自定义

## 实体

### 默认实体

| 实体ID                   | 类型   | 描述     |
| ------------------------ | ------ | -------- |
| switch.{DEVICEID}\_power | switch | 开关实体 |

### 扩展传感器

| 实体ID                                   | 类型   | 描述     |
| ---------------------------------------- | ------ | -------- |
| number.{DEVICEID}\_f1_speed              | number | 速度     |
| number.{DEVICEID}\_f1_set_work_temp      | number | 工作温度 |
| number.{DEVICEID}\_f1_set_keep_warm_temp | number | 保温温度 |
| number.{DEVICEID}\_f1_set_work_time      | number | 工作时间 |
| number.{DEVICEID}\_f1_set_keep_warm_time | number | 保温时间 |
| number.{DEVICEID}\_f1_appoint_time       | number | 预约时间 |
| number.{DEVICEID}\_f1_code_id            | number | 配方编号 |
| number.{DEVICEID}\_f1_work_mode          | number | 工作模式 |
| sensor.{DEVICEID}\_f1_response_type      | sensor | 响应     |
| sensor.{DEVICEID}\_f1_work_status        | sensor | 工作状态 |
| sensor.{DEVICEID}\_f1_step_status        | sensor | 步骤状态 |
| sensor.{DEVICEID}\_f1_work_stage         | sensor | 工作阶段 |
| sensor.{DEVICEID}\_f1_lid_status         | sensor | 杯盖状态 |
| sensor.{DEVICEID}\_f1_cup_status         | sensor | 杯子状态 |
| sensor.{DEVICEID}\_f1_current_time       | sensor | 当前时间 |
| sensor.{DEVICEID}\_f1_current_temp       | sensor | 当前温度 |
| sensor.{DEVICEID}\_error_code            | sensor | 错误代码 |

## 服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性。服务数据:

| 名称      | 描述                                                                                                                                                                   |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| device_id | 设备的 Appliance code (设备 ID)                                                                                                                                        |
| attribute | "power"<br />"speed"<br />"set_work_temp"<br />"set_keep_warm_temp"<br />"set_work_time"<br />"set_keep_warm_time"<br />"appoint_time"<br />"code_id"<br />"work_mode" |
| value     | "power" 为 true/false; 数值属性为范围内的整数                                                                                                                          |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: true
```
