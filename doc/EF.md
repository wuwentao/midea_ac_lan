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

| EntityID                                  | Class  | Description         |
| ----------------------------------------- | ------ | ------------------- |
| switch.{DEVICEID}\_ef_reserve             | switch | Reservation         |
| switch.{DEVICEID}\_ef_warm                | switch | Keep Warm           |
| select.{DEVICEID}\_ef_drink_style         | select | Drink Style         |
| number.{DEVICEID}\_ef_temperature_setting | number | Set Temperature     |
| number.{DEVICEID}\_ef_time_reserve_hr     | number | Reserve Hours       |
| number.{DEVICEID}\_ef_time_reserve_min    | number | Reserve Minutes     |
| number.{DEVICEID}\_ef_time_warm_hr        | number | Keep Warm Hours     |
| number.{DEVICEID}\_ef_time_warm_min       | number | Keep Warm Minutes   |
| number.{DEVICEID}\_ef_cmd_code            | number | Command Code        |
| number.{DEVICEID}\_ef_cmd_id              | number | Command ID          |
| sensor.{DEVICEID}\_ef_response_type       | sensor | Response            |
| sensor.{DEVICEID}\_ef_work_status         | sensor | Work Status         |
| sensor.{DEVICEID}\_ef_work_step           | sensor | Work Step           |
| sensor.{DEVICEID}\_ef_process_status      | sensor | Process Status      |
| sensor.{DEVICEID}\_ef_time_work_hr        | sensor | Work Hours          |
| sensor.{DEVICEID}\_ef_time_work_min       | sensor | Work Minutes        |
| sensor.{DEVICEID}\_ef_time_max            | sensor | Max Time            |
| sensor.{DEVICEID}\_ef_temperature_current | sensor | Current Temperature |
| sensor.{DEVICEID}\_error_code             | sensor | Error code          |

## Service

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                                                                                                                                                               |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance                                                                                                                                               |
| attribute | "reserve"<br />"warm"<br />"drink_style"<br />"temperature_setting"<br />"time_reserve_hr"<br />"time_reserve_min"<br />"time_warm_hr"<br />"time_warm_min"<br />"cmd_code"<br />"cmd_id" |
| value     | true/false for reserve/warm; "hot_drink"/"warm_drink" for drink_style; an integer within range for the numeric attributes                                                                 |

Example

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: drink_style
  value: hot_drink
```
