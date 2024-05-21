# 冰箱

## 生成实体

### 默认实体

无默认实体

### 额外生成实体

| EntityID                                            | 类型            | 名称                                  | 描述       |
|-----------------------------------------------------|---------------|-------------------------------------|----------|
| binary_sensor.{DEVICEID}_bar_door                   | binary_sensor | Bar Door                            | 吧台门状态    |
| binary_sensor.{DEVICEID}_bar_door_overtime          | binary_sensor | Bar Door Overtime                   | 吧台门超时    |
| binary_sensor.{DEVICEID}_flex_zone_door             | binary_sensor | Flex-zone Door                      | 变温区门状态   |
| binary_sensor.{DEVICEID}_flex_zone_door_overtime    | binary_sensor | Flex-zone Door Overtime             | 变温区门超时   |
| binary_sensor.{DEVICEID}_freezer_door               | binary_sensor | Freezer Door                        | 冷冻室门状态   |
| binary_sensor.{DEVICEID}_freezer_door_overtime      | binary_sensor | Freezer Door Overtime               | 冷冻室门超时   |
| binary_sensor.{DEVICEID}_refrigerator_door          | binary_sensor | Refrigerator Door                   | 冷藏室门状态   |
| binary_sensor.{DEVICEID}_refrigerator_door_overtime | binary_sensor | Refrigerator Door Overtime          | 冷藏室门超时   |
| sensor.{DEVICEID}_flex_zone_actual_temp             | sensor        | Flex-zone Actual Temperature        | 变温区实际温度  |
| sensor.{DEVICEID}_flex_zone_setting_temp            | sensor        | Flex-zone Setting Temperature       | 变温区设置温度  |
| sensor.{DEVICEID}_freezer_actual_temp               | sensor        | Freezer Actual Temperature          | 冷冻室实际温度  |
| sensor.{DEVICEID}_freezer_setting_temp              | sensor        | Freezer Setting Temperature         | 冷冻室设置温度  |
| sensor.{DEVICEID}_energy_consumption                | sensor        | Energy Consumption                  | 能耗       |
| sensor.{DEVICEID}_refrigerator_actual_temp          | sensor        | Refrigerator Actual Temperature     | 冷藏室实际温度  |
| sensor.{DEVICEID}_refrigerator_setting_temp         | sensor        | Refrigerator setting Temperature    | 冷藏室设置温度  |
| sensor.{DEVICEID}_right_flex_zone_actual_temp       | sensor        | Right Flex-zone Actual Temperature  | 右变温区实际温度 |
| sensor.{DEVICEID}_right_flex_zone_setting_temp      | sensor        | Right Flex-zone Setting Temperature | 右变温区设置温度 |

## 服务

无服务
