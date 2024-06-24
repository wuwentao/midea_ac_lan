# Heat Bump

## Features

- Supports target temperature
- Supports run mode
- Supports auxiliary heating

## Entities

### Default entity

| EntityID                    | Class   | Description    |
| --------------------------- | ------- | -------------- |
| climate.{DEVICEID}\_climate | climate | Climate entity |

### Extra entities

| EntityID                               | Class  | Description         |
| -------------------------------------- | ------ | ------------------- |
| sensor.{DEVICEID}\_current_temperature | sensor | Current Temperature |
| switch.{DEVICEID}\_aux_heating         | switch | Aux Heating         |
| switch.{DEVICEID}\_power               | switch | Power               |

## Service

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                 |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "aux_heating"<br/>"power"                   |
| value     | true or false                               |

Example

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: aux_heating
  value: true
```
