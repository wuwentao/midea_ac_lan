# Heat Pump Water Heater

## Features

- Supports target temperature
- Supports operating modes
- Supports capability-driven extended water-heater controls and diagnostics

Extended CD appliances can expose immediate and automatic disinfection,
configurable maximum and disinfection temperatures, maintenance reminders,
timer/schedule selection, Demand Response status, heat recovery, and optional
operating modes. Unsupported values remain hidden from the options flow because
the integration only lists attributes reported by `midea-lan`.

## Customize

- Set the temperature step of water heater (1 by default).

```json
{ "temperature_step": 0.5 }
```

- Set the protocol version for temperature unit handling

Some Heat Pump Water Heater models may display incorrect temperature units (showing Fahrenheit when it should be Celsius or vice versa). This is caused by different protocol versions used by various models. If you experience this issue, you can manually set the protocol version:

```json
{ "lua_protocol": "new" }
```

The `lua_protocol` setting can be set to:

- `auto` (default) - Automatically detect the protocol version
- `new` - Use the newer protocol version (try this first if temperature units are wrong)
- `old` - Use the older protocol version

**Note:** This setting specifically affects how temperature units are interpreted. If your device shows temperatures in the wrong unit (e.g., 140°F when it should be 60°C), try setting this to `"new"` or `"old"` to fix the issue.

## Entities

### Default entity

| EntityID                              | Class        | Description         |
| ------------------------------------- | ------------ | ------------------- |
| water_heater.{DEVICEID}\_water_heater | water_heater | Water heater entity |

### Extra entities

| EntityID                                    | Class         | Description                |
| ------------------------------------------- | ------------- | -------------------------- |
| binary_sensor.{DEVICEID}\_compressor_status | binary_sensor | Compressor Status          |
| sensor.{DEVICEID}\_compressor_temperature   | sensor        | Compressor Temperature     |
| sensor.{DEVICEID}\_condenser_temperature    | sensor        | Condenser Temperature      |
| sensor.{DEVICEID}\_outdoor_temperature      | sensor        | Outdoor Temperature        |
| sensor.{DEVICEID}\_water_level              | sensor        | Water Level                |
| number.{DEVICEID}\_disinfection_temperature | number        | Disinfection Temperature   |
| sensor.{DEVICEID}\_elec_heat                | sensor        | Electric Heat              |
| binary_sensor.{DEVICEID}\_top_elec_heat     | binary_sensor | Top Electric Heat          |
| binary_sensor.{DEVICEID}\_bottom_elec_heat  | binary_sensor | Bottom Electric Heat       |
| sensor.{DEVICEID}\_water_pump               | sensor        | Water Pump                 |
| sensor.{DEVICEID}\_four_way                 | sensor        | Four Way Valve             |
| sensor.{DEVICEID}\_back_water               | sensor        | Back Water                 |
| sensor.{DEVICEID}\_sterilize                | sensor        | Sterilize                  |
| sensor.{DEVICEID}\_top_temperature          | sensor        | Top Temperature            |
| sensor.{DEVICEID}\_bottom_temperature       | sensor        | Bottom Temperature         |
| sensor.{DEVICEID}\_wind                     | sensor        | Wind                       |
| binary_sensor.{DEVICEID}\_smart_grid        | binary_sensor | Smart Grid                 |
| binary_sensor.{DEVICEID}\_multi_terminal    | binary_sensor | Multi Terminal             |
| binary_sensor.{DEVICEID}\_mute_effect       | binary_sensor | Mute Effect                |
| binary_sensor.{DEVICEID}\_mute_status       | binary_sensor | Mute Status                |
| sensor.{DEVICEID}\_error_code               | sensor        | Error Code                 |
| sensor.{DEVICEID}\_typeinfo                 | sensor        | Type Info                  |
| binary_sensor.{DEVICEID}\_eco               | binary_sensor | ECO Mode Active            |
| switch.{DEVICEID}\_maintenance_reminder     | switch        | Maintenance Reminder       |
| binary_sensor.{DEVICEID}\_maintain_warn     | binary_sensor | Maintenance Warning        |
| binary_sensor.{DEVICEID}\_order1_effect     | binary_sensor | Schedule 1 Active          |
| binary_sensor.{DEVICEID}\_order2_effect     | binary_sensor | Schedule 2 Active          |
| number.{DEVICEID}\_max_temperature          | number        | Maximum Target Temperature |
| switch.{DEVICEID}\_vacation_mode            | switch        | Vacation Mode              |
| number.{DEVICEID}\_vacation_days            | number        | Vacation Days              |
| sensor.{DEVICEID}\_vacation_start_year      | sensor        | Vacation Start Year        |
| sensor.{DEVICEID}\_vacation_start_month     | sensor        | Vacation Start Month       |
| sensor.{DEVICEID}\_vacation_start_day       | sensor        | Vacation Start Day         |
| sensor.{DEVICEID}\_auto_sterilize_week      | sensor        | Auto Sterilize Week        |
| sensor.{DEVICEID}\_auto_sterilize_hour      | sensor        | Auto Sterilize Hour        |
| sensor.{DEVICEID}\_auto_sterilize_minute    | sensor        | Auto Sterilize Minute      |
| switch.{DEVICEID}\_power                    | switch        | Power                      |

