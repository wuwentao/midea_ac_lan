# 智能燃气灶

## 功能

- 报告左右炉头状态、档位、工作模式及温度
- 报告每个炉头的剩余时间和工作计时
- 报告燃气报警、智能防干烧及菜谱标记状态
- 报告错误代码和提示代码
- 控制面板锁（开/关）
- 触发左右炉头点火（瞬时操作）
- 控制左右炉头档位（0–255）
- 控制左右炉头温度设定（0–65535 °C）

## 自定义

```json
{
  "refresh_interval": 30
}
```

- `refresh_interval`：轮询间隔，单位秒（默认：30）。保存配置表单后，配置选项中的轮询间隔会覆盖此值。

## 实体

### 默认实体

| 实体ID                             | 类型          | 描述     |
| ---------------------------------- | ------------- | -------- |
| binary_sensor.{DEVICEID}\_gas_warn | binary_sensor | 燃气报警 |

### 扩展实体

| 实体ID                                   | 类型          | 描述                  |
| ---------------------------------------- | ------------- | --------------------- |
| switch.{DEVICEID}\_lock                  | switch        | 面板锁                |
| button.{DEVICEID}\_left_power            | button        | 点燃左侧炉头          |
| button.{DEVICEID}\_right_power           | button        | 点燃右侧炉头          |
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

### midea_ac_lan.set_attribute

[![服务](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置可写的设备属性。服务数据：

| 名称      | 描述                                                                                         |
| --------- | -------------------------------------------------------------------------------------------- |
| device_id | 设备的 Appliance code（设备 ID）                                                             |
| attribute | `lock`<br />`left_gear_set`<br />`right_gear_set`<br />`left_temp_set`<br />`right_temp_set` |
| value     | `lock` 使用布尔值；档位使用 0 至 255 的整数；温度使用 0 至 65535 的摄氏度整数                |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: left_gear_set
  value: 5
```
