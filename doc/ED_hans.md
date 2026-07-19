# 饮用水设备

## 生成实体

### 默认实体

无默认实体

### 额外生成实体

#### 开关

| EntityID                                 | 类型   | 名称                  | 描述     |
| ---------------------------------------- | ------ | --------------------- | -------- |
| switch.{DEVICEID}\_power                 | switch | Power                 | 电源开关 |
| lock.{DEVICEID}\_child_lock              | switch | Child Lock            | 童锁     |
| switch.{DEVICEID}\_soften                | switch | Softening             | 软化功能 |
| switch.{DEVICEID}\_cl_sterilization      | switch | CL Sterilization      | 氯杀菌   |
| switch.{DEVICEID}\_leak_water_protection | switch | Leak Water Protection | 漏水保护 |
| switch.{DEVICEID}\_water_way             | switch | Water Way             | 水路     |
| switch.{DEVICEID}\_regeneration          | switch | Regeneration          | 再生     |

#### 二元传感器

| EntityID                               | 类型          | 名称       | 描述     |
| -------------------------------------- | ------------- | ---------- | -------- |
| binary_sensor.{DEVICEID}\_leak_water   | binary_sensor | Leak Water | 漏水报警 |
| binary_sensor.{DEVICEID}\_rsj_stand_by | binary_sensor | Stand By   | 待机     |

#### 数值

| EntityID                                       | 类型   | 名称                        | 描述                     |
| ---------------------------------------------- | ------ | --------------------------- | ------------------------ |
| number.{DEVICEID}\_water_hardness              | number | Water Hardness              | 水硬度（原始值）         |
| number.{DEVICEID}\_flushing_days               | number | Flushing Days               | 再生天数（再生周期，天） |
| number.{DEVICEID}\_leak_water_protection_value | number | Leak Water Protection Value | 漏水保护值（L，步长 50） |

#### 时间

| EntityID                                  | 类型 | 名称                | 描述                                   |
| ----------------------------------------- | ---- | ------------------- | -------------------------------------- |
| time.{DEVICEID}\_timing_regeneration_hour | time | Timing Regeneration | 定时再生时间（计划再生时刻，如 02:30） |

#### 传感器

| EntityID                                     | 类型   | 名称                      | 描述                                                                |
| -------------------------------------------- | ------ | ------------------------- | ------------------------------------------------------------------- |
| sensor.{DEVICEID}\_filter1                   | sensor | Filter1 Available Days    | 滤芯1可用天数                                                       |
| sensor.{DEVICEID}\_filter2                   | sensor | Filter2 Available Days    | 滤芯2可用天数                                                       |
| sensor.{DEVICEID}\_filter3                   | sensor | Filter3 Available Days    | 滤芯3可用天数                                                       |
| sensor.{DEVICEID}\_life1                     | sensor | Filter1 Life Level        | 滤芯1剩余寿命                                                       |
| sensor.{DEVICEID}\_life2                     | sensor | Filter2 Life Level        | 滤芯2剩余寿命                                                       |
| sensor.{DEVICEID}\_life3                     | sensor | Filter3 Life Level        | 滤芯3剩余寿命                                                       |
| sensor.{DEVICEID}\_in_tds                    | sensor | In TDS                    | 进水TDS                                                             |
| sensor.{DEVICEID}\_out_tds                   | sensor | Out TDS                   | 出水TDS                                                             |
| sensor.{DEVICEID}\_water_consumption         | sensor | Water Consumption         | 总耗水量（非软水机 subtype 使用）                                   |
| sensor.{DEVICEID}\_velocity                  | sensor | Velocity                  | 流速                                                                |
| sensor.{DEVICEID}\_soft_available            | sensor | Soft Water Available      | 可用软水（L）                                                       |
| sensor.{DEVICEID}\_left_salt                 | sensor | Left Salt                 | 剩余盐量（%）                                                       |
| sensor.{DEVICEID}\_remaining_days            | sensor | Remaining Days            | 剩余天数（距再生）                                                  |
| sensor.{DEVICEID}\_regeneration_left_seconds | sensor | Regeneration Left Seconds | 再生剩余秒数（0 表示无再生任务）                                    |
| sensor.{DEVICEID}\_use_days                  | sensor | Use Days                  | 使用天数                                                            |
| sensor.{DEVICEID}\_salt_setting              | sensor | Salt Setting              | 总盐量（KG；0 表示固定盐量型号）                                    |
| sensor.{DEVICEID}\_water_consumption_big     | sensor | Water Consumption         | 总耗水量（L，2 位小数，软水机使用）                                 |
| sensor.{DEVICEID}\_water_consumption_average | sensor | Water Consumption Average | 平均耗水量（L）                                                     |
| sensor.{DEVICEID}\_error                     | sensor | Error                     | 故障（枚举：0=无故障，1=E1 找不到工作位，230=E6 盐位传感器故障...） |

## 服务

无服务
