# Front Load Washer

## Entities

### Default entity

No default entity

### Extra entities

| EntityID                                  | Class         | Description                    |
| ----------------------------------------- | ------------- | ------------------------------ |
| sensor.{DEVICEID}\_status                 | sensor        | Status                         |
| sensor.{DEVICEID}\_mode                   | sensor        | Mode                           |
| sensor.{DEVICEID}\_progress               | sensor        | Progress                       |
| sensor.{DEVICEID}\_program                | sensor        | Program                        |
| sensor.{DEVICEID}\_water_level            | sensor        | Water Level                    |
| sensor.{DEVICEID}\_temperature            | sensor        | Temperature                    |
| sensor.{DEVICEID}\_dehydration_speed      | sensor        | Dehydration Speed              |
| sensor.{DEVICEID}\_dehydration_time       | sensor        | dehydration Time Level         |
| sensor.{DEVICEID}\_dehydration_time_value | sensor        | Dehydration Time Value         |
| sensor.{DEVICEID}\_wash_time              | sensor        | Wash Time Level                |
| sensor.{DEVICEID}\_wash_time_value        | sensor        | Wash Time Value                |
| sensor.{DEVICEID}\_time_remaining         | sensor        | Time Remaining                 |
| sensor.{DEVICEID}\_detergent              | sensor        | Detergent                      |
| sensor.{DEVICEID}\_softener               | sensor        | Softener                       |
| sensor.{DEVICEID}\_stains                 | sensor        | Stains                         |
| sensor.{DEVICEID}\_dirty_degree           | sensor        | Dirty Degree                   |
| switch.{DEVICEID}\_power                  | switch        | Power                          |
| switch.{DEVICEID}\_start                  | switch        | Start                          |
| select.{DEVICEID}\_program_control        | select        | Washer program                 |
| select.{DEVICEID}\_temperature_control    | select        | Water temperature              |
| select.{DEVICEID}\_spin_speed_control     | select        | Spin speed                     |
| select.{DEVICEID}\_rinse_count            | select        | Rinse count                    |
| select.{DEVICEID}\_water_level_control    | select        | Water level                    |
| select.{DEVICEID}\_detergent_control      | select        | Detergent dosing               |
| select.{DEVICEID}\_wash_time_control      | select        | Wash time (min)                |
| select.{DEVICEID}\_spin_time_control      | select        | Spin time (min)                |
| switch.{DEVICEID}\_forget_free            | switch        | Forget-free care               |
| time.{DEVICEID}\_appointment_finish       | time          | Finish time (sets reservation) |
| button.{DEVICEID}\_cancel_appointment     | button        | Cancel reservation             |
| binary_sensor.{DEVICEID}\_appointment     | binary_sensor | Reservation                    |

Parameter entities require the verified model/subtype and a supporting SDK.
Availability also depends on the current program and appliance state; see the
verified parameter controls section below.

## Service

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                 |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | A writable attribute listed below           |
| value     | The value for that attribute, listed below  |

| Writable attribute    | Accepted value                                                                                                     |
| --------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `power`, `start`      | `true` or `false`                                                                                                  |
| `appointment_finish`  | Timezone-bearing ISO completion datetime, whole minutes, within the next 24 hours; saving registers a future cycle |
| `program_control`     | Program option key from the program select entity's current `options`                                              |
| `temperature_control` | `"cold"`, `"20"`, `"30"`, `"40"`, `"60"`, `"95"`                                                                   |
| `spin_speed_control`  | `"0"`, `"400"`, `"600"`, `"800"`, `"1000"`, `"1200"`, `"1400"`                                                     |
| `rinse_count`         | `"1"`, `"2"`, `"3"`, `"4"`                                                                                         |
| `water_level_control` | `"auto"`, `"l1"`, `"l2"`, `"l3"`, `"l4"`                                                                           |
| `detergent_control`   | `"smart"`, `"off"`, `"l1"`, `"l2"`, `"l3"`, `"l4"`                                                                 |
| `wash_time_control`   | Actual minutes as a string from the select entity's current `options`                                              |
| `spin_time_control`   | Actual minutes as a string from the select entity's current `options`                                              |
| `forget_free`         | `true` or `false`                                                                                                  |

Select values use option keys, not translated UI labels. Use an option currently
offered by the corresponding entity. For example, `wash_time_control: "45"`
selects 45 actual minutes; it does not write request code 45. Parameter writes
have the same model, SDK, program and state restrictions as the entities.

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

## Completion-time reservations

Enable the `appointment_finish` time entity, `cancel_appointment` button and `appointment` binary sensor in the integration options. These require the verified model/subtype above and the companion SDK. In powered-on standby, use `time.set_value` to choose the completion clock time in one-minute steps. A past clock time means tomorrow; the window is the next 24 hours. One atomic command sets the reservation rather than separate hour/minute writes.

**Setting the completion time registers a future automatic cycle.** The protocol wait is the target deadline minus the current time minus the device-reported program duration. Targets that leave no positive wait, missing durations and running appliances are rejected. Completion remains an estimate that the appliance can adjust.

Use `button.press` on the cancel button to pause and clear both the reservation flag and wait while retaining other program parameters. State changes require real device replies. Ordinary parameters remain unavailable while queued, but reservation editing and cancellation remain available. The binary sensor independently reports the actual reservation flag.
