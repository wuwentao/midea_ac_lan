# 扫地机器人

## 支持功能

B8 支持基于 `midea-lan` 中实现的旧版 B8 局域网协议。本文档暂不包含
型号专用的新版 `750004CE` 协议。

- 工作状态和清扫状态
- 电池电量和工作时间
- 清扫面积、拖布状态、地毯检测和移动状态
- 错误类型、错误描述及部分硬件错误标识
- 指令来源状态（电控触发或其他来源）
- 勿扰模式状态及开始/结束时间
- 边刷、滤网和滚刷剩余时间/寿命
- 清扫模式、风机档位、水量档位、语音档位、移动方向和语音音量控制

## 生成实体

### 默认实体

无默认实体。

### 额外实体

| 实体ID                                             | 类型          | 名称                      | 描述             |
| -------------------------------------------------- | ------------- | ------------------------- | ---------------- |
| sensor.{DEVICEID}_work_status                      | sensor        | Work Status               | 工作状态         |
| sensor.{DEVICEID}_function_type                    | sensor        | Function Type             | 功能状态         |
| sensor.{DEVICEID}_control_type                     | sensor        | Control Type              | 控制类型         |
| sensor.{DEVICEID}_area                             | sensor        | Cleaned Area              | 清扫面积         |
| sensor.{DEVICEID}_battery_percent                  | sensor        | Battery                   | 电池电量         |
| sensor.{DEVICEID}_work_time                        | sensor        | Work Time                 | 工作时间（分钟） |
| sensor.{DEVICEID}_mop                              | sensor        | Mop State                 | 拖布状态         |
| sensor.{DEVICEID}_speed                            | sensor        | Speed                     | 速度             |
| sensor.{DEVICEID}_error_type                       | sensor        | Error Type                | 错误类型         |
| sensor.{DEVICEID}_error_desc                       | sensor        | Error Description         | 错误描述         |
| sensor.{DEVICEID}_disturb_start_time               | sensor        | Do Not Disturb Start Time | 勿扰开始时间     |
| sensor.{DEVICEID}_disturb_end_time                 | sensor        | Do Not Disturb End Time   | 勿扰结束时间     |
| sensor.{DEVICEID}_side_brush_rest_time             | sensor        | Side Brush Remaining Time | 边刷剩余时间     |
| sensor.{DEVICEID}_side_brush_life_time             | sensor        | Side Brush Life Time      | 边刷寿命         |
| sensor.{DEVICEID}_filter_net_rest_time             | sensor        | Filter Remaining Time     | 滤网剩余时间     |
| sensor.{DEVICEID}_filter_net_life_time             | sensor        | Filter Life Time          | 滤网寿命         |
| sensor.{DEVICEID}_roll_brush_rest_time             | sensor        | Roll Brush Remaining Time | 滚刷剩余时间     |
| sensor.{DEVICEID}_roll_brush_life_time             | sensor        | Roll Brush Life Time      | 滚刷寿命         |
| binary_sensor.{DEVICEID}_have_reserve_task         | binary_sensor | Reserve Task              | 是否有预约任务   |
| binary_sensor.{DEVICEID}_disturb_switch            | binary_sensor | Do Not Disturb            | 勿扰模式         |
| binary_sensor.{DEVICEID}_device_error              | binary_sensor | Device Error              | 设备错误         |
| binary_sensor.{DEVICEID}_carpet_switch             | binary_sensor | Carpet Detection          | 地毯检测         |
| binary_sensor.{DEVICEID}_uv_switch                 | binary_sensor | UV Light                  | 紫外灯           |
| binary_sensor.{DEVICEID}_wifi_switch               | binary_sensor | Wi-Fi Light               | Wi-Fi 灯         |
| binary_sensor.{DEVICEID}_voice_switch              | binary_sensor | Voice Prompt              | 语音提示         |
| binary_sensor.{DEVICEID}_command_source            | binary_sensor | Command Source            | 指令来源         |
| binary_sensor.{DEVICEID}_board_communication_error | binary_sensor | Board Communication Error | 主板通信错误     |
| binary_sensor.{DEVICEID}_laser_sensor_shelter      | binary_sensor | Laser Sensor Shelter      | 激光传感器遮挡   |
| binary_sensor.{DEVICEID}_laser_sensor_error        | binary_sensor | Laser Sensor Error        | 激光传感器错误   |
| select.{DEVICEID}_clean_mode                       | select        | Clean Mode                | 清扫模式         |
| select.{DEVICEID}_fan_level                        | select        | Fan Level                 | 风机档位         |
| select.{DEVICEID}_water_level                      | select        | Water Level               | 水量档位         |
| select.{DEVICEID}_speak_level                      | select        | Speak Level               | 语音档位         |
| select.{DEVICEID}_move_direction                   | select        | Move Direction            | 移动方向         |
| select.{DEVICEID}_work_status_control              | select        | Work Status Control       | 工作状态控制     |
| number.{DEVICEID}_voice_volume                     | number        | Voice Volume              | 语音音量         |

实体列表可在集成配置中选择。请只启用具体扫地机器人支持的属性。

## 服务

### `midea_ac_lan.set_attribute`

通用服务可以设置以下 B8 控制属性：

| `attribute`           | 示例值                                     |
| --------------------- | ------------------------------------------ |
| `clean_mode`          | `auto`、`area`、`path`                     |
| `fan_level`           | `off`、`soft`、`normal`、`high`、`low`     |
| `water_level`         | `off`、`low`、`normal`、`high`             |
| `speak_level`         | `none`、`off`、`low`、`normal`、`high`     |
| `move_direction`      | `none`、`forward`、`back`、`left`、`right` |
| `work_status_control` | `charge`、`work`、`stop`、`pause`          |
| `voice_volume`        | `0`-`100`                                  |

示例：

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: clean_mode
  value: auto
```
