# 洗烘一体机

一体机通过单个 LAN 连接同时暴露洗衣机 (DB) 和干衣机 (DC) 两组功能。洗衣机实体以
`db_` 为前缀, 干衣机实体以 `dc_` 为前缀。

## 生成实体

### 默认实体

无默认实体

### 额外生成实体

| EntityID                                   | 类型   | 名称                        | 描述           |
| ------------------------------------------ | ------ | --------------------------- | -------------- |
| switch.{DEVICEID}\_db_power                | switch | Washer Power                | 洗衣机电源     |
| sensor.{DEVICEID}\_db_running_status       | sensor | Washer Status               | 洗衣机状态     |
| sensor.{DEVICEID}\_db_progress             | sensor | Washer Progress             | 洗衣机进度     |
| sensor.{DEVICEID}\_db_program              | sensor | Washer Program              | 洗衣机程序     |
| sensor.{DEVICEID}\_db_remain_time          | sensor | Washer Time Remaining       | 洗衣机剩余时间 |
| sensor.{DEVICEID}\_db_wash_time            | sensor | Washer Wash Time            | 洗衣机洗涤时间 |
| sensor.{DEVICEID}\_db_dehydration_time     | sensor | Washer Dehydration Time     | 洗衣机脱水时间 |
| sensor.{DEVICEID}\_db_dehydration_speed    | sensor | Washer Dehydration Speed    | 洗衣机脱水速度 |
| sensor.{DEVICEID}\_db_water_level          | sensor | Washer Water Level          | 洗衣机水位     |
| sensor.{DEVICEID}\_db_temperature          | sensor | Washer Temperature          | 洗衣机温度     |
| sensor.{DEVICEID}\_db_rinse_count          | sensor | Washer Rinse Count          | 洗衣机漂洗次数 |
| sensor.{DEVICEID}\_db_detergent            | sensor | Washer Detergent            | 洗衣机洗涤剂   |
| sensor.{DEVICEID}\_db_softener             | sensor | Washer Softener             | 洗衣机柔顺剂   |
| sensor.{DEVICEID}\_db_appointment_time     | sensor | Washer Appointment Time     | 洗衣机预约时间 |
| sensor.{DEVICEID}\_db_appointment_end_time | sensor | Washer Appointment End Time | 洗衣机预约结束 |
| sensor.{DEVICEID}\_db_error_code           | sensor | Washer Error Code           | 洗衣机错误码   |
| sensor.{DEVICEID}\_db_water_consumption    | sensor | Washer Water Consumption    | 洗衣机耗水量   |
| sensor.{DEVICEID}\_db_power_consumption    | sensor | Washer Power Consumption    | 洗衣机耗电量   |
| switch.{DEVICEID}\_dc_power                | switch | Dryer Power                 | 烘干机电源     |
| sensor.{DEVICEID}\_dc_running_status       | sensor | Dryer Status                | 烘干机状态     |
| sensor.{DEVICEID}\_dc_dry_status           | sensor | Dryer Dry Status            | 烘干机烘干状态 |
| sensor.{DEVICEID}\_dc_program              | sensor | Dryer Program               | 烘干机程序     |
| sensor.{DEVICEID}\_dc_remain_time          | sensor | Dryer Time Remaining        | 烘干机剩余时间 |
| sensor.{DEVICEID}\_dc_dry_time             | sensor | Dryer Dry Time              | 烘干机烘干时间 |
| sensor.{DEVICEID}\_dc_intensity            | sensor | Dryer Intensity             | 烘干机强度     |
| sensor.{DEVICEID}\_dc_appointment_time     | sensor | Dryer Appointment Time      | 烘干机预约时间 |
| sensor.{DEVICEID}\_dc_appointment_end_time | sensor | Dryer Appointment End Time  | 烘干机预约结束 |
| sensor.{DEVICEID}\_dc_error_code           | sensor | Dryer Error Code            | 烘干机错误码   |
| sensor.{DEVICEID}\_dc_water_consumption    | sensor | Dryer Water Consumption     | 烘干机耗水量   |
| sensor.{DEVICEID}\_dc_power_consumption    | sensor | Dryer Power Consumption     | 烘干机耗电量   |

## 服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置设备属性, 服务数据:

| 名称      | 描述                                                                                                        |
| --------- | ----------------------------------------------------------------------------------------------------------- |
| device_id | 设备的编号(Device ID)                                                                                       |
| attribute | "db_power"<br/>"dc_power"<br/>"db_running_status"<br/>"dc_running_status"<br/>"db_program"<br/>"dc_program" |
| value     | 电源/运行状态为 true 或 false; 程序为程序编号(整数)或程序名称(字符串)                                       |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: db_power
  value: true
```
