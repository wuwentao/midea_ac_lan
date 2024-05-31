# 饮用水设备

## 生成实体

### 默认实体

无默认实体

### 额外生成实体

| EntityID                             | 类型   | 名称                   | 描述          |
| ------------------------------------ | ------ | ---------------------- | ------------- |
| sensor.{DEVICEID}\_filter1           | sensor | Filter1 Available Days | 滤芯1可用天数 |
| sensor.{DEVICEID}\_filter2           | sensor | Filter2 Available Days | 滤芯2可用天数 |
| sensor.{DEVICEID}\_filter3           | sensor | Filter3 Available Days | 滤芯3可用天数 |
| sensor.{DEVICEID}\_life1             | sensor | Filter1 Life Level     | 滤芯1剩余寿命 |
| sensor.{DEVICEID}\_life2             | sensor | Filter2 Life Level     | 滤芯2剩余寿命 |
| sensor.{DEVICEID}\_life3             | sensor | Filter3 Life Level     | 滤芯3剩余寿命 |
| sensor.{DEVICEID}\_in_tds            | sensor | In TDS                 | 进水TDS       |
| sensor.{DEVICEID}\_out_tds           | sensor | Out TDS                | 出水TDS       |
| sensor.{DEVICEID}\_water_consumption | sensor | Water Consumption      | 总耗水量      |
| lock.{DEVICEID}\_child_lock          | switch | 童锁                   |               |
| switch.{DEVICEID}\_power             | switch | Power                  | 电源开关      |

## 服务

无服务
