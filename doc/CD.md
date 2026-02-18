# Heat Pump Water Heater

## Features

- Supports target temperature
- Supports operating modes

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

| EntityID                                    | Class         | Description                   |
| ------------------------------------------- | ------------- | ----------------------------- |
| binary_sensor.{DEVICEID}\_compressor_status | binary_sensor | Compressor Status             |
| sensor.{DEVICEID}\_compressor_temperature   | sensor        | Compressor Temperature        |
| sensor.{DEVICEID}\_condenser_temperature    | sensor        | Condenser Temperature         |
| sensor.{DEVICEID}\_outdoor_temperature      | sensor        | Outdoor Temperature           |
| sensor.{DEVICEID}\_water_level              | sensor        | Water Level                   |
| switch.{DEVICEID}\_disinfect                | switch        | Disinfect                     |
| sensor.{DEVICEID}\_elec_heat                | sensor        | Electric Heat                 |
| binary_sensor.{DEVICEID}\_top_elec_heat     | binary_sensor | Top Electric Heat             |
| binary_sensor.{DEVICEID}\_bottom_elec_heat  | binary_sensor | Bottom Electric Heat          |
| sensor.{DEVICEID}\_water_pump               | sensor        | Water Pump                    |
| sensor.{DEVICEID}\_four_way                 | sensor        | Four Way Valve                |
| sensor.{DEVICEID}\_back_water               | sensor        | Back Water                    |
| sensor.{DEVICEID}\_sterilize                | sensor        | Sterilize                     |
| sensor.{DEVICEID}\_top_temperature          | sensor        | Top Temperature               |
| sensor.{DEVICEID}\_bottom_temperature       | sensor        | Bottom Temperature            |
| sensor.{DEVICEID}\_wind                     | sensor        | Wind                          |
| binary_sensor.{DEVICEID}\_smart_grid        | binary_sensor | Smart Grid                    |
| binary_sensor.{DEVICEID}\_multi_terminal    | binary_sensor | Multi Terminal                |
| binary_sensor.{DEVICEID}\_mute_effect       | binary_sensor | Mute Effect                   |
| binary_sensor.{DEVICEID}\_mute_status       | binary_sensor | Mute Status                   |
| sensor.{DEVICEID}\_error_code               | sensor        | Error Code                    |
| sensor.{DEVICEID}\_typeinfo                 | sensor        | Type Info                     |
| switch.{DEVICEID}\_power                    | switch        | Power                         |

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
