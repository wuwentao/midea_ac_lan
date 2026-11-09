# 调味机

自动调味机 (设备类型 0x70)。设备上报最多 8 个调料盒记录 (类型与在位状态)。

## 特性

- 上报 8 个调料盒的类型
- 上报 8 个调料盒的在位状态

> 注意: 投放调料和设置调料盒类型通过库的结构化命令 `dispense()` /
> `set_box_types()` 完成。它们未暴露为 Home Assistant 实体, 因为该设备的
> `set_attribute` 为空操作, 且 Home Assistant 没有通用的多槽位结构化命令实体。

## 自定义

无自定义

## 实体

### 默认实体

无默认实体

### 扩展传感器

| 实体ID                         | 类型   | 描述        |
| ------------------------------ | ------ | ----------- |
| sensor.{DEVICEID}\_box1_type   | sensor | 调料盒1类型 |
| sensor.{DEVICEID}\_box1_status | sensor | 调料盒1状态 |
| sensor.{DEVICEID}\_box2_type   | sensor | 调料盒2类型 |
| sensor.{DEVICEID}\_box2_status | sensor | 调料盒2状态 |
| sensor.{DEVICEID}\_box3_type   | sensor | 调料盒3类型 |
| sensor.{DEVICEID}\_box3_status | sensor | 调料盒3状态 |
| sensor.{DEVICEID}\_box4_type   | sensor | 调料盒4类型 |
| sensor.{DEVICEID}\_box4_status | sensor | 调料盒4状态 |
| sensor.{DEVICEID}\_box5_type   | sensor | 调料盒5类型 |
| sensor.{DEVICEID}\_box5_status | sensor | 调料盒5状态 |
| sensor.{DEVICEID}\_box6_type   | sensor | 调料盒6类型 |
| sensor.{DEVICEID}\_box6_status | sensor | 调料盒6状态 |
| sensor.{DEVICEID}\_box7_type   | sensor | 调料盒7类型 |
| sensor.{DEVICEID}\_box7_status | sensor | 调料盒7状态 |
| sensor.{DEVICEID}\_box8_type   | sensor | 调料盒8类型 |
| sensor.{DEVICEID}\_box8_status | sensor | 调料盒8状态 |

## 服务

无服务
