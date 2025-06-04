# Clothes Dryer

## Entities

### Default entity

No default entity

### Extra entities

| EntityID                           | Class  | Description     |
| ---------------------------------- | ------ | --------------- |
| sensor.{DEVICEID}\_progress        | sensor | Progress        |
| sensor.{DEVICEID}\_time_remaining  | sensor | Time Remaining  |
| sensor.{DEVICEID}\_status          | sensor | Status          |
| sensor.{DEVICEID}\_program         | sensor | Program         |
| sensor.{DEVICEID}\_dryness_level   | sensor | Dryness Level   |
| sensor.{DEVICEID}\_dry_temperature | sensor | Dry Temperature |
| sensor.{DEVICEID}\_intensity       | sensor | Intensity       |
| sensor.{DEVICEID}\_material        | sensor | Material        |
| sensor.{DEVICEID}\_water_box       | sensor | Water Box       |
| sensor.{DEVICEID}\_door_warn       | sensor | Door Warn       |
| sensor.{DEVICEID}\_ai_switch       | sensor | AI Switch       |
| sensor.{DEVICEID}\_error_code      | sensor | Error Code      |
| switch.{DEVICEID}\_power           | switch | Power           |
| switch.{DEVICEID}\_start           | switch | Start           |

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
