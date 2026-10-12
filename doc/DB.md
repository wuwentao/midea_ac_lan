# Front Load Washer

## Entities

### Default entity

No default entity

### Extra entities

| EntityID                                  | Class  | Description            |
| ----------------------------------------- | ------ | ---------------------- |
| sensor.{DEVICEID}\_status                 | sensor | Status                 |
| sensor.{DEVICEID}\_mode                   | sensor | Mode                   |
| sensor.{DEVICEID}\_progress               | sensor | Progress               |
| sensor.{DEVICEID}\_program                | sensor | Program                |
| sensor.{DEVICEID}\_water_level            | sensor | Water Level            |
| sensor.{DEVICEID}\_temperature            | sensor | Temperature            |
| sensor.{DEVICEID}\_dehydration_speed      | sensor | Dehydration Speed      |
| sensor.{DEVICEID}\_dehydration_time       | sensor | dehydration Time Level |
| sensor.{DEVICEID}\_dehydration_time_value | sensor | Dehydration Time Value |
| sensor.{DEVICEID}\_wash_time              | sensor | Wash Time Level        |
| sensor.{DEVICEID}\_wash_time_value        | sensor | Wash Time Value        |
| sensor.{DEVICEID}\_time_remaining         | sensor | Time Remaining         |
| sensor.{DEVICEID}\_detergent              | sensor | Detergent              |
| sensor.{DEVICEID}\_softener               | sensor | Softener               |
| sensor.{DEVICEID}\_stains                 | sensor | Stains                 |
| sensor.{DEVICEID}\_dirty_degree           | sensor | Dirty Degree           |
| switch.{DEVICEID}\_power                  | switch | Power                  |
| switch.{DEVICEID}\_start                  | switch | Start                  |

## Service

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                 |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "power"<br/>"start"                         |
| value     | true or false                               |

Example

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: true
```

## Verified parameter controls: 38131140 / subtype 13145

In **CONFIGURE**, enable the additional select entities for program, water
temperature, spin speed, rinse count, water level, detergent dosing, wash time
and spin time, plus the **Forget-free care** switch. These entities are exposed
only when the protocol library identifies this verified model/subtype pair.
Existing sensor, power and start entity identifiers are unchanged.

The program selector contains 30 confirmed cycles, including deep tub clean,
yoga clothes and quick-drying clothes. Keep the washer powered on and in standby
before adjusting parameters; running, delayed, fault and service-mode states are
not editable. Parameter changes never start the washer.

Wash/spin selections display actual minutes, with the unit in the entity name.
Options derive from the current effective time and request level. For example,
mixed wash with cold water offers 42/45/50/55/60 minutes; at 30°C it offers
11/14/19/24/29. Spin 8/9/10/11/12 minutes has request codes 3/4/0/1/2, rather than
being a linear 8–12 write. Smart detergent and L4 use distinct codes 4 and 5.
Unavailable fields remain unavailable; the integration does not invent defaults.

Forget-free care uses the model's V2 fresh-air switch and preserves the full
current program settings, including custom wash/spin time selections. Displayed
state always follows the appliance's real reply. No cloud connection is needed
for these parameter writes.

These controls require the companion protocol-library feature to be released
and the integration's `midea-lan` dependency updated by the maintainer. They are
safely skipped on older SDK versions; this feature does not change the pin.
