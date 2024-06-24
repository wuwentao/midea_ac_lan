# Electric Heater

## Features

- Supports target temperature
- Supports preset mode

## Entities

### Default entity

| EntityID                    | Class   | Description    |
| --------------------------- | ------- | -------------- |
| climate.{DEVICEID}\_climate | climate | Climate entity |

### Extra entities

| EntityID                               | Class  | Description         |
| -------------------------------------- | ------ | ------------------- |
| sensor.{DEVICEID}\_current_temperature | sensor | Current Temperature |
| lock.{DEVICEID}\_child_lock            | lock   | Child Lock          |
| number.{DEVICEID}\_heating_level       | number | Heating Level       |
| switch.{DEVICEID}\_power               | switch | Power               |

## Service

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                 |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "child_lock"<br/>"power"                    |
| value     | true or false                               |

| Name      | Description                                 |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "heating_level"                             |
| value     | 1 - 10                                      |

Example

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: true
```

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: heating_level
  value: 9
```
