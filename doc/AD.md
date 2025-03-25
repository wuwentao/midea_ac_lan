# Air Box

## Features

- Air sensor data from the Air Box
- Sleep module data from the Air Box

## Entity Generation

### Additional Generated Entities

| EntityID                                     | Type          | Name                    | Description                           |
| -------------------------------------------- | ------------- | ----------------------- | ------------------------------------- |
| sensor.{DEVICEID}\_temperature               | Sensor        | Temperature             | Temperature value                     |
| sensor.{DEVICEID}\_temperature_compensate    | Sensor        | Temperature Compensate  | Raw temperature value                 |
| sensor.{DEVICEID}\_humidity                  | Sensor        | Humidity                | Humidity value                        |
| sensor.{DEVICEID}\_humidity_compensate       | Sensor        | Humidity Compensate     | Raw humidity value                    |
| sensor.{DEVICEID}\_tvoc                      | Sensor        | TVOC                    | Total Volatile Organic Compounds      |
| sensor.{DEVICEID}\_co2                       | Sensor        | Carbon Dioxide          | CO₂ concentration                     |
| sensor.{DEVICEID}\_pm25                      | Sensor        | PM 2.5                  | Fine particulate concentration        |
| sensor.{DEVICEID}\_hcho                      | Sensor        | Methanal                | Formaldehyde concentration            |
| binary_sensor.{DEVICEID}\_presets_function   | Binary Sensor | Presets Function        | Preset function status                |
| binary_sensor.{DEVICEID}\_fall_asleep_status | Binary Sensor | Asleep Status           | Sleep induction status                |
| binary_sensor.{DEVICEID}\_portable_sense     | Binary Sensor | Portable Sense          | Portable sensing status               |
| binary_sensor.{DEVICEID}\_night_mode         | Binary Sensor | Night Mode              | Night mode status                     |
| binary_sensor.{DEVICEID}\_screen_status      | Binary Sensor | Screen Status           | Screen on/off status                  |
| binary_sensor.{DEVICEID}\_led_status         | Binary Sensor | Ambient Lighting Status | Ambient light status                  |
| binary_sensor.{DEVICEID}\_arofene_link       | Binary Sensor | Methanal Status         | Formaldehyde module connection status |
| binary_sensor.{DEVICEID}\_radar_exist        | Binary Sensor | Radar Status            | Radar module presence status          |
| binary_sensor.{DEVICEID}\_header_led_status  | Binary Sensor | Breathing Light         | Breathing light status                |
