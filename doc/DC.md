# Clothes Dryer

## Entities

### Default entity

No default entity

### Extra entities

| EntityID                               | Class         | Description                    |
| -------------------------------------- | ------------- | ------------------------------ |
| sensor.{DEVICEID}\_progress            | sensor        | Progress                       |
| sensor.{DEVICEID}\_time_remaining      | sensor        | Time Remaining                 |
| sensor.{DEVICEID}\_status              | sensor        | Status                         |
| sensor.{DEVICEID}\_program             | sensor        | Program                        |
| sensor.{DEVICEID}\_dryness_level       | sensor        | Dryness Level                  |
| sensor.{DEVICEID}\_dry_temperature     | sensor        | Dry Temperature                |
| sensor.{DEVICEID}\_intensity           | sensor        | Intensity                      |
| sensor.{DEVICEID}\_material            | sensor        | Material                       |
| sensor.{DEVICEID}\_water_box           | sensor        | Water Box                      |
| sensor.{DEVICEID}\_door_warn           | sensor        | Door Warn                      |
| sensor.{DEVICEID}\_ai_switch           | sensor        | AI Switch                      |
| sensor.{DEVICEID}\_error_code          | sensor        | Error Code                     |
| switch.{DEVICEID}\_power               | switch        | Power                          |
| switch.{DEVICEID}\_start               | switch        | Start                          |
| select.{DEVICEID}\_program_control     | select        | Dryer program                  |
| select.{DEVICEID}\_dryness_control     | select        | Dryness                        |
| select.{DEVICEID}\_temperature_control | select        | Drying temperature             |
| switch.{DEVICEID}\_sterilize           | switch        | Multidimensional sterilization |
| switch.{DEVICEID}\_anti_wrinkle        | switch        | Smart anti-wrinkle             |
| number.{DEVICEID}\_timed_extra         | number        | Timed drying extension         |
| time.{DEVICEID}\_appointment_finish    | time          | Finish time (sets reservation) |
| button.{DEVICEID}\_cancel_appointment  | button        | Cancel reservation             |
| binary_sensor.{DEVICEID}\_appointment  | binary_sensor | Reservation                    |

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
| `dryness_control`     | `"ready_to_wear"` or `"storage"`; only `"ready_to_wear"` with sterilization on                                     |
| `temperature_control` | `"standard"` or `"low"`                                                                                            |
| `sterilize`           | `true` or `false`                                                                                                  |
| `anti_wrinkle`        | `true` or `false`                                                                                                  |
| `timed_extra`         | A number from 0 to 170 minutes, step 10, only in the timed drying program                                          |

Select values use option keys, not translated UI labels. Use an option currently
offered by the corresponding entity. Parameter writes have the same model, SDK,
program and state restrictions as the entities. `timed_extra: 0` means 10 total
minutes, while `timed_extra: 170` means 180 total minutes.

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

## Completion-time reservations

Enable the `appointment_finish` time entity, `cancel_appointment` button and `appointment` binary sensor in the integration options. These require the verified model/subtype above and the companion SDK. In powered-on standby, use `time.set_value` to choose the completion clock time in one-minute steps. A past clock time means tomorrow; the window is the next 24 hours. One atomic command sets the reservation rather than separate hour/minute writes.

**Setting the completion time registers a future automatic cycle.** The protocol wait is the target deadline minus the current time minus the device-reported program duration. Targets that leave no positive wait, missing durations and running appliances are rejected. Completion remains an estimate that the appliance can adjust.

Use `button.press` on the cancel button to pause and clear both the reservation flag and wait while retaining other program parameters. State changes require real device replies. Ordinary parameters remain unavailable while queued, but reservation editing and cancellation remain available. The binary sensor independently reports the actual reservation flag.

For this model, start is on during active reservation wait (status 8) and off during reservation pause (status 9). Start/resume retains the high byte of the wait minutes.
