# 智能面板

0x44 面板（ZKP-3INCH01）的屏幕状态和屏幕设置。按键、场景、设备列表命令库里还没有，所以这里没有对应实体。

数值控件接受整数。屏幕命令能写出的最大字节是 254；255 表示这个字段保持不变，不会被写下去。小时是 0–23，分钟是 0–59。

## 生成实体

### 默认实体

| 实体ID                           | 类型   | 名称     |
| -------------------------------- | ------ | -------- |
| sensor.{DEVICEID}\_error_code    | sensor | 错误码   |
| switch.{DEVICEID}\_screen_state  | switch | 屏幕     |
| switch.{DEVICEID}\_voice_control | switch | 语音控制 |
| switch.{DEVICEID}\_sleep_mode    | switch | 睡眠模式 |
| number.{DEVICEID}\_voice_volume  | number | 语音音量 |
| number.{DEVICEID}\_brightness    | number | 亮度     |

### 额外生成实体

| 实体ID                                     | 类型          | 名称           |
| ------------------------------------------ | ------------- | -------------- |
| binary_sensor.{DEVICEID}\_has_token        | binary_sensor | 已有令牌       |
| sensor.{DEVICEID}\_panel_status            | sensor        | 面板状态       |
| switch.{DEVICEID}\_left_button             | switch        | 左键           |
| switch.{DEVICEID}\_middle_button           | switch        | 中键           |
| switch.{DEVICEID}\_right_button            | switch        | 右键           |
| switch.{DEVICEID}\_show_button_name        | switch        | 显示按键名称   |
| switch.{DEVICEID}\_close_screen_bright     | switch        | 关闭时降低亮度 |
| switch.{DEVICEID}\_sleep_mode_switch       | switch        | 睡眠模式开关   |
| switch.{DEVICEID}\_sleep_mode_mute         | switch        | 睡眠模式静音   |
| switch.{DEVICEID}\_left_button_keep        | switch        | 左键保持       |
| switch.{DEVICEID}\_middle_button_keep      | switch        | 中键保持       |
| switch.{DEVICEID}\_right_button_keep       | switch        | 右键保持       |
| number.{DEVICEID}\_auto_off_screen_type    | number        | 自动息屏类型   |
| number.{DEVICEID}\_theme                   | number        | 主题           |
| number.{DEVICEID}\_night_volume            | number        | 夜间音量       |
| number.{DEVICEID}\_sleep_start_hour        | number        | 休眠开始小时   |
| number.{DEVICEID}\_sleep_start_minute      | number        | 休眠开始分钟   |
| number.{DEVICEID}\_sleep_duration_hour     | number        | 休眠时长小时   |
| number.{DEVICEID}\_sleep_duration_minute   | number        | 休眠时长分钟   |
| number.{DEVICEID}\_left_button_work_mode   | number        | 左键工作模式   |
| number.{DEVICEID}\_middle_button_work_mode | number        | 中键工作模式   |
| number.{DEVICEID}\_right_button_work_mode  | number        | 右键工作模式   |

## 服务

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

设置一项屏幕属性。这次调用没有带上的字段保持不变。

| 名称      | 描述                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| device_id | 设备的编号(Device ID)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| attribute | "screen_state"<br />"voice_control"<br />"sleep_mode"<br />"left_button"<br />"middle_button"<br />"right_button"<br />"show_button_name"<br />"close_screen_bright"<br />"sleep_mode_switch"<br />"sleep_mode_mute"<br />"left_button_keep"<br />"middle_button_keep"<br />"right_button_keep"<br />"voice_volume"<br />"brightness"<br />"night_volume"<br />"theme"<br />"auto_off_screen_type"<br />"sleep_start_hour"<br />"sleep_start_minute"<br />"sleep_duration_hour"<br />"sleep_duration_minute"<br />"left_button_work_mode"<br />"middle_button_work_mode"<br />"right_button_work_mode" |
| value     | 开关用 true 或 false；数值用上面范围内的整数                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |

示例

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: voice_volume
  value: 40
```
