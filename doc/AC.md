# Air Conditioner
## Features
- Supports target temperature
- Supports run mode
- Supports fan mode
- Supports swing mode
- Supports preset mode
- Supports build-in fresh air system

### Supported Run-Modes
- Comfort Mode
- ECO Mode
- Boost Mode

## Customize

- Set the temperature step of AC (0.5 by default).

```json
{"temperature_step": 1}
```

- Power consumption analysis method (1 by default)

  There are 3 different methods to analyze the power consumption of an AC, but I don’t know which is right for your device. 
  If the power consumption data looks incorrect, try another method and see if they are correct. 
  The options include 1, 2, and 3.
  
```json
{"power_analysis_method": 2}
```

## Entities
### Default entity
| EntityID                   | Class   | Description    |
|----------------------------|---------|----------------|
| climate.{DEVICEID}_climate | climate | Climate entity |

### Extra entities

| EntityID                                     | Class         | Description                |
|----------------------------------------------|---------------|----------------------------|
| sensor.{DEVICEID}_full_dust                  | binary_sensor | Full of Dust               |
| sensor.{DEVICEID}_indoor_humidity            | sensor        | Indoor humidity            |
| sensor.{DEVICEID}_indoor_temperature         | sensor        | Indoor Temperature         |
| sensor.{DEVICEID}_outdoor_temperature        | sensor        | Outdoor Temperature        |
| sensor.{DEVICEID}_total_energy_consumption   | sensor        | Total Energy Consumption   |
| sensor.{DEVICEID}_current_energy_consumption | sensor        | Current Energy Consumption |
| sensor.{DEVICEID}_realtime_power             | sensor        | Realtime Power             |
| fan.{DEVICEID}_fresh_air                     | fan           | Fresh Air Fan              |
| switch.{DEVICEID}_aux_heating                | switch        | Aux Heating                |
| switch.{DEVICEID}_boost_mode                 | switch        | Boost Mode                 |
| switch.{DEVICEID}_breezeless                 | switch        | Breezeless                 |
| switch.{DEVICEID}_comfort_mode               | switch        | Comfort Mode               |
| switch.{DEVICEID}_dry                        | switch        | Dry                        |
| switch.{DEVICEID}_eco_mode                   | switch        | ECO Mode                   |
| switch.{DEVICEID}_indirect_wind              | switch        | Indirect Wind              |
| switch.{DEVICEID}_natural_wind               | switch        | Natural Wind               |
| switch.{DEVICEID}_prompt_tone                | switch        | Prompt Tone                |
| switch.{DEVICEID}_power                      | switch        | Power                      |
| switch.{DEVICEID}_screen_display             | switch        | Screen Display             |
| switch.{DEVICEID}_screen_display_alternate   | switch        | Screen Display Alternate   |
| switch.{DEVICEID}_smart_eye                  | switch        | Smart Eye                  |
| switch.{DEVICEID}_swing_horizontal           | switch        | Swing Horizontal           |
| switch.{DEVICEID}_swing_vertical             | switch        | Swing Vertical             |

## Build-in fresh air system

Some Midea appliance be named "Fresh Air Appliance", the protocol that actually uses the air conditioner. If your fresh air appliance is identified as an air conditioner, you should check the Fresh Air Fan entity in CONFIGURE, and use this fan entity to control your fresh air appliance.***

## Services

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                                                                                                                                                                                                                                              |
|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| device_id | The Appliance code (Device ID) of appliance                                                                                                                                                                                                                              |
| attribute | "aux_heating"<br/>"breezeless"<br/>"comfort_mode"<br/>"dry"<br/>"eco_mode"<br/>"indirect_wind"<br/>"natural_wind"<br/>"prompt_tone"<br/>"power"<br/>"screen_display"<br/>"screen_display_2"<br/>"smart_eye"<br/>"swing_horizontal"<br/>"swing_vertical"<br/>"turbo_mode" |
| value     | true or false                                                                                                                                                                                                                                                            |

| Name      | Description                                 |
|-----------|---------------------------------------------|
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