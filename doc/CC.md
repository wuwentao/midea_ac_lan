# MDV Wi-Fi Controller

## Features

- Supports target temperature
- Supports run mode
- Supports fan mode
- Supports swing mode
- Supports auxiliary heating

### Supported Run-Modes

- Sleep Mode
- ECO Mode

## Entities

### Default entity

| EntityID                    | Class   | Description    |
| --------------------------- | ------- | -------------- |
| climate.{DEVICEID}\_climate | climate | Climate entity |

### Extra entities

| EntityID                              | Class  | Description        |
| ------------------------------------- | ------ | ------------------ |
| sensor.{DEVICEID}\_indoor_temperature | sensor | Indoor Temperature |
| switch.{DEVICEID}\_aux_heating        | switch | Aux Heating        |
| switch.{DEVICEID}\_eco_mode           | switch | ECO Mode           |
| switch.{DEVICEID}\_night_light        | switch | Night Light        |
| switch.{DEVICEID}\_power              | switch | Power              |
| switch.{DEVICEID}\_sleep_mode         | switch | Sleep Mode         |
| switch.{DEVICEID}\_swing              | switch | Swing              |

## Service

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                                                              |
| --------- | ---------------------------------------------------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance                                              |
| attribute | "aux_heating"<br/>"eco_mode"<br/>"night_light"<br/>"power"<br />"sleep_mode"<br/>"swing" |
| value     | true or false                                                                            |

Example

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: eco_mode
  value: true
```
