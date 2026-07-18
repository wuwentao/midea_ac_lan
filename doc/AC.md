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

### Temperature range of AC

The min/max target temperature shown by the climate entity. By default it is
read from the device capability (B5 message) when available, otherwise it falls
back to 16–30 °C. Set these options to override the range manually, for example
when your device reports a wrong range or does not report one at all (confirm the
expected values via the Midea app or the remote control). Each value is optional.

```json
{ "min_temperature": 16, "max_temperature": 30 }
```

### Capabilities (modes / swing / presets)

The available run-modes, fan speeds, swing support and presets are detected
automatically from the device's B5 capability report. A cooling-only portable
AC, for example, then exposes only `cool`/`dry`/`fan_only`, the `low`/`high`/
`auto` fan speeds, no swing, and no presets.

Some capabilities cannot be derived (older library, or features the protocol
does not declare such as the `comfort` and `sleep` presets). You can override
them via customize (confirm the real values via the Midea app or remote):

```json
{
  "swing": false,
  "hvac_modes": ["off", "cool", "dry", "fan_only"],
  "preset_modes": ["none"]
}
```

- `swing` (bool): force the swing control on/off.
- `hvac_modes` (list): restrict the modes shown. `off` is always kept. Valid
  values: `off`, `auto`, `cool`, `dry`, `heat`, `fan_only`.
- `preset_modes` (list): restrict the presets. `none` is always kept; use
  `["none"]` to remove the preset control entirely. Valid values: `none`,
  `comfort`, `eco`, `boost`, `sleep`, `away`.

Priority is customize > B5 capabilities > defaults. All keys are optional; omit
them to use the auto-detected set.

### Power consumption analysis method

There are 5 different methods to decode the consumption of an AC, but we don’t know which is right for your device.
If the power and/or energy consumption data looks incorrect, try another method and see if they are correct.
The options are 1 (binary), 2 (BCD), 3 (base/radix 100),
12 (BCD like #2, but with an additional /10 divider for the energy values),
and 101 (BCD energy values with binary realtime power).

Default mode: 1

```json
{ "power_analysis_method": 2 }
```

Known settings:

| Device                     | Mode |
| :------------------------- | ---: |
| Midea PortaSplit           |   12 |
| Midea 00000Q1D subtype 524 |  101 |

### BB subprotocol diagnostics

Midea AC model 23096725 subtype 1 uses the BB subprotocol and does not implement
the traditional energy query. For this model the integration can expose the
compressor current and frequency reported by the outdoor unit, plus estimated
power, total estimated energy, and daily estimated energy. The daily value
resets at midnight in Home Assistant's configured time zone. Both energy values
are restored after an integration or Home Assistant restart. Estimated power is
calculated from compressor current, line voltage, and power factor; it is not a
substitute for a calibrated external energy meter.

The total estimate starts when this sensor is first enabled; it is not the
appliance's factory lifetime energy counter. These diagnostics are only offered
for the matching 0xAC model and subtype, and do not appear for other AC models.

The default line voltage is 220 V. The fallback power factor is 0.95 and is only
used when the device does not report one. Both values and the raw-current scale
can be customized:

```json
{
  "bb_power_voltage": 220,
  "bb_power_factor": 0.95,
  "bb_current_scale": 0.1
}
```

### C1 compressor frequency diagnostics

AC models 22390001 subtype 8 and 22390003 subtype 8 expose actual and target
compressor frequency, whole-ampere compressor and outdoor-unit current, and
whole-volt outdoor-unit RMS voltage in the otherwise unused C1 group 0x41
response. The integration adds this read-only query only for those model/subtype
combinations. These C1 frames do not report power factor or input power.

On a multi-split system, active indoor units connected to the same outdoor unit
report the same frequency. An inactive indoor unit reports 0 Hz even while a
different indoor unit is running. Do not add frequency-derived power estimates
from multiple indoor units: they refer to the same outdoor compressor. Frequency
alone is also insufficient for a universal power estimate because the outdoor
unit capacity and operating conditions affect power draw.

## Entities

### Default entity

| EntityID                    | Class   | Description    |
| --------------------------- | ------- | -------------- |
| climate.{DEVICEID}\_climate | climate | Climate entity |

### Extra entities

| EntityID                                      | Class         | Description                |
| --------------------------------------------- | ------------- | -------------------------- |
| sensor.{DEVICEID}\_full_dust                  | binary_sensor | Full of Dust               |
| sensor.{DEVICEID}\_self_clean_active          | binary_sensor | Self Clean Active          |
| sensor.{DEVICEID}\_indoor_humidity            | sensor        | Indoor humidity            |
| sensor.{DEVICEID}\_indoor_temperature         | sensor        | Indoor Temperature         |
| sensor.{DEVICEID}\_outdoor_temperature        | sensor        | Outdoor Temperature        |
| sensor.{DEVICEID}\_total_energy_consumption   | sensor        | Total Energy Consumption   |
| sensor.{DEVICEID}\_current_energy_consumption | sensor        | Current Energy Consumption |
| sensor.{DEVICEID}\_realtime_power             | sensor        | Realtime Power             |
| sensor.{DEVICEID}\_compressor_frequency        | sensor        | Compressor Frequency       |
| sensor.{DEVICEID}\_compressor_target_frequency | sensor        | Compressor Target Frequency |
| sensor.{DEVICEID}\_compressor_current          | sensor        | Compressor Current         |
| sensor.{DEVICEID}\_outdoor_unit_total_current  | sensor        | Outdoor Unit Total Current |
| sensor.{DEVICEID}\_outdoor_unit_voltage        | sensor        | Outdoor Unit Voltage       |
| sensor.{DEVICEID}\_estimated_realtime_power    | sensor        | Estimated Realtime Power   |
| sensor.{DEVICEID}\_estimated_total_energy_consumption | sensor | Estimated Total Energy Consumption |
| sensor.{DEVICEID}\_estimated_daily_energy_consumption | sensor | Estimated Daily Energy Consumption |
| sensor.{DEVICEID}\_pmv                        | sensor        | PMV (Predicted Mean Vote)  |
| sensor.{DEVICEID}\_error_code                 | sensor        | Error Code                 |
| fan.{DEVICEID}\_fresh_air                     | fan           | Fresh Air Fan              |
| switch.{DEVICEID}\_anion                      | switch        | Anion (Ionizer)            |
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
| switch.{DEVICEID}\_self_clean                 | switch        | Self Clean                 |
| switch.{DEVICEID}\_smart_eye                  | switch        | Smart Eye                  |
| switch.{DEVICEID}\_sound                      | switch        | Sound                      |
| switch.{DEVICEID}\_swing_horizontal           | switch        | Swing Horizontal           |
| switch.{DEVICEID}\_swing_vertical             | switch        | Swing Vertical             |
| switch.{DEVICEID}\_wind_lr_angle              | select        | Airflow Horizontal         |
| switch.{DEVICEID}\_wind_ud_angle              | select        | Airflow Vertical           |
| switch.{DEVICEID}\_rate_select                | select        | Power Rate Limit           |
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
