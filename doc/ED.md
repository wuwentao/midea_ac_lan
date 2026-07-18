# Water Drinking Appliance

## Entities

### Default entity

No default entity.

### Extra entities

#### Switches

| EntityID                                    | Class   | Description                  |
| ------------------------------------------- | ------- | ---------------------------- |
| switch.{DEVICEID}\_power                    | switch  | Power                        |
| lock.{DEVICEID}\_child_lock                 | switch  | Child Lock                   |
| switch.{DEVICEID}\_soften                  | switch  | Softening (water softener)  |
| switch.{DEVICEID}\_cl_sterilization         | switch  | CL Sterilization             |
| switch.{DEVICEID}\_leak_water_protection   | switch  | Leak Water Protection        |
| switch.{DEVICEID}\_water_way               | switch  | Water Way                    |
| switch.{DEVICEID}\_regeneration            | switch  | Regeneration                 |

#### Binary sensors

| EntityID                                       | Class         | Description                          |
| ---------------------------------------------- | ------------- | ------------------------------------ |
| binary_sensor.{DEVICEID}\_leak_water          | binary_sensor | Leak Water (alarm)                  |
| binary_sensor.{DEVICEID}\_rsj_stand_by        | binary_sensor | Stand By                            |

#### Number

| EntityID                                       | Class  | Description                                    |
| ---------------------------------------------- | ------ | ---------------------------------------------- |
| number.{DEVICEID}\_water_hardness              | number | Water Hardness (raw value)                     |
| number.{DEVICEID}\_flushing_days               | number | Flushing Days (regeneration cycle, days)       |
| number.{DEVICEID}\_leak_water_protection_value | number | Leak Water Protection Value (L, step 50)       |

#### Time

| EntityID                                       | Class | Description                                                       |
| ---------------------------------------------- | ----- | ----------------------------------------------------------------- |
| time.{DEVICEID}\_timing_regeneration_hour      | time  | Timing Regeneration (scheduled regen time, e.g. 02:30)           |

#### Sensors

| EntityID                                       | Class  | Description                                                   |
| ---------------------------------------------- | ------ | ------------------------------------------------------------- |
| sensor.{DEVICEID}\_filter1                    | sensor | Filter1 Available Days                                       |
| sensor.{DEVICEID}\_filter2                    | sensor | Filter2 Available Days                                       |
| sensor.{DEVICEID}\_filter3                    | sensor | Filter3 Available Days                                       |
| sensor.{DEVICEID}\_life1                      | sensor | Filter1 Life Level                                           |
| sensor.{DEVICEID}\_life2                      | sensor | Filter2 Life Level                                           |
| sensor.{DEVICEID}\_life3                      | sensor | Filter3 Life Level                                           |
| sensor.{DEVICEID}\_in_tds                     | sensor | In TDS                                                       |
| sensor.{DEVICEID}\_out_tds                    | sensor | Out TDS                                                      |
| sensor.{DEVICEID}\_water_consumption          | sensor | Water Consumption (for non soft-water subtypes)              |
| sensor.{DEVICEID}\_velocity                   | sensor | Velocity (current flow rate)                                 |
| sensor.{DEVICEID}\_soft_available             | sensor | Soft Water Available (L)                                     |
| sensor.{DEVICEID}\_left_salt                  | sensor | Left Salt (%)                                                |
| sensor.{DEVICEID}\_remaining_days             | sensor | Remaining Days (until regeneration)                          |
| sensor.{DEVICEID}\_regeneration_left_seconds | sensor | Regeneration Left Seconds (0 = no active regeneration)       |
| sensor.{DEVICEID}\_use_days                   | sensor | Use Days                                                     |
| sensor.{DEVICEID}\_salt_setting               | sensor | Salt Setting (total salt capacity in KG; 0 = fixed)          |
| sensor.{DEVICEID}\_water_consumption_big      | sensor | Water Consumption (L, 2-decimal precision, soft water)       |
| sensor.{DEVICEID}\_water_consumption_average  | sensor | Water Consumption Average (L)                                |
| sensor.{DEVICEID}\_error                      | sensor | Error (enum: 0=none, 1=E1 position, 230=E6 salt sensor...)  |

## Service

No services.
