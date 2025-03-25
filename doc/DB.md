# Front Load Washer

## Entities

### Default entity

No default entity

### Extra entities

| EntityID                                  | Class  | Description            |
| ----------------------------------------- | ------ | ---------------------- |
| sensor.{DEVICEID}\_status                 | sensor | Status                 |
| sensor.{DEVICEID}\_mode                   | sensor | Mode                   |
| sensor.{DEVICEID}\_progress               | sensor | Progress               |
| sensor.{DEVICEID}\_program                | sensor | Program                |
| sensor.{DEVICEID}\_water_level            | sensor | Water Level            |
| sensor.{DEVICEID}\_temperature            | sensor | Temperature            |
| sensor.{DEVICEID}\_dehydration_speed      | sensor | Dehydration Speed      |
| sensor.{DEVICEID}\_dehydration_time       | sensor | dehydration Time Level |
| sensor.{DEVICEID}\_dehydration_time_value | sensor | Dehydration Time Value |
| sensor.{DEVICEID}\_wash_time              | sensor | Wash Time Level        |
| sensor.{DEVICEID}\_wash_time_value        | sensor | Wash Time Value        |
| sensor.{DEVICEID}\_time_remaining         | sensor | Time Remaining         |
| sensor.{DEVICEID}\_detergent              | sensor | Detergent              |
| sensor.{DEVICEID}\_softener               | sensor | Softener               |
| sensor.{DEVICEID}\_stains                 | sensor | Stains                 |
| sensor.{DEVICEID}\_dirty_degree           | sensor | Dirty Degree           |
| switch.{DEVICEID}\_power                  | switch | Power                  |
| switch.{DEVICEID}\_start                  | switch | Start                  |

## Service

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                 |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "power"<br/>"start"                         |
| value     | true or false                               |

Example

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: true
```
