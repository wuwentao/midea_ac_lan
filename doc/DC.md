# Clothes Dryer

## Entities

### Default entity

No default entity

### Extra entities

| EntityID                           | Class  | Description     |
| ---------------------------------- | ------ | --------------- |
| sensor.{DEVICEID}\_progress        | sensor | Progress        |
| sensor.{DEVICEID}\_time_remaining  | sensor | Time Remaining  |
| sensor.{DEVICEID}\_status          | sensor | Status          |
| sensor.{DEVICEID}\_program         | sensor | Program         |
| sensor.{DEVICEID}\_dryness_level   | sensor | Dryness Level   |
| sensor.{DEVICEID}\_dry_temperature | sensor | Dry Temperature |
| sensor.{DEVICEID}\_intensity       | sensor | Intensity       |
| sensor.{DEVICEID}\_material        | sensor | Material        |
| sensor.{DEVICEID}\_water_box       | sensor | Water Box       |
| sensor.{DEVICEID}\_door_warn       | sensor | Door Warn       |
| sensor.{DEVICEID}\_ai_switch       | sensor | AI Switch       |
| sensor.{DEVICEID}\_error_code      | sensor | Error Code      |
| switch.{DEVICEID}\_power           | switch | Power           |
| switch.{DEVICEID}\_start           | switch | Start           |

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

## Verified parameter controls: 38208801 / subtype 13367

In **CONFIGURE**, enable the additional **Dryer program**, **Dryness** and
**Drying temperature** selectors, **Multidimensional sterilization** and
**Smart anti-wrinkle** switches, and **Timed drying extension** number entity.
The protocol library exposes them only for this verified model/subtype pair.
Existing sensor, power and start entity identifiers are unchanged.

There are 36 confirmed ordinary programs, including school uniforms, chiffon,
polar fleece, yoga clothes, pet sterilization and the separate Hanfu™ styles.
DIY/pollen-allergy drying is omitted because its write protocol is unconfirmed.

Keep the dryer powered on and in standby or pause when changing parameters.
Running, delayed and fault states are not editable; parameter changes never
start drying. Displayed state follows real appliance replies without optimistic
updates, and unsupported per-program fields are unavailable.

- Ready-to-wear = 2; storage = 3. Unsupported dryness 0 is unavailable.
- Sterilization writes both the mode and feature flag, requests ready-to-wear,
  and limits the dryness menu accordingly. The appliance computes extra duration.
- Standard/low temperature reads the actual extended temperature field, separate
  from sterilization. The complete extended write preserves anti-wrinkle and
  season, rather than resetting other options.
- Timed extension is available only in timed program 26: 0–170 minutes, step 10.
  The machine's total duration is 10–180 minutes; the remaining-time sensor
  continues to use the real device report.

These controls require the companion protocol-library feature to be released
and the integration's `midea-lan` dependency updated by the maintainer. They are
safely skipped on older SDK versions; this feature does not change the pin.
