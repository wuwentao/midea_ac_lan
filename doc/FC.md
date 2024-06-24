# Air Purifier

## Customize

Set the high/low value of PM2.5 to automatically turn standby mode on or off.

```json
{ "standby_detect": [50, 20] }
```

## Entities

### Default entity

No default entity.

### Extra entities

| EntityID                          | Class  | Description        |
| --------------------------------- | ------ | ------------------ |
| sensor.{DEVICEID}\_pm25           | sensor | PM 2.5             |
| sensor.{DEVICEID}\_tvoc           | sensor | TVOC               |
| sensor.{DEVICEID}\_hcho           | sensor | Methanal           |
| sensor.{DEVICEID}\_filter1_life   | sensor | Filter1 Life Level |
| sensor.{DEVICEID}\_filter2_life   | sensor | Filter2 Life Level |
| lock.{DEVICEID}\_child_lock       | lock   | Child Lock         |
| switch.{DEVICEID}\_anion          | switch | Anion              |
| switch.{DEVICEID}\_prompt_tone    | switch | Prompt Tone        |
| switch.{DEVICEID}\_power          | switch | Power              |
| switch.{DEVICEID}\_standby        | switch | Standby            |
| select.{DEVICEID}\_detect_mode    | select | Detect Mode        |
| select.{DEVICEID}\_mode           | select | Mode               |
| select.{DEVICEID}\_fan_speed      | select | Fan Speed          |
| select.{DEVICEID}\_screen_display | select | Screen Display     |

## Service

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                            |
| --------- | ------------------------------------------------------ |
| device_id | The Appliance code (Device ID) of appliance            |
| attribute | "child_lock"<br/>"anion"<br/>"prompt_tone"<br/>"power" |
| value     | true or false                                          |

| Name      | Description                                 |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "detect_mode"                               |
| value     | "Off"<br/>"PM 2.5"<br/>"Methanal"           |

| Name      | Description                                            |
| --------- | ------------------------------------------------------ |
| device_id | The Appliance code (Device ID) of appliance            |
| attribute | "mode"                                                 |
| value     | "Auto"<br/>"Manual"<br/>"Sleep"<br/>"Fast"<br/>"Smoke" |

| Name      | Description                                 |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "fan_speed"                                 |
| value     | "Auto"<br/>"Low"<br/>"Medium"<br/>"High"    |

| Name      | Description                                 |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "screen_display"                            |
| value     | "Bright"<br/>"Dim"<br/>"Off"                |

Example

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: prompt_tone
  value: true
```

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: fan_speed
  value: Auto
```