### Extended CD entities

The following optional entities are offered only when the corresponding device
attribute has been reported. `Schedule Mode` uses `0` for off, `1` for the daily
timer, and `2` for the weekly schedule.

| EntityID                                                | Class         | Description                         |
| ------------------------------------------------------- | ------------- | ----------------------------------- |
| switch.{DEVICEID}\_disinfect                            | switch        | Immediate disinfection              |
| number.{DEVICEID}\_schedule_mode                        | number        | Off/daily/weekly schedule selection |
| sensor.{DEVICEID}\_max_temperature_upper_limit          | sensor        | Maximum-temperature upper limit     |
| sensor.{DEVICEID}\_max_temperature_lower_limit          | sensor        | Maximum-temperature lower limit     |
| sensor.{DEVICEID}\_disinfection_temperature_upper_limit | sensor        | Disinfection upper limit            |
| sensor.{DEVICEID}\_disinfection_temperature_lower_limit | sensor        | Disinfection lower limit            |
| binary_sensor.{DEVICEID}\_dr_enable                     | binary_sensor | Demand Response enabled             |
| sensor.{DEVICEID}\_dr_option                            | sensor        | Demand Response option              |
| binary_sensor.{DEVICEID}\_electric_rod_exception        | binary_sensor | Electric-heater fault               |
| sensor.{DEVICEID}\_remaining_hot_water_max              | sensor        | Maximum remaining hot-water value   |
| sensor.{DEVICEID}\_force_e_heating_status               | sensor        | Forced electric-heating status      |
| binary_sensor.{DEVICEID}\_ac_heater_priority            | binary_sensor | Heat-pump priority                  |
| binary_sensor.{DEVICEID}\_high_temp_reminder            | binary_sensor | High-temperature reminder           |
| binary_sensor.{DEVICEID}\_new_version_water_heater      | binary_sensor | Extended-protocol status            |
| sensor.{DEVICEID}\_holiday_max                          | sensor        | Maximum holiday duration            |
| sensor.{DEVICEID}\_holiday_min                          | sensor        | Minimum holiday duration            |
| sensor.{DEVICEID}\_timer_step_gap                       | sensor        | Timer increment                     |
| binary_sensor.{DEVICEID}\_heat_recovery_status          | binary_sensor | Heat-recovery status                |
| binary_sensor.{DEVICEID}\_holiday_mode                  | binary_sensor | Holiday-mode status                 |
| binary_sensor.{DEVICEID}\_hybrid_motion_mode            | binary_sensor | Hybrid-motion status                |

Capability diagnostics are also available for Boost, Silent, remaining hot
water, electric mode, automatic disinfection, forced electric heating,
time-of-use, heat-pump priority, heat recovery, heat-pump mode, Smart mode, and
negative-temperature support.

Weekly and daily schedule mappings are structured values and therefore remain
available through `midea_ac_lan.set_attribute` rather than scalar entities.

## Services

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                 |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "power"                                     |
| value     | true or false                               |

Example

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: false
```
