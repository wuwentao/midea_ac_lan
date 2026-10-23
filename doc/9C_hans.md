# 集成灶

## 实体

### 默认实体

#### 开关

| EntityID                               | 类型   | 名称                | 描述         |
| -------------------------------------- | ------ | ------------------- | ------------ |
| switch.{DEVICEID}\_ai_voice_microphone | switch | AI Voice Microphone | AI语音麦克风 |
| switch.{DEVICEID}\_total_lock          | switch | Child Lock          | 童锁         |
| switch.{DEVICEID}\_total_power         | switch | Power               | 电源         |

#### 数字

| EntityID                           | 类型   | 名称            | 描述       |
| ---------------------------------- | ------ | --------------- | ---------- |
| number.{DEVICEID}\_ai_voice_volume | number | AI Voice Volume | AI语音音量 |

#### 传感器

| EntityID                                    | 类型   | 名称                         | 描述             |
| ------------------------------------------- | ------ | ---------------------------- | ---------------- |
| sensor.{DEVICEID}\_ac_work_status           | sensor | AC Work Status               | 空调工作状态     |
| sensor.{DEVICEID}\_b2_downstair_work_status | sensor | Steam Oven Lower Work Status | 蒸箱下层工作状态 |
| sensor.{DEVICEID}\_b2_upstair_work_status   | sensor | Steam Oven Upper Work Status | 蒸箱上层工作状态 |
| sensor.{DEVICEID}\_b3_downstair_status      | sensor | Steam Cabinet Lower Status   | 蒸柜下层状态     |
| sensor.{DEVICEID}\_b3_upstair_status        | sensor | Steam Cabinet Upper Status   | 蒸柜上层状态     |
| sensor.{DEVICEID}\_b6_gear                  | sensor | Range Hood Gear              | 油烟机档位       |
| sensor.{DEVICEID}\_b6_light                 | sensor | Range Hood Light             | 油烟机照明灯     |
| sensor.{DEVICEID}\_b6_power                 | sensor | Range Hood Power             | 油烟机电源       |
| sensor.{DEVICEID}\_b7_left_status           | sensor | Gas Hob Left Status          | 燃气灶左灶状态   |
| sensor.{DEVICEID}\_b7_right_status          | sensor | Gas Hob Right Status         | 燃气灶右灶状态   |
| sensor.{DEVICEID}\_bf_work_status           | sensor | Oven Work Status             | 烤箱工作状态     |
| sensor.{DEVICEID}\_error_list               | sensor | Error List                   | 错误列表         |
| sensor.{DEVICEID}\_total_error_code         | sensor | Error Code                   | 错误代码         |
| sensor.{DEVICEID}\_total_error_type         | sensor | Error Type                   | 错误类型         |

### 扩展实体

#### 二元传感器

