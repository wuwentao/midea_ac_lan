# 微蒸烤一体机

## 实体

### 默认实体

无默认实体

### 扩展实体

| EntityID                                        | 类型          | 名称                  | 描述     |
| ----------------------------------------------- | ------------- | --------------------- | -------- |
| binary_sensor.{DEVICEID}\_tank_ejected          | binary_sensor | Tank Ejected          | 水箱弹出 |
| binary_sensor.{DEVICEID}\_water_change_reminder | binary_sensor | Water Change Reminder | 换水提醒 |
| binary_sensor.{DEVICEID}\_door                  | binary_sensor | Door                  | 门状态   |
| binary_sensor.{DEVICEID}\_water_shortage        | binary_sensor | Water shortage        | 缺水提醒 |
| sensor.{DEVICEID}\_current_temperature          | sensor        | Current Temperature   | 当前温度 |
| sensor.{DEVICEID}\_status                       | sensor        | Status                | 当前状态 |
| sensor.{DEVICEID}\_time_remaining               | sensor        | Time Remaining        | 剩余时间 |

## 服务

无服务
