# Water Drinking Appliance

## Entities

### Default entity

The following entities are created for tea bar appliance subtype 395:

| EntityID                                       | Class         | Description                                                                                                                                 |
| ---------------------------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| sensor.{DEVICEID}\_current_temperature         | sensor        | Current water temperature                                                                                                                   |
| sensor.{DEVICEID}\_target_temperature          | sensor        | Native target temperature                                                                                                                   |
| binary_sensor.{DEVICEID}\_heating              | binary_sensor | Water is heating                                                                                                                            |
| binary_sensor.{DEVICEID}\_dispensing           | binary_sensor | Water is being dispensed                                                                                                                    |
| switch.{DEVICEID}\_tea_bar                     | switch        | Boil Water Switch. Turning it on starts the appliance's automatic fill-and-boil cycle to 100 °C; turning it off stops boiling.              |
| climate.{DEVICEID}\_tea_bar_temperature        | climate       | Primary “Tea Bar” control. Turning it on starts the official 100 °C cycle; explicit targets use the supported 40–100 °C whole-degree range. |
| switch.{DEVICEID}\_tea_bar_child_lock          | switch        | Child lock with on/off semantics, using the official model 63000622 command.                                                                |
| switch.{DEVICEID}\_keep_warm                   | switch        | Keep-warm control using the official model 63000622 command.                                                                                |
| switch.{DEVICEID}\_cooling                     | switch        | Signal-cooling control using the official model 63000622 command.                                                                           |
| switch.{DEVICEID}\_screen_display              | switch        | Screen display; on lights the display and off sends the official sleep command.                                                             |
| number.{DEVICEID}\_keep_warm_time              | number        | Keep-warm duration from 1 to 12 hours in 0.5-hour steps.                                                                                    |
| sensor.{DEVICEID}\_keep_warm_remaining         | sensor        | Remaining keep-warm time; displayed as hours and minutes, with the exact source minutes retained as an attribute.                           |
| binary_sensor.{DEVICEID}\_lack_water           | binary_sensor | The appliance reports a lack-water condition.                                                                                               |
| binary_sensor.{DEVICEID}\_standby              | binary_sensor | The appliance reports standby state.                                                                                                        |
| binary_sensor.{DEVICEID}\_hot_water_dispensing | binary_sensor | Hot water is being dispensed.                                                                                                               |
| binary_sensor.{DEVICEID}\_fault                | binary_sensor | The appliance reports a non-zero fault code.                                                                                                |
| sensor.{DEVICEID}\_fault_code                  | sensor        | Raw model fault code reported by the appliance.                                                                                             |

### Extra entities

Water-softener controls and status entities listed below are exposed only for
subtype 703. They are not offered to tea bar appliance subtype 395.

#### Switches

| EntityID                                 | Class  | Description                |
| ---------------------------------------- | ------ | -------------------------- |
| switch.{DEVICEID}\_power                 | switch | Power                      |
| switch.{DEVICEID}\_soften                | switch | Softening (water softener) |
| switch.{DEVICEID}\_cl_sterilization      | switch | CL Sterilization           |
| switch.{DEVICEID}\_leak_water_protection | switch | Leak Water Protection      |
| switch.{DEVICEID}\_water_way             | switch | Water Way                  |
| switch.{DEVICEID}\_regeneration          | switch | Regeneration               |

#### Binary sensors

| EntityID                               | Class         | Description        |
| -------------------------------------- | ------------- | ------------------ |
| binary_sensor.{DEVICEID}\_leak_water   | binary_sensor | Leak Water (alarm) |
| binary_sensor.{DEVICEID}\_rsj_stand_by | binary_sensor | Stand By           |

#### Number

| EntityID                                       | Class  | Description                              |
| ---------------------------------------------- | ------ | ---------------------------------------- |
| number.{DEVICEID}\_water_hardness              | number | Water Hardness (raw value)               |
| number.{DEVICEID}\_flushing_days               | number | Flushing Days (regeneration cycle, days) |
| number.{DEVICEID}\_leak_water_protection_value | number | Leak Water Protection Value (L, step 50) |

#### Time

| EntityID                                  | Class | Description                                            |
| ----------------------------------------- | ----- | ------------------------------------------------------ |
| time.{DEVICEID}\_timing_regeneration_hour | time  | Timing Regeneration (scheduled regen time, e.g. 02:30) |

#### Sensors

| EntityID                                     | Class  | Description                                                |
| -------------------------------------------- | ------ | ---------------------------------------------------------- |
| sensor.{DEVICEID}\_filter1                   | sensor | Filter1 Available Days                                     |
| sensor.{DEVICEID}\_filter2                   | sensor | Filter2 Available Days                                     |
| sensor.{DEVICEID}\_filter3                   | sensor | Filter3 Available Days                                     |
| sensor.{DEVICEID}\_life1                     | sensor | Filter1 Life Level                                         |
| sensor.{DEVICEID}\_life2                     | sensor | Filter2 Life Level                                         |
| sensor.{DEVICEID}\_life3                     | sensor | Filter3 Life Level                                         |
| sensor.{DEVICEID}\_in_tds                    | sensor | In TDS                                                     |
| sensor.{DEVICEID}\_out_tds                   | sensor | Out TDS                                                    |
| sensor.{DEVICEID}\_water_consumption         | sensor | Water Consumption (for non soft-water subtypes)            |
| sensor.{DEVICEID}\_velocity                  | sensor | Velocity (current flow rate)                               |
| sensor.{DEVICEID}\_soft_available            | sensor | Soft Water Available (L)                                   |
| sensor.{DEVICEID}\_left_salt                 | sensor | Left Salt (%)                                              |
| sensor.{DEVICEID}\_remaining_days            | sensor | Remaining Days (until regeneration)                        |
| sensor.{DEVICEID}\_regeneration_left_seconds | sensor | Regeneration Left Seconds (0 = no active regeneration)     |
| sensor.{DEVICEID}\_use_days                  | sensor | Use Days                                                   |
| sensor.{DEVICEID}\_salt_setting              | sensor | Salt Setting (total salt capacity in KG; 0 = fixed)        |
| sensor.{DEVICEID}\_water_consumption_big     | sensor | Water Consumption (L, 2-decimal precision, soft water)     |
| sensor.{DEVICEID}\_water_consumption_average | sensor | Water Consumption Average (L)                              |
| sensor.{DEVICEID}\_error                     | sensor | Error (enum: 0=none, 1=E1 position, 230=E6 salt sensor...) |

## Service

No services.
