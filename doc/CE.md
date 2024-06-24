# Fresh Air Appliance

**_Note: Some Midea appliance be named "Fresh Air Appliance", the protocol that actually uses the air conditioner. If your fresh air appliance is identified as an air conditioner, check out [Built-in fresh air system](CE.md#Built-in%20fresh%20air%20system)_**

## Features

- Supports fan speed
- Supports preset mode

## Customize

Set the levels of fan except "Auto" (7 by default).

```json
{ "speed_count": 5 }
```

## Entities

### Default entity

| EntityID            | Class | Description |
| ------------------- | ----- | ----------- |
| fan.{DEVICEID}\_fan | fan   | Fan entity  |

### Extra entities

| EntityID                                           | Class         | Description              |
| -------------------------------------------------- | ------------- | ------------------------ |
| binary_sensor.{DEVICEID}\_filter_cleaning_reminder | binary_sensor | Filter Cleaning Reminder |
| binary_sensor.{DEVICEID}\_filter_change_reminder   | binary_sensor | Filter Change Reminder   |
| sensor.{DEVICEID}\_current_humidity                | sensor        | Current Humidity         |
| sensor.{DEVICEID}\_current_temperature             | sensor        | Current Temperature      |
| sensor.{DEVICEID}\_co2                             | sensor        | Carbon Dioxide           |
| sensor.{DEVICEID}\_hcho                            | sensor        | Methanal                 |
| sensor.{DEVICEID}\_pm25                            | sensor        | PM 2.5                   |
| lock.{DEVICEID}\_child_lock                        | lock          | Child Lock               |
| switch.{DEVICEID}\_aux_heating                     | switch        | Aux Heating              |
| switch.{DEVICEID}\_eco_mode                        | switch        | ECO Mode                 |
| switch.{DEVICEID}\_link_to_ac                      | switch        | Link to AC               |
| switch.{DEVICEID}\_power                           | switch        | Power                    |
| switch.{DEVICEID}\_powerful_purify                 | switch        | Powerful Purification    |
| switch.{DEVICEID}\_sleep_mode                      | switch        | Sleep Mode               |

## Services

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                                                                                       |
| --------- | ----------------------------------------------------------------------------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance                                                                       |
| attribute | "child_lock"<br/>"aux_heating"<br/>"eco_mode"<br/>"link_to_ac"<br/>"power"<br/>"powerful_purify"<br/>"sleep_mode" |
| value     | true or false                                                                                                     |

Example

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: true
```
