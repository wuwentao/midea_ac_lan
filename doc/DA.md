# Top Load Washer

## Entities

### Default entity

No default entity

### Extra entities

| EntityID                          | Class  | Description    |
| --------------------------------- | ------ | -------------- |
| sensor.{DEVICEID}\_progress       | sensor | Progress       |
| sensor.{DEVICEID}\_time_remaining | sensor | Time Remaining |
| switch.{DEVICEID}\_power          | switch | Power          |
| switch.{DEVICEID}\_start          | switch | Start          |

## Service

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                 |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "power"<br/>"start"                         |
| value     | true or false                               |

Example

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: true
```
