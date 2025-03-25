# 空气盒子

## 特性

- 空气盒子的空气传感器数据
- 空气盒子的睡眠模块数据

## 生成实体

### 额外生成实体

| EntityID                                     | 类型          | 名称                    | 描述             |
| -------------------------------------------- | ------------- | ----------------------- | ---------------- |
| sensor.{DEVICEID}\_temperature               | Sensor        | Temperature             | 温度原始值       |
| sensor.{DEVICEID}\_temperature_compensate    | Sensor        | Temperature Compensate  | 温度补偿值       |
| sensor.{DEVICEID}\_humidity                  | Sensor        | Humidity                | 湿度原始值       |
| sensor.{DEVICEID}\_humidity_compensate       | Sensor        | Humidity Compensate     | 湿度补偿值       |
| sensor.{DEVICEID}\_tvoc                      | Sensor        | TVOC                    | 总挥发性有机物   |
| sensor.{DEVICEID}\_co2                       | Sensor        | Carbon Dioxide          | 二氧化碳浓度     |
| sensor.{DEVICEID}\_pm25                      | Sensor        | PM 2.5                  | 细颗粒物浓度     |
| sensor.{DEVICEID}\_hcho                      | Sensor        | Methanal                | 甲醛浓度         |
| binary_sensor.{DEVICEID}\_presets_function   | Binary Sensor | Presets Function        | 预设功能状态     |
| binary_sensor.{DEVICEID}\_fall_asleep_status | Binary Sensor | Asleep Status           | 入睡状态         |
| binary_sensor.{DEVICEID}\_portable_sense     | Binary Sensor | Portable Sense          | 便携感应状态     |
| binary_sensor.{DEVICEID}\_night_mode         | Binary Sensor | Night Mode              | 夜间模式状态     |
| binary_sensor.{DEVICEID}\_screen_status      | Binary Sensor | Screen Status           | 屏幕开关状态     |
| binary_sensor.{DEVICEID}\_led_status         | Binary Sensor | Ambient Lighting Status | 氛围灯状态       |
| binary_sensor.{DEVICEID}\_arofene_link       | Binary Sensor | Methanal Status         | 甲醛模块连接状态 |
| binary_sensor.{DEVICEID}\_radar_exist        | Binary Sensor | Radar Status            | 雷达模块存在状态 |
| binary_sensor.{DEVICEID}\_header_led_status  | Binary Sensor | Breathing Light         | 呼吸灯状态       |
