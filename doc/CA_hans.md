# 冰箱

## 生成实体

### 默认实体

无默认实体

### 额外生成实体

| EntityID                                             | 类型          | 名称                                | 描述             |
| ---------------------------------------------------- | ------------- | ----------------------------------- | ---------------- |
| binary_sensor.{DEVICEID}\_bar_door                   | binary_sensor | Bar Door                            | 吧台门状态       |
| binary_sensor.{DEVICEID}\_bar_door_overtime          | binary_sensor | Bar Door Overtime                   | 吧台门超时       |
| binary_sensor.{DEVICEID}\_flex_zone_door             | binary_sensor | Flex-zone Door                      | 变温区门状态     |
| binary_sensor.{DEVICEID}\_flex_zone_door_overtime    | binary_sensor | Flex-zone Door Overtime             | 变温区门超时     |
| binary_sensor.{DEVICEID}\_freezer_door               | binary_sensor | Freezer Door                        | 冷冻室门状态     |
| binary_sensor.{DEVICEID}\_freezer_door_overtime      | binary_sensor | Freezer Door Overtime               | 冷冻室门超时     |
| binary_sensor.{DEVICEID}\_refrigerator_door          | binary_sensor | Refrigerator Door                   | 冷藏室门状态     |
| binary_sensor.{DEVICEID}\_refrigerator_door_overtime | binary_sensor | Refrigerator Door Overtime          | 冷藏室门超时     |
| binary_sensor.{DEVICEID}\_microcrystal_fresh         | binary_sensor | Microcrystal Fresh                  | 微晶一周鲜       |
| binary_sensor.{DEVICEID}\_electronic_smell           | binary_sensor | Deodorizing sterilizing             | 净味除菌         |
| sensor.{DEVICEID}\_flex_zone_actual_temp             | sensor        | Flex-zone Actual Temperature        | 变温区实际温度   |
| sensor.{DEVICEID}\_flex_zone_setting_temp            | sensor        | Flex-zone Setting Temperature       | 变温区设置温度   |
| sensor.{DEVICEID}\_freezer_actual_temp               | sensor        | Freezer Actual Temperature          | 冷冻室实际温度   |
| sensor.{DEVICEID}\_freezer_setting_temp              | sensor        | Freezer Setting Temperature         | 冷冻室设置温度   |
| sensor.{DEVICEID}\_energy_consumption                | sensor        | Energy Consumption                  | 能耗             |
| sensor.{DEVICEID}\_refrigerator_actual_temp          | sensor        | Refrigerator Actual Temperature     | 冷藏室实际温度   |
| sensor.{DEVICEID}\_refrigerator_setting_temp         | sensor        | Refrigerator setting Temperature    | 冷藏室设置温度   |
| sensor.{DEVICEID}\_right_flex_zone_actual_temp       | sensor        | Right Flex-zone Actual Temperature  | 右变温区实际温度 |
| sensor.{DEVICEID}\_right_flex_zone_setting_temp      | sensor        | Right Flex-zone Setting Temperature | 右变温区设置温度 |
| sensor.{DEVICEID}\_humidity                          | sensor        | Humidity                            | 湿度             |
| sensor.{DEVICEID}\_variable_mode                     | sensor        | Variable Mode                       | 变温区模式       |

### 310A2111 变温区模式

`midea-lan` 库对型号 `310A2111`、subtype `56` 根据设备上报的
变温区**设置**温度推导 App 模式：6°C 为母婴（`baby`），2°C 为珍品
（`treasure`），0°C 为零度（`zero`）。其他温度、缺失值和非数值均显示未知。
该功能只读，不发送控制命令；其他冰箱型号和 subtype 保留原有模式行为。

在集成的额外传感器选项中启用“变温区模式”。实体 ID 仍为
`sensor.{DEVICEID}_variable_mode`。

HA 只通过翻译文件展示库返回的模式键，不处理型号或温度映射。
推导模式需要包含该映射的库版本；当前固定依赖 `midea-lan==2026.9.2`
尚不包含这次迁移。

## 服务

无服务