| EntityID                                                    | 类型          | 名称                                  | 描述                   |
| ----------------------------------------------------------- | ------------- | ------------------------------------- | ---------------------- |
| binary_sensor.{DEVICEID}\_ac_air_direction                  | binary_sensor | AC Air Direction                      | 空调风向               |
| binary_sensor.{DEVICEID}\_ac_cooling_fan                    | binary_sensor | AC Cooling Fan                        | 空调冷却风扇           |
| binary_sensor.{DEVICEID}\_ac_draining_pump                  | binary_sensor | AC Draining Pump                      | 空调排水泵             |
| binary_sensor.{DEVICEID}\_ac_low_temperature                | binary_sensor | AC Low Temperature                    | 空调低温               |
| binary_sensor.{DEVICEID}\_ac_over_temperature               | binary_sensor | AC Over Temperature                   | 空调过温               |
| binary_sensor.{DEVICEID}\_ac_swing                          | binary_sensor | AC Swing                              | 空调摆风               |
| binary_sensor.{DEVICEID}\_ac_water_full                     | binary_sensor | AC Water Full                         | 空调水满               |
| binary_sensor.{DEVICEID}\_b2_downstair_clean_tips           | binary_sensor | Steam Oven Lower Clean Tips           | 蒸箱下层清洁提示       |
| binary_sensor.{DEVICEID}\_b2_downstair_door                 | binary_sensor | Steam Oven Lower Door                 | 蒸箱下层门             |
| binary_sensor.{DEVICEID}\_b2_downstair_fresh_water          | binary_sensor | Steam Oven Lower Fresh Water          | 蒸箱下层清水           |
| binary_sensor.{DEVICEID}\_b2_downstair_light                | binary_sensor | Steam Oven Lower Light                | 蒸箱下层照明灯         |
| binary_sensor.{DEVICEID}\_b2_downstair_lock                 | binary_sensor | Steam Oven Lower Lock                 | 蒸箱下层锁定           |
| binary_sensor.{DEVICEID}\_b2_downstair_must_clean_tips      | binary_sensor | Steam Oven Lower Must Clean Tips      | 蒸箱下层必须清洁提示   |
| binary_sensor.{DEVICEID}\_b2_downstair_water_shortage       | binary_sensor | Steam Oven Lower Water Shortage       | 蒸箱下层缺水           |
| binary_sensor.{DEVICEID}\_b2_upstair_clean_tips             | binary_sensor | Steam Oven Upper Clean Tips           | 蒸箱上层清洁提示       |
| binary_sensor.{DEVICEID}\_b2_upstair_door                   | binary_sensor | Steam Oven Upper Door                 | 蒸箱上层门             |
| binary_sensor.{DEVICEID}\_b2_upstair_fresh_water            | binary_sensor | Steam Oven Upper Fresh Water          | 蒸箱上层清水           |
| binary_sensor.{DEVICEID}\_b2_upstair_light                  | binary_sensor | Steam Oven Upper Light                | 蒸箱上层照明灯         |
| binary_sensor.{DEVICEID}\_b2_upstair_lock                   | binary_sensor | Steam Oven Upper Lock                 | 蒸箱上层锁定           |
| binary_sensor.{DEVICEID}\_b2_upstair_must_clean_tips        | binary_sensor | Steam Oven Upper Must Clean Tips      | 蒸箱上层必须清洁提示   |
| binary_sensor.{DEVICEID}\_b2_upstair_water_shortage         | binary_sensor | Steam Oven Upper Water Shortage       | 蒸箱上层缺水           |
| binary_sensor.{DEVICEID}\_b3_downstair_door                 | binary_sensor | Steam Cabinet Lower Door              | 蒸柜下层门             |
| binary_sensor.{DEVICEID}\_b3_downstair_door_lock            | binary_sensor | Steam Cabinet Lower Door Lock         | 蒸柜下层门锁           |
| binary_sensor.{DEVICEID}\_b3_downstair_infrared             | binary_sensor | Steam Cabinet Lower Infrared          | 蒸柜下层红外           |
| binary_sensor.{DEVICEID}\_b3_downstair_ultraviolet          | binary_sensor | Steam Cabinet Lower Ultraviolet       | 蒸柜下层紫外线         |
| binary_sensor.{DEVICEID}\_b3_upstair_door                   | binary_sensor | Steam Cabinet Upper Door              | 蒸柜上层门             |
| binary_sensor.{DEVICEID}\_b3_upstair_door_lock              | binary_sensor | Steam Cabinet Upper Door Lock         | 蒸柜上层门锁           |
| binary_sensor.{DEVICEID}\_b3_upstair_infrared               | binary_sensor | Steam Cabinet Upper Infrared          | 蒸柜上层红外           |
| binary_sensor.{DEVICEID}\_b3_upstair_ultraviolet            | binary_sensor | Steam Cabinet Upper Ultraviolet       | 蒸柜上层紫外线         |
| binary_sensor.{DEVICEID}\_b6_TVOC_status                    | binary_sensor | Range Hood TVOC Status                | 油烟机TVOC状态         |
| binary_sensor.{DEVICEID}\_b6_delay_gear_linkage             | binary_sensor | Range Hood Delay Gear Linkage         | 油烟机延时档位联动     |
| binary_sensor.{DEVICEID}\_b6_delay_time                     | binary_sensor | Range Hood Delay Time                 | 油烟机延时时间         |
| binary_sensor.{DEVICEID}\_b6_gesture_status                 | binary_sensor | Range Hood Gesture Status             | 油烟机手势状态         |
| binary_sensor.{DEVICEID}\_b6_infrared_status                | binary_sensor | Range Hood Infrared Status            | 油烟机红外状态         |
| binary_sensor.{DEVICEID}\_b6_lock                           | binary_sensor | Range Hood Lock                       | 油烟机锁定             |
| binary_sensor.{DEVICEID}\_b6_power_on_light                 | binary_sensor | Range Hood Power On Light             | 油烟机开机照明         |
| binary_sensor.{DEVICEID}\_b6_smoke_detector                 | binary_sensor | Range Hood Smoke Detector             | 油烟机烟雾探测器       |
| binary_sensor.{DEVICEID}\_b6_smoke_stove_linkage            | binary_sensor | Range Hood Smoke Stove Linkage        | 油烟机烟灶联动         |
| binary_sensor.{DEVICEID}\_b7_left_dry_burning               | binary_sensor | Gas Hob Left Dry Burning              | 燃气灶左灶干烧         |
| binary_sensor.{DEVICEID}\_b7_left_dry_burning_invalid       | binary_sensor | Gas Hob Left Dry Burning Invalid      | 燃气灶左灶干烧失效     |
| binary_sensor.{DEVICEID}\_b7_left_gas_leakage               | binary_sensor | Gas Hob Left Gas Leakage              | 燃气灶左灶燃气泄漏     |
| binary_sensor.{DEVICEID}\_b7_left_has_fire                  | binary_sensor | Gas Hob Left Has Fire                 | 燃气灶左灶有火         |
| binary_sensor.{DEVICEID}\_b7_left_has_pot                   | binary_sensor | Gas Hob Left Has Pot                  | 燃气灶左灶有锅         |
| binary_sensor.{DEVICEID}\_b7_right_dry_burning              | binary_sensor | Gas Hob Right Dry Burning             | 燃气灶右灶干烧         |
| binary_sensor.{DEVICEID}\_b7_right_dry_burning_invalid      | binary_sensor | Gas Hob Right Dry Burning Invalid     | 燃气灶右灶干烧失效     |
| binary_sensor.{DEVICEID}\_b7_right_gas_leakage              | binary_sensor | Gas Hob Right Gas Leakage             | 燃气灶右灶燃气泄漏     |
| binary_sensor.{DEVICEID}\_b7_right_has_fire                 | binary_sensor | Gas Hob Right Has Fire                | 燃气灶右灶有火         |
| binary_sensor.{DEVICEID}\_b7_right_has_pot                  | binary_sensor | Gas Hob Right Has Pot                 | 燃气灶右灶有锅         |
| binary_sensor.{DEVICEID}\_bf_door                           | binary_sensor | Oven Door                             | 烤箱门                 |
| binary_sensor.{DEVICEID}\_bf_error                          | binary_sensor | Oven Error                            | 烤箱错误               |
| binary_sensor.{DEVICEID}\_bf_flip                           | binary_sensor | Oven Flip                             | 烤箱翻转               |
| binary_sensor.{DEVICEID}\_bf_hightemp_error                 | binary_sensor | Oven Hightemp Error                   | 烤箱高温错误           |
| binary_sensor.{DEVICEID}\_bf_hightemp_lock                  | binary_sensor | Oven Hightemp Lock                    | 烤箱高温锁定           |
| binary_sensor.{DEVICEID}\_bf_hightemp_over                  | binary_sensor | Oven Hightemp Over                    | 烤箱高温超限           |
| binary_sensor.{DEVICEID}\_bf_hotwind                        | binary_sensor | Oven Hotwind                          | 烤箱热风               |
| binary_sensor.{DEVICEID}\_bf_hotwind_set                    | binary_sensor | Oven Hotwind Set                      | 烤箱热风设置           |
| binary_sensor.{DEVICEID}\_bf_hydrops_full                   | binary_sensor | Oven Hydrops Full                     | 烤箱积水已满           |
| binary_sensor.{DEVICEID}\_bf_light                          | binary_sensor | Oven Light                            | 烤箱照明灯             |
| binary_sensor.{DEVICEID}\_bf_lock                           | binary_sensor | Oven Lock                             | 烤箱锁定               |
| binary_sensor.{DEVICEID}\_bf_off_fromapp                    | binary_sensor | Oven Off Fromapp                      | 烤箱App关闭            |
| binary_sensor.{DEVICEID}\_bf_on_smart                       | binary_sensor | Oven On Smart                         | 烤箱智能开启           |
| binary_sensor.{DEVICEID}\_bf_order                          | binary_sensor | Oven Order                            | 烤箱预约               |
| binary_sensor.{DEVICEID}\_bf_order_time_isabsolute          | binary_sensor | Oven Order Time Isabsolute            | 烤箱预约时间为绝对时间 |
| binary_sensor.{DEVICEID}\_bf_overheat                       | binary_sensor | Oven Overheat                         | 烤箱过热               |
| binary_sensor.{DEVICEID}\_bf_preheat                        | binary_sensor | Oven Preheat                          | 烤箱预热               |
| binary_sensor.{DEVICEID}\_bf_preheat_done                   | binary_sensor | Oven Preheat Done                     | 烤箱预热完成           |
| binary_sensor.{DEVICEID}\_bf_preheat_set                    | binary_sensor | Oven Preheat Set                      | 烤箱预热设置           |
| binary_sensor.{DEVICEID}\_bf_probe                          | binary_sensor | Oven Probe                            | 烤箱探针               |
| binary_sensor.{DEVICEID}\_bf_probe_meat                     | binary_sensor | Oven Probe Meat                       | 烤箱肉类探针           |
| binary_sensor.{DEVICEID}\_bf_radiating                      | binary_sensor | Oven Radiating                        | 烤箱辐射               |
| binary_sensor.{DEVICEID}\_bf_repair_cook                    | binary_sensor | Oven Repair Cook                      | 烤箱修复烹饪           |
| binary_sensor.{DEVICEID}\_bf_sabbath                        | binary_sensor | Oven Sabbath                          | 烤箱安息日模式         |
| binary_sensor.{DEVICEID}\_bf_scalehandling_remind           | binary_sensor | Oven Scalehandling Remind             | 烤箱除垢提醒           |
| binary_sensor.{DEVICEID}\_bf_sensor                         | binary_sensor | Oven Sensor                           | 烤箱传感器             |
| binary_sensor.{DEVICEID}\_bf_stove_1                        | binary_sensor | Oven Stove 1                          | 烤箱灶眼1              |
| binary_sensor.{DEVICEID}\_bf_stove_2                        | binary_sensor | Oven Stove 2                          | 烤箱灶眼2              |
| binary_sensor.{DEVICEID}\_bf_stove_3                        | binary_sensor | Oven Stove 3                          | 烤箱灶眼3              |
| binary_sensor.{DEVICEID}\_bf_stove_4                        | binary_sensor | Oven Stove 4                          | 烤箱灶眼4              |
| binary_sensor.{DEVICEID}\_bf_stove_5                        | binary_sensor | Oven Stove 5                          | 烤箱灶眼5              |
| binary_sensor.{DEVICEID}\_bf_temp_fahrenheit                | binary_sensor | Oven Temp Fahrenheit                  | 烤箱温度华氏度         |
| binary_sensor.{DEVICEID}\_bf_time_synchronization           | binary_sensor | Oven Time Synchronization             | 烤箱时间同步           |
| binary_sensor.{DEVICEID}\_bf_turntable                      | binary_sensor | Oven Turntable                        | 烤箱转盘               |
| binary_sensor.{DEVICEID}\_bf_turntable_reset                | binary_sensor | Oven Turntable Reset                  | 烤箱转盘复位           |
| binary_sensor.{DEVICEID}\_bf_upload_interval                | binary_sensor | Oven Upload Interval                  | 烤箱上传间隔           |
| binary_sensor.{DEVICEID}\_bf_voice_identify                 | binary_sensor | Oven Voice Identify                   | 烤箱语音识别           |
| binary_sensor.{DEVICEID}\_bf_voice_module                   | binary_sensor | Oven Voice Module                     | 烤箱语音模块           |
| binary_sensor.{DEVICEID}\_bf_water_box                      | binary_sensor | Oven Water Box                        | 烤箱水盒               |
| binary_sensor.{DEVICEID}\_bf_water_change                   | binary_sensor | Oven Water Change                     | 烤箱换水               |
| binary_sensor.{DEVICEID}\_bf_water_shortage                 | binary_sensor | Oven Water Shortage                   | 烤箱缺水               |
| binary_sensor.{DEVICEID}\_bf_wintersummertime               | binary_sensor | Oven Wintersummertime                 | 烤箱冬夏令时           |
| binary_sensor.{DEVICEID}\_e7_left_bottom_has_pot            | binary_sensor | Induction Left Bottom Has Pot         | 电磁炉左下有锅         |
| binary_sensor.{DEVICEID}\_e7_left_has_pot                   | binary_sensor | Induction Left Has Pot                | 电磁炉左有锅           |
| binary_sensor.{DEVICEID}\_e7_left_top_has_pot               | binary_sensor | Induction Left Top Has Pot            | 电磁炉左上有锅         |
| binary_sensor.{DEVICEID}\_e7_right_bottom_has_pot           | binary_sensor | Induction Right Bottom Has Pot        | 电磁炉右下有锅         |
| binary_sensor.{DEVICEID}\_e7_right_has_pot                  | binary_sensor | Induction Right Has Pot               | 电磁炉右有锅           |
| binary_sensor.{DEVICEID}\_e7_right_top_has_pot              | binary_sensor | Induction Right Top Has Pot           | 电磁炉右上有锅         |
| binary_sensor.{DEVICEID}\_sp_fandrying_door                 | binary_sensor | Plate Fan Drying Door                 | 碗篮风干门             |
| binary_sensor.{DEVICEID}\_sp_fandrying_setting_automode     | binary_sensor | Plate Fan Drying Setting Automode     | 碗篮风干自动模式设置   |
| binary_sensor.{DEVICEID}\_sp_fandrying_setting_linkage      | binary_sensor | Plate Fan Drying Setting Linkage      | 碗篮风干联动设置       |
| binary_sensor.{DEVICEID}\_sp_fandrying_setting_linkcooker   | binary_sensor | Plate Fan Drying Setting Linkcooker   | 碗篮风干联动灶具设置   |
| binary_sensor.{DEVICEID}\_sp_fandrying_setting_sync         | binary_sensor | Plate Fan Drying Setting Sync         | 碗篮风干同步设置       |
| binary_sensor.{DEVICEID}\_sp_heatingdisk_door               | binary_sensor | Plate Heating Disk Door               | 碗篮加热盘门           |
| binary_sensor.{DEVICEID}\_sp_heatingdisk_setting_automode   | binary_sensor | Plate Heating Disk Setting Automode   | 碗篮加热盘自动模式设置 |
| binary_sensor.{DEVICEID}\_sp_heatingdisk_setting_linkage    | binary_sensor | Plate Heating Disk Setting Linkage    | 碗篮加热盘联动设置     |
| binary_sensor.{DEVICEID}\_sp_heatingdisk_setting_linkcooker | binary_sensor | Plate Heating Disk Setting Linkcooker | 碗篮加热盘联动灶具设置 |
| binary_sensor.{DEVICEID}\_sp_heatingdisk_setting_sync       | binary_sensor | Plate Heating Disk Setting Sync       | 碗篮加热盘同步设置     |
| binary_sensor.{DEVICEID}\_sp_uvc_door                       | binary_sensor | Plate UVC Door                        | 碗篮UVC门              |
| binary_sensor.{DEVICEID}\_sp_uvc_setting_automode           | binary_sensor | Plate UVC Setting Automode            | 碗篮UVC自动模式设置    |
| binary_sensor.{DEVICEID}\_sp_uvc_setting_linkage            | binary_sensor | Plate UVC Setting Linkage             | 碗篮UVC联动设置        |
| binary_sensor.{DEVICEID}\_sp_uvc_setting_linkcooker         | binary_sensor | Plate UVC Setting Linkcooker          | 碗篮UVC联动灶具设置    |
| binary_sensor.{DEVICEID}\_sp_uvc_setting_sync               | binary_sensor | Plate UVC Setting Sync                | 碗篮UVC同步设置        |
| binary_sensor.{DEVICEID}\_total_water_shortage              | binary_sensor | Water Shortage                        | 缺水                   |

