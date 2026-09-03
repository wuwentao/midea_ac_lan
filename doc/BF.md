# Microwave Steam Oven

## Entities

### Default entity

No default entity

### Extra entities

#### Switches

| EntityID                         | Class  | Description   |
| -------------------------------- | ------ | ------------- |
| switch.{DEVICEID}\_power         | switch | Power         |
| switch.{DEVICEID}\_child_lock    | switch | Child Lock    |
| switch.{DEVICEID}\_furnace_light | switch | Furnace Light |
| switch.{DEVICEID}\_hot_wind      | switch | Hot Wind      |
| switch.{DEVICEID}\_ramadan       | switch | Ramadan       |
| switch.{DEVICEID}\_turntable     | switch | Turntable     |

#### Selects

| EntityID                              | Class  | Description        | Options                                       |
| ------------------------------------- | ------ | ------------------ | --------------------------------------------- |
| select.{DEVICEID}\_work_mode_select   | select | Work Mode          | BF work mode names from midea-lan             |
| select.{DEVICEID}\_fire_power_select  | select | Fire Power         | fire_power_0 through fire_power_10            |
| select.{DEVICEID}\_temperature_select | select | Target Temperature | Integer temperature values from 0 through 250 |

#### Binary sensors

| EntityID                                        | Class         | Description           |
| ----------------------------------------------- | ------------- | --------------------- |
| binary_sensor.{DEVICEID}\_pre_heat              | binary_sensor | Pre Heat              |
| binary_sensor.{DEVICEID}\_tank_ejected          | binary_sensor | Tank Ejected          |
| binary_sensor.{DEVICEID}\_water_change_reminder | binary_sensor | Water Change Reminder |
| binary_sensor.{DEVICEID}\_door                  | binary_sensor | Door                  |
| binary_sensor.{DEVICEID}\_water_shortage        | binary_sensor | Water shortage        |
| binary_sensor.{DEVICEID}\_error                 | binary_sensor | Error                 |
| binary_sensor.{DEVICEID}\_flip_side             | binary_sensor | Flip Side Reminder    |
| binary_sensor.{DEVICEID}\_reaction              | binary_sensor | Reaction              |
| binary_sensor.{DEVICEID}\_high_temperature_lock | binary_sensor | High Temperature Lock |
| binary_sensor.{DEVICEID}\_high_temperature_work | binary_sensor | High Temperature Work |
| binary_sensor.{DEVICEID}\_high_temperature      | binary_sensor | High Temperature      |
| binary_sensor.{DEVICEID}\_probe_mode            | binary_sensor | Probe Mode            |
| binary_sensor.{DEVICEID}\_probe                 | binary_sensor | Probe                 |
| binary_sensor.{DEVICEID}\_clean_scale           | binary_sensor | Clean Scale           |
| binary_sensor.{DEVICEID}\_clean_sink_ponding    | binary_sensor | Clean Sink Ponding    |
| binary_sensor.{DEVICEID}\_dissipate_heat        | binary_sensor | Dissipate Heat        |

#### Sensors

| EntityID                                     | Class  | Description                   |
| -------------------------------------------- | ------ | ----------------------------- |
| sensor.{DEVICEID}\_status                    | sensor | Status                        |
| sensor.{DEVICEID}\_work_mode                 | sensor | Work Mode                     |
| sensor.{DEVICEID}\_fire_power                | sensor | Fire Power                    |
| sensor.{DEVICEID}\_current_temperature       | sensor | Current Temperature           |
| sensor.{DEVICEID}\_temperature               | sensor | Target Temperature            |
| sensor.{DEVICEID}\_temperature_above         | sensor | Temperature Above             |
| sensor.{DEVICEID}\_temperature_underside     | sensor | Temperature Underside         |
| sensor.{DEVICEID}\_cur_temperature_above     | sensor | Current Temperature Above     |
| sensor.{DEVICEID}\_cur_temperature_underside | sensor | Current Temperature Underside |
| sensor.{DEVICEID}\_probe_temperature         | sensor | Probe Temperature             |
| sensor.{DEVICEID}\_cur_probe_temperature     | sensor | Current Probe Temperature     |
| sensor.{DEVICEID}\_time_remaining            | sensor | Time Remaining                |
| sensor.{DEVICEID}\_steam_quantity            | sensor | Steam Quantity                |
| sensor.{DEVICEID}\_weight                    | sensor | Weight (g)                    |
| sensor.{DEVICEID}\_people_number             | sensor | People Number                 |
| sensor.{DEVICEID}\_totalstep                 | sensor | Total Steps                   |
| sensor.{DEVICEID}\_stepnum                   | sensor | Current Step                  |
| sensor.{DEVICEID}\_cloudmenuid               | sensor | Cloud Menu ID                 |
| sensor.{DEVICEID}\_execute                   | sensor | Execute Status                |

## Service

No service
