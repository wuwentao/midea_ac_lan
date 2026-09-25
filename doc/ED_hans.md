# 饮用水设备

## 生成实体

### 默认实体

茶吧机型号 63000622、子型号 395 默认生成以下实体：

| EntityID                                       | 类型          | 描述                                                                         |
| ---------------------------------------------- | ------------- | ---------------------------------------------------------------------------- |
| sensor.{DEVICEID}\_current_temperature         | sensor        | 当前水温                                                                     |
| sensor.{DEVICEID}\_target_temperature          | sensor        | 目标水温                                                                     |
| binary_sensor.{DEVICEID}\_heating              | binary_sensor | 正在烧水                                                                     |
| binary_sensor.{DEVICEID}\_dispensing           | binary_sensor | 正在取水                                                                     |
| switch.{DEVICEID}\_tea_bar                     | switch        | “烧水开关”；打开后由设备自动取水并烧到 100℃，关闭时停止烧水                  |
| climate.{DEVICEID}\_tea_bar_temperature        | climate       | 主“茶吧机”控制；普通开启按官方协议烧到 100℃，明确设温时支持 40–100℃ 整数温度 |
| switch.{DEVICEID}\_tea_bar_child_lock          | switch        | 童锁开关；使用型号 63000622 官方协议，支持“打开/关闭”语义                    |
| switch.{DEVICEID}\_keep_warm                   | switch        | 保温开关；使用型号 63000622 官方保温命令                                     |
| switch.{DEVICEID}\_cooling                     | switch        | 茶吧机制冷；使用型号 63000622 官方信号制冷命令                               |
| switch.{DEVICEID}\_screen_display              | switch        | 屏幕显示；开启时点亮，关闭时发送官方休眠命令                                 |
| number.{DEVICEID}\_keep_warm_time              | number        | 保温时长；1–12 小时，每 0.5 小时一档                                         |
| sensor.{DEVICEID}\_keep_warm_remaining         | sensor        | 剩余保温时间；界面按小时和分钟显示，并保留设备上报的原始分钟属性             |
| binary_sensor.{DEVICEID}\_lack_water           | binary_sensor | 设备报告缺水                                                                 |
| binary_sensor.{DEVICEID}\_standby              | binary_sensor | 设备报告待机状态                                                             |
| binary_sensor.{DEVICEID}\_hot_water_dispensing | binary_sensor | 设备正在输出热水                                                             |
| binary_sensor.{DEVICEID}\_fault                | binary_sensor | 设备报告非零故障码                                                           |
| sensor.{DEVICEID}\_fault_code                  | sensor        | 设备上报的原始故障代码                                                       |

### 额外生成实体

#### 非软水机传感器

| EntityID                             | 类型   | 名称              | 描述                           |
| ------------------------------------ | ------ | ----------------- | ------------------------------ |
| sensor.{DEVICEID}\_water_consumption | sensor | Water Consumption | 总耗水量（非软水机子型号使用） |

#### 软水机实体

下列软水机控制和状态实体仅向子型号 703 提供，不会再向茶吧机子型号 395 提供。

#### 开关

| EntityID                                 | 类型   | 名称                  | 描述     |
| ---------------------------------------- | ------ | --------------------- | -------- |
| switch.{DEVICEID}\_power                 | switch | Power                 | 电源开关 |
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

#### 净水器实体（FF 状态帧）

以下实体来自使用 FF 状态帧上报的净水器。它们均为额外（需手动开启）实体，
仅在上报对应记录的型号上才会有数据。

##### 传感器

| EntityID                               | 类型   | 名称                | 描述                         |
| -------------------------------------- | ------ | ------------------- | ---------------------------- |
| sensor.{DEVICEID}\_filter4_life        | sensor | Filter4 Life Level  | 滤芯4剩余寿命（%）           |
| sensor.{DEVICEID}\_filter5_life        | sensor | Filter5 Life Level  | 滤芯5剩余寿命（%）           |
| sensor.{DEVICEID}\_filter1_maxlife     | sensor | Filter1 Life Limit  | 滤芯1寿命上限（月）          |
| sensor.{DEVICEID}\_filter2_maxlife     | sensor | Filter2 Life Limit  | 滤芯2寿命上限（月）          |
| sensor.{DEVICEID}\_filter3_maxlife     | sensor | Filter3 Life Limit  | 滤芯3寿命上限（月）          |
| sensor.{DEVICEID}\_filter4_maxlife     | sensor | Filter4 Life Limit  | 滤芯4寿命上限（月）          |
| sensor.{DEVICEID}\_filter5_maxlife     | sensor | Filter5 Life Limit  | 滤芯5寿命上限（月）          |
| sensor.{DEVICEID}\_hot_pot_temperature | sensor | Hot Pot Temperature | 热罐/热水温度（°C）          |
| sensor.{DEVICEID}\_ice_gall_status     | sensor | Ice Gall Status     | 制冰仓状态字节（厂商定义）   |
| sensor.{DEVICEID}\_water_kind          | sensor | Water Kind          | 出水类型（枚举：空闲/温/冷） |
| sensor.{DEVICEID}\_heat_start          | sensor | Heat Start          | 加热启动（枚举：加热/保温）  |

##### 二元传感器

| EntityID                                 | 类型          | 名称           | 描述       |
| ---------------------------------------- | ------------- | -------------- | ---------- |
| binary_sensor.{DEVICEID}\_filter_status  | binary_sensor | Filter Alarm   | 滤芯报警   |
| binary_sensor.{DEVICEID}\_standby_status | binary_sensor | Standby Status | 待机状态   |
| binary_sensor.{DEVICEID}\_out_water      | binary_sensor | Out Water      | 正在出水   |
| binary_sensor.{DEVICEID}\_out_hot_water  | binary_sensor | Out Hot Water  | 正在出热水 |
| binary_sensor.{DEVICEID}\_backflow       | binary_sensor | Backflow       | 正在回流   |
| binary_sensor.{DEVICEID}\_sleep_status   | binary_sensor | Sleep Status   | 睡眠状态   |

##### 开关

| EntityID                      | 类型   | 名称        | 描述                         |
| ----------------------------- | ------ | ----------- | ---------------------------- |
| switch.{DEVICEID}\_wash       | switch | Filter Wash | 启动滤芯冲洗（固定 60 秒）。 |
| switch.{DEVICEID}\_antifreeze | switch | Antifreeze  | 切换防冻保护。               |

## 服务

无服务
