# 智能燃气灶

## 功能

- 报告左右炉头状态、档位、工作模式及温度
- 报告每个炉头的剩余时间和工作计时
- 报告燃气报警、智能防干烧及菜谱标记状态
- 报告错误代码和提示代码
- 控制面板锁（开/关）
- 控制左右炉头电源（点火/熄火触发）
- 控制左右炉头档位（0–255）
- 控制左右炉头温度设定（0–65535 °C）

## 自定义

```json
{
  "refresh_interval": 30
}
```

- `refresh_interval`：轮询间隔，单位秒（默认：30）。

## 实体

### 默认实体

| 实体ID                             | 类型          | 描述     |
| ---------------------------------- | ------------- | -------- |
| binary_sensor.{DEVICEID}\_gas_warn | binary_sensor | 燃气报警 |

### 扩展实体

| 实体ID                                   | 类型          | 描述                  |
| ---------------------------------------- | ------------- | --------------------- |
| switch.{DEVICEID}\_lock                  | switch        | 面板锁                |
| switch.{DEVICEID}\_left_power            | switch        | 左侧炉头电源          |
| switch.{DEVICEID}\_right_power           | switch        | 右侧炉头电源          |
| number.{DEVICEID}\_left_gear_set         | number        | 左侧炉头档位（0–255） |
| number.{DEVICEID}\_right_gear_set        | number        | 右侧炉头档位（0–255） |
| number.{DEVICEID}\_left_temp_set         | number        | 左侧炉头温度设定      |
| number.{DEVICEID}\_right_temp_set        | number        | 右侧炉头温度设定      |
| binary_sensor.{DEVICEID}\_left_smart_bl  | binary_sensor | 左侧智能防干烧        |
| binary_sensor.{DEVICEID}\_right_smart_bl | binary_sensor | 右侧智能防干烧        |
| binary_sensor.{DEVICEID}\_menu_mark      | binary_sensor | 菜谱标记              |
| sensor.{DEVICEID}\_left_status           | sensor        | 左侧炉头状态          |
| sensor.{DEVICEID}\_right_status          | sensor        | 右侧炉头状态          |
| sensor.{DEVICEID}\_left_gear             | sensor        | 左侧炉头档位          |
| sensor.{DEVICEID}\_right_gear            | sensor        | 右侧炉头档位          |
| sensor.{DEVICEID}\_left_work_mode        | sensor        | 左侧炉头工作模式      |
| sensor.{DEVICEID}\_right_work_mode       | sensor        | 右侧炉头工作模式      |
| sensor.{DEVICEID}\_left_temp             | sensor        | 左侧炉头温度          |
| sensor.{DEVICEID}\_right_temp            | sensor        | 右侧炉头温度          |
| sensor.{DEVICEID}\_left_surplus_hours    | sensor        | 左侧剩余时间（小时）  |
| sensor.{DEVICEID}\_left_surplus_minutes  | sensor        | 左侧剩余时间（分钟）  |
| sensor.{DEVICEID}\_right_surplus_hours   | sensor        | 右侧剩余时间（小时）  |
| sensor.{DEVICEID}\_right_surplus_minutes | sensor        | 右侧剩余时间（分钟）  |
| sensor.{DEVICEID}\_left_work_hours       | sensor        | 左侧工作时间（小时）  |
| sensor.{DEVICEID}\_left_work_minutes     | sensor        | 左侧工作时间（分钟）  |
| sensor.{DEVICEID}\_left_work_seconds     | sensor        | 左侧工作时间（秒）    |
| sensor.{DEVICEID}\_right_work_hours      | sensor        | 右侧工作时间（小时）  |
| sensor.{DEVICEID}\_right_work_minutes    | sensor        | 右侧工作时间（分钟）  |
| sensor.{DEVICEID}\_right_work_seconds    | sensor        | 右侧工作时间（秒）    |
| sensor.{DEVICEID}\_error_code            | sensor        | 错误代码（诊断）      |
| sensor.{DEVICEID}\_tips_code             | sensor        | 提示代码（诊断）      |

## 服务

无服务
