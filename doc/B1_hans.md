# 电烤箱

## 实体

### 默认实体

无默认实体

### 额外生成实体

| EntityID                                        | 类型          | 名称                                     | 描述               |
| ----------------------------------------------- | ------------- | ---------------------------------------- | ------------------ |
| binary_sensor.{DEVICEID}\_door                  | binary_sensor | Door Status                              | 门状态             |
| binary_sensor.{DEVICEID}\_tank_ejected          | binary_sensor | Tank Ejected (warnning message)          | 水箱弹出(警告信息) |
| binary_sensor.{DEVICEID}\_water_change_reminder | binary_sensor | Water Change Reminder (warnning message) | 换水提醒(警告信息) |
| binary_sensor.{DEVICEID}\_water_shortage        | binary_sensor | Water Shortage (warnning message)        | 缺水(警告信息)     |
| sensor.{DEVICEID}\_current_temperature          | sensor        | Current Temperatur                       | 当前温度           |
| sensor.{DEVICEID}\_status                       | sensor        | Current Status                           | 当前状态           |
| sensor.{DEVICEID}\_time_remaining               | sensor        | Time Remaining                           | 剩余时间           |

## 服务

无服务.
