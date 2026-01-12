# Air Conditioner

## Features

- Supports target temperature
- Supports run mode
- Supports fan mode
- Supports swing mode
- Supports preset mode
- Supports built-in fresh air system

### Supported Run-Modes

- Comfort Mode
- ECO Mode
- Boost Mode

## Customize

### Temperature setting step of AC

Default step: 0.5

```json
{ "temperature_step": 1 }
```

### Power consumption analysis method

There are 4 different methods to decode the consumption of an AC, but we don’t know which is right for your device.
If the power and/or energy consumption data looks incorrect, try another method and see if they are correct.
The options are 1 (binary), 2 (BCD), 3 (base/radix 100) and 12 (BCD like #2, but with an additional /10 divider for the energy values).

Default mode: 1

```json
{ "power_analysis_method": 2 }
```

Known settings:
| Device | Mode |
| :------------------------------- | ---: |
| Midea PortaSplit | 12 |

## Entities

### Default entity

| EntityID                    | Class   | Description    |
| --------------------------- | ------- | -------------- |
| climate.{DEVICEID}\_climate | climate | Climate entity |

### Extra entities

| EntityID                                      | Class         | Description                |
| --------------------------------------------- | ------------- | -------------------------- |
| sensor.{DEVICEID}\_full_dust                  | binary_sensor | Full of Dust               |
| sensor.{DEVICEID}\_indoor_humidity            | sensor        | Indoor humidity            |
| sensor.{DEVICEID}\_indoor_temperature         | sensor        | Indoor Temperature         |
| sensor.{DEVICEID}\_outdoor_temperature        | sensor        | Outdoor Temperature        |
| sensor.{DEVICEID}\_total_energy_consumption   | sensor        | Total Energy Consumption   |
| sensor.{DEVICEID}\_current_energy_consumption | sensor        | Current Energy Consumption |
| sensor.{DEVICEID}\_realtime_power             | sensor        | Realtime Power             |
| fan.{DEVICEID}\_fresh_air                     | fan           | Fresh Air Fan              |
| switch.{DEVICEID}\_aux_heating                | switch        | Aux Heating                |
| switch.{DEVICEID}\_boost_mode                 | switch        | Boost Mode                 |
| switch.{DEVICEID}\_breezeless                 | switch        | Breezeless                 |
| switch.{DEVICEID}\_comfort_mode               | switch        | Comfort Mode               |
| switch.{DEVICEID}\_dry                        | switch        | Dry                        |
| switch.{DEVICEID}\_eco_mode                   | switch        | ECO Mode                   |
| switch.{DEVICEID}\_indirect_wind              | switch        | Indirect Wind              |
| switch.{DEVICEID}\_natural_wind               | switch        | Natural Wind               |
| switch.{DEVICEID}\_prompt_tone                | switch        | Prompt Tone                |
| switch.{DEVICEID}\_power                      | switch        | Power                      |
| switch.{DEVICEID}\_screen_display             | switch        | Screen Display             |
| switch.{DEVICEID}\_screen_display_alternate   | switch        | Screen Display Alternate   |
| switch.{DEVICEID}\_smart_eye                  | switch        | Smart Eye                  |
| switch.{DEVICEID}\_swing_horizontal           | switch        | Swing Horizontal           |
| switch.{DEVICEID}\_swing_vertical             | switch        | Swing Vertical             |
| switch.{DEVICEID}\_wind_lr_angle              | select        | Airflow Horizontal         |
| switch.{DEVICEID}\_wind_ud_angle              | select        | Airflow Vertical           |
| switch.{DEVICEID}\_fan_speed                  | number        | Fan Speed Percent          |

## Built-in fresh air system

Some Midea appliance be named "Fresh Air Appliance", the protocol that actually uses the air conditioner. If your fresh air appliance is identified as an air conditioner, you should check the Fresh Air Fan entity in CONFIGURE, and use this fan entity to control your fresh air appliance.\*\*\*

## Services

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                                                                                                                                                                                                                                              |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| device_id | The Appliance code (Device ID) of appliance                                                                                                                                                                                                                              |
| attribute | "aux_heating"<br/>"breezeless"<br/>"comfort_mode"<br/>"dry"<br/>"eco_mode"<br/>"indirect_wind"<br/>"natural_wind"<br/>"prompt_tone"<br/>"power"<br/>"screen_display"<br/>"screen_display_2"<br/>"smart_eye"<br/>"swing_horizontal"<br/>"swing_vertical"<br/>"turbo_mode" |
| value     | true or false                                                                                                                                                                                                                                                            |

| Name      | Description                                 |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | fan_speed                                   |
| value     | Range 1 to 100 or "auto"                    |

Example

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: eco_mode
  value: true
```

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: fan_speed
  value: auto
```
