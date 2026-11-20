# Beverage Maker

Beverage / drink maker (device type 0xEF).

## Features

- Supports Reservation and Keep Warm switches
- Supports Drink Style selection (hot / warm)
- Supports Set Temperature and reservation / keep-warm timers
- Reports work status, process status, current temperature and error code

## Customize

No customize

## Entities

### Default entity

No default entity

### Extra entity

| EntityID                               | Class  | Description         |
| -------------------------------------- | ------ | ------------------- |
| switch.{DEVICEID}\_reserve             | switch | Reservation         |
| switch.{DEVICEID}\_warm                | switch | Keep Warm           |
| select.{DEVICEID}\_drink_style         | select | Drink Style         |
| number.{DEVICEID}\_temperature_setting | number | Set Temperature     |
| number.{DEVICEID}\_cmd_code            | number | Command Code        |
| number.{DEVICEID}\_cmd_id              | number | Command ID          |
| sensor.{DEVICEID}\_response_type       | sensor | Response            |
| sensor.{DEVICEID}\_work_status         | sensor | Work Status         |
| sensor.{DEVICEID}\_work_step           | sensor | Work Step           |
| sensor.{DEVICEID}\_process_status      | sensor | Process Status      |
| sensor.{DEVICEID}\_time_work_hr        | sensor | Work Hours          |
| sensor.{DEVICEID}\_time_work_min       | sensor | Work Minutes        |
| sensor.{DEVICEID}\_time_max            | sensor | Max Time            |
| sensor.{DEVICEID}\_temperature_current | sensor | Current Temperature |
| sensor.{DEVICEID}\_error_code          | sensor | Error code          |

## Service

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                                                                                                                                                               |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance                                                                                                                                               |
| attribute | "reserve"<br />"warm"<br />"drink_style"<br />"temperature_setting"<br />"cmd_code"<br />"cmd_id"                                                                                         |
| value     | true/false for reserve/warm; "hot_drink"/"warm_drink" for drink_style; an integer within range for the numeric attributes: temperature_setting (0-98), cmd_code (0-65535), cmd_id (0-255) |

Example

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: drink_style
  value: hot_drink
```
