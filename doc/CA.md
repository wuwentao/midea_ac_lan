# Refrigerator

## Entities

### Default entity

No default entity.

### Extra entities

| EntityID                                             | Class         | Description                         |
| ---------------------------------------------------- | ------------- | ----------------------------------- |
| binary_sensor.{DEVICEID}\_bar_door                   | binary_sensor | Bar Door                            |
| binary_sensor.{DEVICEID}\_bar_door_overtime          | binary_sensor | Bar Door Overtime                   |
| binary_sensor.{DEVICEID}\_flex_zone_door             | binary_sensor | Flex-zone Door                      |
| binary_sensor.{DEVICEID}\_flex_zone_door_overtime    | binary_sensor | Flex-zone Door Overtime             |
| binary_sensor.{DEVICEID}\_freezer_door               | binary_sensor | Freezer Door                        |
| binary_sensor.{DEVICEID}\_freezer_door_overtime      | binary_sensor | Freezer Door Overtime               |
| binary_sensor.{DEVICEID}\_refrigerator_door          | binary_sensor | Refrigerator Door                   |
| binary_sensor.{DEVICEID}\_refrigerator_door_overtime | binary_sensor | Refrigerator Door Overtime          |
| binary_sensor.{DEVICEID}\_microcrystal_fresh         | binary_sensor | Microcrystal Fresh                  |
| binary_sensor.{DEVICEID}\_electronic_smell           | binary_sensor | Deodorizing sterilizing             |
| sensor.{DEVICEID}\_flex_zone_actual_temp             | sensor        | Flex-zone Actual Temperature        |
| sensor.{DEVICEID}\_flex_zone_setting_temp            | sensor        | Flex-zone Setting Temperature       |
| sensor.{DEVICEID}\_freezer_actual_temp               | sensor        | Freezer Actual Temperature          |
| sensor.{DEVICEID}\_freezer_setting_temp              | sensor        | Freezer Setting Temperature         |
| sensor.{DEVICEID}\_energy_consumption                | sensor        | Energy Consumptio                   |
| sensor.{DEVICEID}\_refrigerator_actual_temp          | sensor        | Refrigerator Actual Temperature     |
| sensor.{DEVICEID}\_refrigerator_setting_temp         | sensor        | Refrigerator setting Temperature    |
| sensor.{DEVICEID}\_right_flex_zone_actual_temp       | sensor        | Right Flex-zone Actual Temperature  |
| sensor.{DEVICEID}\_right_flex_zone_setting_temp      | sensor        | Right Flex-zone Setting Temperature |
| sensor.{DEVICEID}\_humidity                          | sensor        | Humidity                            |
| sensor.{DEVICEID}\_variable_mode                     | sensor        | Variable Mode                       |

### 310A2111 flex-zone mode

For model `310A2111`, subtype `56`, the optional `variable_mode` sensor derives
the App preset from the reported flex-zone **setting** temperature: 6°C is
Mother & Infant (`baby`), 2°C is Treasure (`treasure`), and 0°C is Zero Degree
(`zero`). Other temperatures, missing values, and non-numeric values are
reported as unknown. This is a read-only interpretation; it sends no commands.
Other refrigerator models and subtypes retain their existing mode behavior.

Enable Variable Mode under the integration's extra sensor options. The entity
ID remains `sensor.{DEVICEID}_variable_mode`.

## Service

No services.