#### 传感器

| EntityID                                                       | 类型   | 名称                                            | 描述                           |
| -------------------------------------------------------------- | ------ | ----------------------------------------------- | ------------------------------ |
| sensor.{DEVICEID}\_ac_air_direction_gear                       | sensor | AC Air Direction Gear                           | 空调风向档位                   |
| sensor.{DEVICEID}\_ac_air_direction_max_angle                  | sensor | AC Air Direction Max Angle                      | 空调风向最大角度               |
| sensor.{DEVICEID}\_ac_air_direction_min_angle                  | sensor | AC Air Direction Min Angle                      | 空调风向最小角度               |
| sensor.{DEVICEID}\_ac_ambient_temperature                      | sensor | AC Ambient Temperature                          | 空调环境温度                   |
| sensor.{DEVICEID}\_ac_current_temp                             | sensor | AC Current Temp                                 | 空调当前温度                   |
| sensor.{DEVICEID}\_ac_destination_temp                         | sensor | AC Destination Temp                             | 空调目标温度                   |
| sensor.{DEVICEID}\_ac_destination_time                         | sensor | AC Destination Time                             | 空调目标时间                   |
| sensor.{DEVICEID}\_ac_gear                                     | sensor | AC Gear                                         | 空调档位                       |
| sensor.{DEVICEID}\_ac_mode                                     | sensor | AC Mode                                         | 空调模式                       |
| sensor.{DEVICEID}\_ac_order_destination_time                   | sensor | AC Order Destination Time                       | 空调预约目标时间               |
| sensor.{DEVICEID}\_ac_order_remaining_time                     | sensor | AC Order Remaining Time                         | 空调预约剩余时间               |
| sensor.{DEVICEID}\_ac_remaining_time                           | sensor | AC Remaining Time                               | 空调剩余时间                   |
| sensor.{DEVICEID}\_ac_swing_gear                               | sensor | AC Swing Gear                                   | 空调摆风档位                   |
| sensor.{DEVICEID}\_ac_swing_max_angle                          | sensor | AC Swing Max Angle                              | 空调摆风最大角度               |
| sensor.{DEVICEID}\_ac_swing_min_angle                          | sensor | AC Swing Min Angle                              | 空调摆风最小角度               |
| sensor.{DEVICEID}\_ai_voice_microphone_status                  | sensor | AI Voice Microphone Status                      | AI语音麦克风状态               |
| sensor.{DEVICEID}\_ai_voice_status                             | sensor | AI Voice Status                                 | AI语音状态                     |
| sensor.{DEVICEID}\_ai_voice_volume_status                      | sensor | AI Voice Volume Status                          | AI语音音量状态                 |
| sensor.{DEVICEID}\_b2_downstair_current_temp                   | sensor | Steam Oven Lower Current Temp                   | 蒸箱下层当前温度               |
| sensor.{DEVICEID}\_b2_downstair_destination_temp               | sensor | Steam Oven Lower Destination Temp               | 蒸箱下层目标温度               |
| sensor.{DEVICEID}\_b2_downstair_light_off_type                 | sensor | Steam Oven Lower Light Off Type                 | 蒸箱下层照明灯关闭方式         |
| sensor.{DEVICEID}\_b2_downstair_light_on_type                  | sensor | Steam Oven Lower Light On Type                  | 蒸箱下层照明灯开启方式         |
| sensor.{DEVICEID}\_b2_downstair_order_destination_time         | sensor | Steam Oven Lower Order Destination Time         | 蒸箱下层预约目标时间           |
| sensor.{DEVICEID}\_b2_downstair_order_remaining_time           | sensor | Steam Oven Lower Order Remaining Time           | 蒸箱下层预约剩余时间           |
| sensor.{DEVICEID}\_b2_downstair_power_off_type                 | sensor | Steam Oven Lower Power Off Type                 | 蒸箱下层电源关闭方式           |
| sensor.{DEVICEID}\_b2_downstair_power_on_type                  | sensor | Steam Oven Lower Power On Type                  | 蒸箱下层电源开启方式           |
| sensor.{DEVICEID}\_b2_downstair_preheating                     | sensor | Steam Oven Lower Preheating                     | 蒸箱下层预热                   |
| sensor.{DEVICEID}\_b2_downstair_recipe_after                   | sensor | Steam Oven Lower Recipe After                   | 蒸箱下层菜谱完成后             |
| sensor.{DEVICEID}\_b2_downstair_recipe_code                    | sensor | Steam Oven Lower Recipe Code                    | 蒸箱下层菜谱代码               |
| sensor.{DEVICEID}\_b2_downstair_recipe_current_mode            | sensor | Steam Oven Lower Recipe Current Mode            | 蒸箱下层菜谱当前模式           |
| sensor.{DEVICEID}\_b2_downstair_recipe_current_step            | sensor | Steam Oven Lower Recipe Current Step            | 蒸箱下层菜谱当前步骤           |
| sensor.{DEVICEID}\_b2_downstair_recipe_off_type                | sensor | Steam Oven Lower Recipe Off Type                | 蒸箱下层菜谱关闭方式           |
| sensor.{DEVICEID}\_b2_downstair_recipe_on_type                 | sensor | Steam Oven Lower Recipe On Type                 | 蒸箱下层菜谱开启方式           |
| sensor.{DEVICEID}\_b2_downstair_recipe_total_steps             | sensor | Steam Oven Lower Recipe Total Steps             | 蒸箱下层菜谱总步骤             |
| sensor.{DEVICEID}\_b2_downstair_work_destination_time          | sensor | Steam Oven Lower Work Destination Time          | 蒸箱下层工作目标时间           |
| sensor.{DEVICEID}\_b2_downstair_work_func                      | sensor | Steam Oven Lower Work Func                      | 蒸箱下层工作功能               |
| sensor.{DEVICEID}\_b2_downstair_work_menu                      | sensor | Steam Oven Lower Work Menu                      | 蒸箱下层工作菜单               |
| sensor.{DEVICEID}\_b2_downstair_work_remaining_time            | sensor | Steam Oven Lower Work Remaining Time            | 蒸箱下层工作剩余时间           |
| sensor.{DEVICEID}\_b2_upstair_current_temp                     | sensor | Steam Oven Upper Current Temp                   | 蒸箱上层当前温度               |
| sensor.{DEVICEID}\_b2_upstair_destination_temp                 | sensor | Steam Oven Upper Destination Temp               | 蒸箱上层目标温度               |
| sensor.{DEVICEID}\_b2_upstair_light_off_type                   | sensor | Steam Oven Upper Light Off Type                 | 蒸箱上层照明灯关闭方式         |
| sensor.{DEVICEID}\_b2_upstair_light_on_type                    | sensor | Steam Oven Upper Light On Type                  | 蒸箱上层照明灯开启方式         |
| sensor.{DEVICEID}\_b2_upstair_order_destination_time           | sensor | Steam Oven Upper Order Destination Time         | 蒸箱上层预约目标时间           |
| sensor.{DEVICEID}\_b2_upstair_order_remaining_time             | sensor | Steam Oven Upper Order Remaining Time           | 蒸箱上层预约剩余时间           |
| sensor.{DEVICEID}\_b2_upstair_power_off_type                   | sensor | Steam Oven Upper Power Off Type                 | 蒸箱上层电源关闭方式           |
| sensor.{DEVICEID}\_b2_upstair_power_on_type                    | sensor | Steam Oven Upper Power On Type                  | 蒸箱上层电源开启方式           |
| sensor.{DEVICEID}\_b2_upstair_preheating                       | sensor | Steam Oven Upper Preheating                     | 蒸箱上层预热                   |
| sensor.{DEVICEID}\_b2_upstair_recipe_after                     | sensor | Steam Oven Upper Recipe After                   | 蒸箱上层菜谱完成后             |
| sensor.{DEVICEID}\_b2_upstair_recipe_code                      | sensor | Steam Oven Upper Recipe Code                    | 蒸箱上层菜谱代码               |
| sensor.{DEVICEID}\_b2_upstair_recipe_current_mode              | sensor | Steam Oven Upper Recipe Current Mode            | 蒸箱上层菜谱当前模式           |
| sensor.{DEVICEID}\_b2_upstair_recipe_current_step              | sensor | Steam Oven Upper Recipe Current Step            | 蒸箱上层菜谱当前步骤           |
| sensor.{DEVICEID}\_b2_upstair_recipe_off_type                  | sensor | Steam Oven Upper Recipe Off Type                | 蒸箱上层菜谱关闭方式           |
| sensor.{DEVICEID}\_b2_upstair_recipe_on_type                   | sensor | Steam Oven Upper Recipe On Type                 | 蒸箱上层菜谱开启方式           |
| sensor.{DEVICEID}\_b2_upstair_recipe_total_steps               | sensor | Steam Oven Upper Recipe Total Steps             | 蒸箱上层菜谱总步骤             |
| sensor.{DEVICEID}\_b2_upstair_work_destination_time            | sensor | Steam Oven Upper Work Destination Time          | 蒸箱上层工作目标时间           |
| sensor.{DEVICEID}\_b2_upstair_work_func                        | sensor | Steam Oven Upper Work Func                      | 蒸箱上层工作功能               |
| sensor.{DEVICEID}\_b2_upstair_work_menu                        | sensor | Steam Oven Upper Work Menu                      | 蒸箱上层工作菜单               |
| sensor.{DEVICEID}\_b2_upstair_work_remaining_time              | sensor | Steam Oven Upper Work Remaining Time            | 蒸箱上层工作剩余时间           |
| sensor.{DEVICEID}\_b3_disinfect_off_type                       | sensor | Steam Cabinet Disinfect Off Type                | 蒸柜消毒关闭方式               |
| sensor.{DEVICEID}\_b3_disinfect_on_type                        | sensor | Steam Cabinet Disinfect On Type                 | 蒸柜消毒开启方式               |
| sensor.{DEVICEID}\_b3_downstair_current_temp                   | sensor | Steam Cabinet Lower Current Temp                | 蒸柜下层当前温度               |
| sensor.{DEVICEID}\_b3_downstair_destination_temp               | sensor | Steam Cabinet Lower Destination Temp            | 蒸柜下层目标温度               |
| sensor.{DEVICEID}\_b3_downstair_destination_time               | sensor | Steam Cabinet Lower Destination Time            | 蒸柜下层目标时间               |
| sensor.{DEVICEID}\_b3_downstair_remaining_time                 | sensor | Steam Cabinet Lower Remaining Time              | 蒸柜下层剩余时间               |
| sensor.{DEVICEID}\_b3_downstair_sensor                         | sensor | Steam Cabinet Lower Sensor                      | 蒸柜下层传感器                 |
| sensor.{DEVICEID}\_b3_thermotank_off_type                      | sensor | Steam Cabinet Thermotank Off Type               | 蒸柜保温箱关闭方式             |
| sensor.{DEVICEID}\_b3_thermotank_on_type                       | sensor | Steam Cabinet Thermotank On Type                | 蒸柜保温箱开启方式             |
| sensor.{DEVICEID}\_b3_upstair_current_temp                     | sensor | Steam Cabinet Upper Current Temp                | 蒸柜上层当前温度               |
| sensor.{DEVICEID}\_b3_upstair_destination_temp                 | sensor | Steam Cabinet Upper Destination Temp            | 蒸柜上层目标温度               |
| sensor.{DEVICEID}\_b3_upstair_destination_time                 | sensor | Steam Cabinet Upper Destination Time            | 蒸柜上层目标时间               |
| sensor.{DEVICEID}\_b3_upstair_remaining_time                   | sensor | Steam Cabinet Upper Remaining Time              | 蒸柜上层剩余时间               |
| sensor.{DEVICEID}\_b3_upstair_sensor                           | sensor | Steam Cabinet Upper Sensor                      | 蒸柜上层传感器                 |
| sensor.{DEVICEID}\_b6_TVOC_value                               | sensor | Range Hood TVOC Value                           | 油烟机TVOC值                   |
| sensor.{DEVICEID}\_b6_air_duct_detection_score                 | sensor | Range Hood Air Duct Detection Score             | 油烟机风道检测评分             |
| sensor.{DEVICEID}\_b6_air_duct_detection_state                 | sensor | Range Hood Air Duct Detection State             | 油烟机风道检测状态             |
| sensor.{DEVICEID}\_b6_air_duct_detection_time                  | sensor | Range Hood Air Duct Detection Time              | 油烟机风道检测时间             |
| sensor.{DEVICEID}\_b6_air_duct_detection_windage               | sensor | Range Hood Air Duct Detection Windage           | 油烟机风道检测风阻             |
| sensor.{DEVICEID}\_b6_air_volume                               | sensor | Range Hood Air Volume                           | 油烟机风量                     |
| sensor.{DEVICEID}\_b6_delay_gear_linkage_gear                  | sensor | Range Hood Delay Gear Linkage Gear              | 油烟机延时档位联动档位         |
| sensor.{DEVICEID}\_b6_delay_time_value                         | sensor | Range Hood Delay Time Value                     | 油烟机延时时间值               |
| sensor.{DEVICEID}\_b6_destination_time                         | sensor | Range Hood Destination Time                     | 油烟机目标时间                 |
| sensor.{DEVICEID}\_b6_gear_control_type                        | sensor | Range Hood Gear Control Type                    | 油烟机档位控制类型             |
| sensor.{DEVICEID}\_b6_gesture_sensitivity                      | sensor | Range Hood Gesture Sensitivity                  | 油烟机手势灵敏度               |
| sensor.{DEVICEID}\_b6_gesture_value                            | sensor | Range Hood Gesture Value                        | 油烟机手势值                   |
| sensor.{DEVICEID}\_b6_hotclean_tips                            | sensor | Range Hood Hotclean Tips                        | 油烟机热清洗提示               |
| sensor.{DEVICEID}\_b6_infrared_value                           | sensor | Range Hood Infrared Value                       | 油烟机红外值                   |
| sensor.{DEVICEID}\_b6_inverter_ac_frequency                    | sensor | Range Hood Inverter AC Frequency                | 油烟机变频交流频率             |
| sensor.{DEVICEID}\_b6_inverter_back_electromotive_force        | sensor | Range Hood Inverter Back Electromotive Force    | 油烟机变频反电动势             |
| sensor.{DEVICEID}\_b6_inverter_capacity                        | sensor | Range Hood Inverter Capacity                    | 油烟机变频容量                 |
| sensor.{DEVICEID}\_b6_inverter_efficiency                      | sensor | Range Hood Inverter Efficiency                  | 油烟机变频效率                 |
| sensor.{DEVICEID}\_b6_inverter_motor_compensation_angle        | sensor | Range Hood Inverter Motor Compensation Angle    | 油烟机变频电机补偿角度         |
| sensor.{DEVICEID}\_b6_inverter_motor_speed                     | sensor | Range Hood Inverter Motor Speed                 | 油烟机变频电机转速             |
| sensor.{DEVICEID}\_b6_inverter_q_axis_current                  | sensor | Range Hood Inverter Q Axis Current              | 油烟机变频Q轴电流              |
| sensor.{DEVICEID}\_b6_inverter_start_time                      | sensor | Range Hood Inverter Start Time                  | 油烟机变频启动时间             |
| sensor.{DEVICEID}\_b6_inverter_temperature                     | sensor | Range Hood Inverter Temperature                 | 油烟机变频温度                 |
| sensor.{DEVICEID}\_b6_inverter_temperature_limit_sign          | sensor | Range Hood Inverter Temperature Limit Sign      | 油烟机变频温度限制标志         |
| sensor.{DEVICEID}\_b6_inverter_voltage                         | sensor | Range Hood Inverter Voltage                     | 油烟机变频电压                 |
| sensor.{DEVICEID}\_b6_inverter_wind_flow                       | sensor | Range Hood Inverter Wind Flow                   | 油烟机变频风量                 |
| sensor.{DEVICEID}\_b6_inverter_wind_presssure                  | sensor | Range Hood Inverter Wind Pressure               | 油烟机变频风压                 |
| sensor.{DEVICEID}\_b6_inverter_windage                         | sensor | Range Hood Inverter Windage                     | 油烟机变频风阻                 |
| sensor.{DEVICEID}\_b6_inverter_work_gear                       | sensor | Range Hood Inverter Work Gear                   | 油烟机变频工作档位             |
| sensor.{DEVICEID}\_b6_last_hotclean_hour                       | sensor | Range Hood Last Hotclean Hour                   | 油烟机上次热清洗时长           |
| sensor.{DEVICEID}\_b6_light_off_type                           | sensor | Range Hood Light Off Type                       | 油烟机照明灯关闭方式           |
| sensor.{DEVICEID}\_b6_light_on_type                            | sensor | Range Hood Light On Type                        | 油烟机照明灯开启方式           |
| sensor.{DEVICEID}\_b6_lightness                                | sensor | Range Hood Lightness                            | 油烟机亮度                     |
| sensor.{DEVICEID}\_b6_lock_off_type                            | sensor | Range Hood Lock Off Type                        | 油烟机锁定关闭方式             |
| sensor.{DEVICEID}\_b6_lock_on_type                             | sensor | Range Hood Lock On Type                         | 油烟机锁定开启方式             |
| sensor.{DEVICEID}\_b6_power_off_type                           | sensor | Range Hood Power Off Type                       | 油烟机电源关闭方式             |
| sensor.{DEVICEID}\_b6_power_on_type                            | sensor | Range Hood Power On Type                        | 油烟机电源开启方式             |
| sensor.{DEVICEID}\_b6_remaining_time                           | sensor | Range Hood Remaining Time                       | 油烟机剩余时间                 |
| sensor.{DEVICEID}\_b6_smoke_detector_value                     | sensor | Range Hood Smoke Detector Value                 | 油烟机烟雾探测器值             |
| sensor.{DEVICEID}\_b6_smoke_potency                            | sensor | Range Hood Smoke Potency                        | 油烟机烟雾浓度                 |
| sensor.{DEVICEID}\_b6_smoke_stove_linkage_flowin               | sensor | Range Hood Smoke Stove Linkage Flow In          | 油烟机烟灶联动进风             |
| sensor.{DEVICEID}\_b6_smoke_stove_linkage_gear                 | sensor | Range Hood Smoke Stove Linkage Gear             | 油烟机烟灶联动档位             |
| sensor.{DEVICEID}\_b6_smoke_stove_linkage_gear_fix             | sensor | Range Hood Smoke Stove Linkage Gear Fix         | 油烟机烟灶联动档位固定         |
| sensor.{DEVICEID}\_b6_steaming                                 | sensor | Range Hood Steaming                             | 油烟机蒸汽                     |
| sensor.{DEVICEID}\_b6_steaming_stage                           | sensor | Range Hood Steaming Stage                       | 油烟机蒸汽阶段                 |
| sensor.{DEVICEID}\_b6_wind_pressure                            | sensor | Range Hood Wind Pressure                        | 油烟机风压                     |
| sensor.{DEVICEID}\_b6_work_status                              | sensor | Range Hood Work Status                          | 油烟机工作状态                 |
| sensor.{DEVICEID}\_b7_left_current_temp                        | sensor | Gas Hob Left Current Temp                       | 燃气灶左灶当前温度             |
| sensor.{DEVICEID}\_b7_left_destination_temp                    | sensor | Gas Hob Left Destination Temp                   | 燃气灶左灶目标温度             |
| sensor.{DEVICEID}\_b7_left_destination_time                    | sensor | Gas Hob Left Destination Time                   | 燃气灶左灶目标时间             |
| sensor.{DEVICEID}\_b7_left_gear                                | sensor | Gas Hob Left Gear                               | 燃气灶左灶档位                 |
| sensor.{DEVICEID}\_b7_left_power_off_type                      | sensor | Gas Hob Left Power Off Type                     | 燃气灶左灶熄火方式             |
| sensor.{DEVICEID}\_b7_left_remaining_time                      | sensor | Gas Hob Left Remaining Time                     | 燃气灶左灶剩余时间             |
| sensor.{DEVICEID}\_b7_left_work_time                           | sensor | Gas Hob Left Work Time                          | 燃气灶左灶工作时间             |
| sensor.{DEVICEID}\_b7_right_current_temp                       | sensor | Gas Hob Right Current Temp                      | 燃气灶右灶当前温度             |
| sensor.{DEVICEID}\_b7_right_destination_temp                   | sensor | Gas Hob Right Destination Temp                  | 燃气灶右灶目标温度             |
| sensor.{DEVICEID}\_b7_right_destination_time                   | sensor | Gas Hob Right Destination Time                  | 燃气灶右灶目标时间             |
| sensor.{DEVICEID}\_b7_right_gear                               | sensor | Gas Hob Right Gear                              | 燃气灶右灶档位                 |
| sensor.{DEVICEID}\_b7_right_power_off_type                     | sensor | Gas Hob Right Power Off Type                    | 燃气灶右灶熄火方式             |
| sensor.{DEVICEID}\_b7_right_remaining_time                     | sensor | Gas Hob Right Remaining Time                    | 燃气灶右灶剩余时间             |
| sensor.{DEVICEID}\_b7_right_work_time                          | sensor | Gas Hob Right Work Time                         | 燃气灶右灶工作时间             |
| sensor.{DEVICEID}\_bf_cavity                                   | sensor | Oven Cavity                                     | 烤箱腔体                       |
| sensor.{DEVICEID}\_bf_control_back                             | sensor | Oven Control Back                               | 烤箱控制返回                   |
| sensor.{DEVICEID}\_bf_end_next                                 | sensor | Oven End Next                                   | 烤箱结束下一步                 |
| sensor.{DEVICEID}\_bf_fire                                     | sensor | Oven Fire                                       | 烤箱火力                       |
| sensor.{DEVICEID}\_bf_mode                                     | sensor | Oven Mode                                       | 烤箱模式                       |
| sensor.{DEVICEID}\_bf_quick_btn_bake_id                        | sensor | Oven Quick Btn Bake Id                          | 烤箱快捷键烘焙ID               |
| sensor.{DEVICEID}\_bf_quick_btn_bake_set                       | sensor | Oven Quick Btn Bake Set                         | 烤箱快捷键烘焙设置             |
| sensor.{DEVICEID}\_bf_quick_btn_bake_time                      | sensor | Oven Quick Btn Bake Time                        | 烤箱快捷键烘焙时间             |
| sensor.{DEVICEID}\_bf_quick_btn_microwave_id                   | sensor | Oven Quick Btn Microwave Id                     | 烤箱快捷键微波ID               |
| sensor.{DEVICEID}\_bf_quick_btn_microwave_set                  | sensor | Oven Quick Btn Microwave Set                    | 烤箱快捷键微波设置             |
| sensor.{DEVICEID}\_bf_quick_btn_microwave_time                 | sensor | Oven Quick Btn Microwave Time                   | 烤箱快捷键微波时间             |
| sensor.{DEVICEID}\_bf_quick_btn_steam_id                       | sensor | Oven Quick Btn Steam Id                         | 烤箱快捷键蒸制ID               |
| sensor.{DEVICEID}\_bf_quick_btn_steam_set                      | sensor | Oven Quick Btn Steam Set                        | 烤箱快捷键蒸制设置             |
| sensor.{DEVICEID}\_bf_quick_btn_steam_time                     | sensor | Oven Quick Btn Steam Time                       | 烤箱快捷键蒸制时间             |
| sensor.{DEVICEID}\_bf_recipe_code                              | sensor | Oven Recipe Code                                | 烤箱菜谱代码                   |
| sensor.{DEVICEID}\_bf_remaining_time                           | sensor | Oven Remaining Time                             | 烤箱剩余时间                   |
| sensor.{DEVICEID}\_bf_steam                                    | sensor | Oven Steam                                      | 烤箱蒸制                       |
| sensor.{DEVICEID}\_bf_step_current                             | sensor | Oven Step Current                               | 烤箱当前步骤                   |
| sensor.{DEVICEID}\_bf_step_total                               | sensor | Oven Step Total                                 | 烤箱总步骤                     |
| sensor.{DEVICEID}\_bf_temp_down                                | sensor | Oven Temp Down                                  | 烤箱下火                       |
| sensor.{DEVICEID}\_bf_temp_down_set                            | sensor | Oven Temp Down Set                              | 烤箱下火设置                   |
| sensor.{DEVICEID}\_bf_temp_probe                               | sensor | Oven Temp Probe                                 | 烤箱温度探针                   |
| sensor.{DEVICEID}\_bf_temp_probe_set                           | sensor | Oven Temp Probe Set                             | 烤箱温度探针设置               |
| sensor.{DEVICEID}\_bf_temp_up                                  | sensor | Oven Temp Up                                    | 烤箱上火                       |
| sensor.{DEVICEID}\_bf_temp_up_set                              | sensor | Oven Temp Up Set                                | 烤箱上火设置                   |
| sensor.{DEVICEID}\_bf_tips_mark                                | sensor | Oven Tips Mark                                  | 烤箱提示标记                   |
| sensor.{DEVICEID}\_bf_weight_mount                             | sensor | Oven Weight Mount                               | 烤箱称重安装                   |
| sensor.{DEVICEID}\_bf_weight_multiple                          | sensor | Oven Weight Multiple                            | 烤箱称重倍数                   |
| sensor.{DEVICEID}\_bf_weight_unit                              | sensor | Oven Weight Unit                                | 烤箱称重单位                   |
| sensor.{DEVICEID}\_bf_working_time                             | sensor | Oven Working Time                               | 烤箱工作时间                   |
| sensor.{DEVICEID}\_e7_left_bottom_bridge_link                  | sensor | Induction Left Bottom Bridge Link               | 电磁炉左下桥接联动             |
| sensor.{DEVICEID}\_e7_left_bottom_destination_time             | sensor | Induction Left Bottom Destination Time          | 电磁炉左下目标时间             |
| sensor.{DEVICEID}\_e7_left_bottom_efficiency                   | sensor | Induction Left Bottom Efficiency                | 电磁炉左下效率                 |
| sensor.{DEVICEID}\_e7_left_bottom_gear                         | sensor | Induction Left Bottom Gear                      | 电磁炉左下档位                 |
| sensor.{DEVICEID}\_e7_left_bottom_mode                         | sensor | Induction Left Bottom Mode                      | 电磁炉左下模式                 |
| sensor.{DEVICEID}\_e7_left_bottom_remaining_time               | sensor | Induction Left Bottom Remaining Time            | 电磁炉左下剩余时间             |
| sensor.{DEVICEID}\_e7_left_bottom_work_status                  | sensor | Induction Left Bottom Work Status               | 电磁炉左下工作状态             |
| sensor.{DEVICEID}\_e7_left_bottom_work_time                    | sensor | Induction Left Bottom Work Time                 | 电磁炉左下工作时间             |
| sensor.{DEVICEID}\_e7_left_bridge_link                         | sensor | Induction Left Bridge Link                      | 电磁炉左桥接联动               |
| sensor.{DEVICEID}\_e7_left_destination_time                    | sensor | Induction Left Destination Time                 | 电磁炉左目标时间               |
| sensor.{DEVICEID}\_e7_left_efficiency                          | sensor | Induction Left Efficiency                       | 电磁炉左效率                   |
| sensor.{DEVICEID}\_e7_left_gear                                | sensor | Induction Left Gear                             | 电磁炉左档位                   |
| sensor.{DEVICEID}\_e7_left_mode                                | sensor | Induction Left Mode                             | 电磁炉左模式                   |
| sensor.{DEVICEID}\_e7_left_remaining_time                      | sensor | Induction Left Remaining Time                   | 电磁炉左剩余时间               |
| sensor.{DEVICEID}\_e7_left_top_bridge_link                     | sensor | Induction Left Top Bridge Link                  | 电磁炉左上桥接联动             |
| sensor.{DEVICEID}\_e7_left_top_destination_time                | sensor | Induction Left Top Destination Time             | 电磁炉左上目标时间             |
| sensor.{DEVICEID}\_e7_left_top_efficiency                      | sensor | Induction Left Top Efficiency                   | 电磁炉左上效率                 |
| sensor.{DEVICEID}\_e7_left_top_gear                            | sensor | Induction Left Top Gear                         | 电磁炉左上档位                 |
| sensor.{DEVICEID}\_e7_left_top_mode                            | sensor | Induction Left Top Mode                         | 电磁炉左上模式                 |
| sensor.{DEVICEID}\_e7_left_top_remaining_time                  | sensor | Induction Left Top Remaining Time               | 电磁炉左上剩余时间             |
| sensor.{DEVICEID}\_e7_left_top_work_status                     | sensor | Induction Left Top Work Status                  | 电磁炉左上工作状态             |
| sensor.{DEVICEID}\_e7_left_top_work_time                       | sensor | Induction Left Top Work Time                    | 电磁炉左上工作时间             |
| sensor.{DEVICEID}\_e7_left_work_status                         | sensor | Induction Left Work Status                      | 电磁炉左工作状态               |
| sensor.{DEVICEID}\_e7_left_work_time                           | sensor | Induction Left Work Time                        | 电磁炉左工作时间               |
| sensor.{DEVICEID}\_e7_right_bottom_bridge_link                 | sensor | Induction Right Bottom Bridge Link              | 电磁炉右下桥接联动             |
| sensor.{DEVICEID}\_e7_right_bottom_destination_time            | sensor | Induction Right Bottom Destination Time         | 电磁炉右下目标时间             |
| sensor.{DEVICEID}\_e7_right_bottom_efficiency                  | sensor | Induction Right Bottom Efficiency               | 电磁炉右下效率                 |
| sensor.{DEVICEID}\_e7_right_bottom_gear                        | sensor | Induction Right Bottom Gear                     | 电磁炉右下档位                 |
| sensor.{DEVICEID}\_e7_right_bottom_mode                        | sensor | Induction Right Bottom Mode                     | 电磁炉右下模式                 |
| sensor.{DEVICEID}\_e7_right_bottom_remaining_time              | sensor | Induction Right Bottom Remaining Time           | 电磁炉右下剩余时间             |
| sensor.{DEVICEID}\_e7_right_bottom_work_status                 | sensor | Induction Right Bottom Work Status              | 电磁炉右下工作状态             |
| sensor.{DEVICEID}\_e7_right_bottom_work_time                   | sensor | Induction Right Bottom Work Time                | 电磁炉右下工作时间             |
| sensor.{DEVICEID}\_e7_right_bridge_link                        | sensor | Induction Right Bridge Link                     | 电磁炉右桥接联动               |
| sensor.{DEVICEID}\_e7_right_destination_time                   | sensor | Induction Right Destination Time                | 电磁炉右目标时间               |
| sensor.{DEVICEID}\_e7_right_efficiency                         | sensor | Induction Right Efficiency                      | 电磁炉右效率                   |
| sensor.{DEVICEID}\_e7_right_gear                               | sensor | Induction Right Gear                            | 电磁炉右档位                   |
| sensor.{DEVICEID}\_e7_right_mode                               | sensor | Induction Right Mode                            | 电磁炉右模式                   |
| sensor.{DEVICEID}\_e7_right_remaining_time                     | sensor | Induction Right Remaining Time                  | 电磁炉右剩余时间               |
| sensor.{DEVICEID}\_e7_right_top_bridge_link                    | sensor | Induction Right Top Bridge Link                 | 电磁炉右上桥接联动             |
| sensor.{DEVICEID}\_e7_right_top_destination_time               | sensor | Induction Right Top Destination Time            | 电磁炉右上目标时间             |
| sensor.{DEVICEID}\_e7_right_top_efficiency                     | sensor | Induction Right Top Efficiency                  | 电磁炉右上效率                 |
| sensor.{DEVICEID}\_e7_right_top_gear                           | sensor | Induction Right Top Gear                        | 电磁炉右上档位                 |
| sensor.{DEVICEID}\_e7_right_top_mode                           | sensor | Induction Right Top Mode                        | 电磁炉右上模式                 |
| sensor.{DEVICEID}\_e7_right_top_remaining_time                 | sensor | Induction Right Top Remaining Time              | 电磁炉右上剩余时间             |
| sensor.{DEVICEID}\_e7_right_top_work_status                    | sensor | Induction Right Top Work Status                 | 电磁炉右上工作状态             |
| sensor.{DEVICEID}\_e7_right_top_work_time                      | sensor | Induction Right Top Work Time                   | 电磁炉右上工作时间             |
| sensor.{DEVICEID}\_e7_right_work_status                        | sensor | Induction Right Work Status                     | 电磁炉右工作状态               |
| sensor.{DEVICEID}\_e7_right_work_time                          | sensor | Induction Right Work Time                       | 电磁炉右工作时间               |
| sensor.{DEVICEID}\_electronic_version                          | sensor | Electronic Version                              | 电子版本                       |
| sensor.{DEVICEID}\_sp_fandrying_destination_time               | sensor | Plate Fan Drying Destination Time               | 碗篮风干目标时间               |
| sensor.{DEVICEID}\_sp_fandrying_order_destination_time         | sensor | Plate Fan Drying Order Destination Time         | 碗篮风干预约目标时间           |
| sensor.{DEVICEID}\_sp_fandrying_order_remaining_time           | sensor | Plate Fan Drying Order Remaining Time           | 碗篮风干预约剩余时间           |
| sensor.{DEVICEID}\_sp_fandrying_remaining_time                 | sensor | Plate Fan Drying Remaining Time                 | 碗篮风干剩余时间               |
| sensor.{DEVICEID}\_sp_fandrying_setting_automode_day           | sensor | Plate Fan Drying Setting Automode Day           | 碗篮风干自动模式日期设置       |
| sensor.{DEVICEID}\_sp_fandrying_setting_automode_starthour     | sensor | Plate Fan Drying Setting Automode Starthour     | 碗篮风干自动模式开始小时设置   |
| sensor.{DEVICEID}\_sp_fandrying_setting_automode_startminute   | sensor | Plate Fan Drying Setting Automode Startminute   | 碗篮风干自动模式开始分钟设置   |
| sensor.{DEVICEID}\_sp_fandrying_status                         | sensor | Plate Fan Drying Status                         | 碗篮风干状态                   |
| sensor.{DEVICEID}\_sp_fandrying_temperature                    | sensor | Plate Fan Drying Temperature                    | 碗篮风干温度                   |
| sensor.{DEVICEID}\_sp_heatingdisk_destination_time             | sensor | Plate Heating Disk Destination Time             | 碗篮加热盘目标时间             |
| sensor.{DEVICEID}\_sp_heatingdisk_order_destination_time       | sensor | Plate Heating Disk Order Destination Time       | 碗篮加热盘预约目标时间         |
| sensor.{DEVICEID}\_sp_heatingdisk_order_remaining_time         | sensor | Plate Heating Disk Order Remaining Time         | 碗篮加热盘预约剩余时间         |
| sensor.{DEVICEID}\_sp_heatingdisk_remaining_time               | sensor | Plate Heating Disk Remaining Time               | 碗篮加热盘剩余时间             |
| sensor.{DEVICEID}\_sp_heatingdisk_setting_automode_day         | sensor | Plate Heating Disk Setting Automode Day         | 碗篮加热盘自动模式日期设置     |
| sensor.{DEVICEID}\_sp_heatingdisk_setting_automode_starthour   | sensor | Plate Heating Disk Setting Automode Starthour   | 碗篮加热盘自动模式开始小时设置 |
| sensor.{DEVICEID}\_sp_heatingdisk_setting_automode_startminute | sensor | Plate Heating Disk Setting Automode Startminute | 碗篮加热盘自动模式开始分钟设置 |
| sensor.{DEVICEID}\_sp_heatingdisk_status                       | sensor | Plate Heating Disk Status                       | 碗篮加热盘状态                 |
| sensor.{DEVICEID}\_sp_heatingdisk_temperature                  | sensor | Plate Heating Disk Temperature                  | 碗篮加热盘温度                 |
| sensor.{DEVICEID}\_sp_uvc_destination_time                     | sensor | Plate UVC Destination Time                      | 碗篮UVC目标时间                |
| sensor.{DEVICEID}\_sp_uvc_order_destination_time               | sensor | Plate UVC Order Destination Time                | 碗篮UVC预约目标时间            |
| sensor.{DEVICEID}\_sp_uvc_order_remaining_time                 | sensor | Plate UVC Order Remaining Time                  | 碗篮UVC预约剩余时间            |
| sensor.{DEVICEID}\_sp_uvc_remaining_time                       | sensor | Plate UVC Remaining Time                        | 碗篮UVC剩余时间                |
| sensor.{DEVICEID}\_sp_uvc_setting_automode_day                 | sensor | Plate UVC Setting Automode Day                  | 碗篮UVC自动模式日期设置        |
| sensor.{DEVICEID}\_sp_uvc_setting_automode_starthour           | sensor | Plate UVC Setting Automode Starthour            | 碗篮UVC自动模式开始小时设置    |
| sensor.{DEVICEID}\_sp_uvc_setting_automode_startminute         | sensor | Plate UVC Setting Automode Startminute          | 碗篮UVC自动模式开始分钟设置    |
| sensor.{DEVICEID}\_sp_uvc_status                               | sensor | Plate UVC Status                                | 碗篮UVC状态                    |
| sensor.{DEVICEID}\_sp_uvc_temperature                          | sensor | Plate UVC Temperature                           | 碗篮UVC温度                    |
| sensor.{DEVICEID}\_total_firewall_temp                         | sensor | Firewall Temp                                   | 防火墙温度                     |
| sensor.{DEVICEID}\_total_gesture                               | sensor | Gesture                                         | 手势                           |
| sensor.{DEVICEID}\_total_ir                                    | sensor | IR                                              | 红外                           |
| sensor.{DEVICEID}\_total_lock_off_type                         | sensor | Lock Off Type                                   | 锁定关闭方式                   |
| sensor.{DEVICEID}\_total_lock_on_type                          | sensor | Lock On Type                                    | 锁定开启方式                   |
| sensor.{DEVICEID}\_total_shelving_unit_temp                    | sensor | Shelving Unit Temp                              | 置物架温度                     |
| sensor.{DEVICEID}\_total_speak                                 | sensor | Speak                                           | 语音播报                       |
| sensor.{DEVICEID}\_total_tips_code                             | sensor | Tips Code                                       | 提示代码                       |
| sensor.{DEVICEID}\_total_tips_type                             | sensor | Tips Type                                       | 提示类型                       |

## 服务

无服务
