# Warming Cooking Appliance

Steam / warming cooking appliance (device type 0xEB).

## Features

- Supports Function selection
- Supports Work status control
- Supports Fire level control
- Supports Reservation timer
- Supports Countdown timer
- Reports running / remaining time and work stage

## Customize

No customize

## Entities

### Default entity

No default entity

### Extra entity

| EntityID                                | Class  | Description       |
| --------------------------------------- | ------ | ----------------- |
| number.{DEVICEID}\_eb_function_no       | number | Function number   |
| number.{DEVICEID}\_eb_work_status       | number | Work status       |
| number.{DEVICEID}\_eb_fire_level        | number | Fire level        |
| number.{DEVICEID}\_eb_time_reserve_hr   | number | Reserve hours     |
| number.{DEVICEID}\_eb_time_reserve_min  | number | Reserve minutes   |
| number.{DEVICEID}\_eb_definite_time_hr  | number | Timer hours       |
| number.{DEVICEID}\_eb_definite_time_min | number | Timer minutes     |
| sensor.{DEVICEID}\_eb_time_running_hr   | sensor | Running hours     |
| sensor.{DEVICEID}\_eb_time_running_min  | sensor | Running minutes   |
| sensor.{DEVICEID}\_eb_time_surplus_hr   | sensor | Remaining hours   |
| sensor.{DEVICEID}\_eb_time_surplus_min  | sensor | Remaining minutes |
| sensor.{DEVICEID}\_eb_work_stage        | sensor | Work stage        |
| sensor.{DEVICEID}\_error_code           | sensor | Error code        |

## Service

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                                                                                                                        |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance                                                                                                        |
| attribute | "function_no"<br />"work_status"<br />"fire_level"<br />"time_reserve_hr"<br />"time_reserve_min"<br />"definite_time_hr"<br />"definite_time_min" |
| value     | an integer within the attribute's range                                                                                                            |

Example

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: fire_level
  value: 5
```
