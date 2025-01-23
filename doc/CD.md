# Heat Pump Water Heater

## Features

- Supports target temperature
- Supports operating modes

## Customize

- Set the temperature step of water heater (1 by default).

```json
{ "temperature_step": 0.5 }
```

- switch temperature between Fahrenheit and Celsius

if you got a error temperature value between Fahrenheit and Celsius, you can manual change it with:

```json
{ "lua_protocol": new }
```

其中`lua_protocol`为key, 不能修改，值可以设置为`old`, `new`, `auto`(default is `auto`).

## Entities

### Default entity

| EntityID                              | Class        | Description         |
| ------------------------------------- | ------------ | ------------------- |
| water_heater.{DEVICEID}\_water_heater | water_heater | Water heater entity |

### Extra entities

| EntityID                                    | Class         | Description                                             |
| ------------------------------------------- | ------------- | ------------------------------------------------------- |
| sensor.{DEVICEID}\_compressor_temperature   | sensor        | Compressor Temperature                                  |
| sensor.{DEVICEID}\_condenser_temperature    | sensor        | Condenser Temperature                                   |
| sensor.{DEVICEID}\_outdoor_temperature      | sensor        | Outdoor Temperature                                     |
| sensor.{DEVICEID}\_water_level              | sensor        | Water Level                                             |
| binary_sensor.{DEVICEID}\_compressor_status | binary_sensor | Compressor Status (It may doesn't work in some devices) |
| switch.{DEVICEID}\_power                    | switch        | Power                                                   |

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
