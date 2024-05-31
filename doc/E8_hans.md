# 慢炖锅

## 实体

### 默认实体

无默认实体

### 扩展实体

| EntityID                                 | 类型          | 名称                             | 描述     |
| ---------------------------------------- | ------------- | -------------------------------- | -------- |
| binary_sensor.{DEVICEID}\_finished       | binary_sensor | Cooking Finished                 | 烹饪完成 |
| binary_sensor.{DEVICEID}\_water_shortage | binary_sensor | Water Shortage (warning message) | 缺水     |
| sensor.{DEVICEID}\_status                | sensor        | Current Status                   | 当前状态 |
| sensor.{DEVICEID}\_time_remaining        | sensor        | Time Remaining                   | 剩余时间 |
| sensor.{DEVICEID}\_keep_warm_remaining   | sensor        | Keep Warm Remaining              | 保温时间 |
| sensor.{DEVICEID}\_working_time          | sensor        | Working Time                     | 工作时间 |
| sensor.{DEVICEID}\_target_temperature    | sensor        | Target Temperature               | 设定温度 |
| sensor.{DEVICEID}\_current_temperature   | sensor        | Current Temperature              | 当前温度 |

## 服务

无服务
