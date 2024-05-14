# Midea AC LAN

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![Donate](https://img.shields.io/badge/donate-BuyMeCoffee-yellow.svg)](https://www.buymeacoffee.com/georgezhao2010)
[![Stable](https://img.shields.io/github/v/release/CyrielRct/midea_ac_lan)](https://github.com/CyrielRct/midea_ac_lan/releases/latest)
[![Super-Linter](https://github.com/<OWNER>/<REPOSITORY>/actions/workflows/<WORKFLOW_FILE_NAME>/badge.svg)](https://github.com/marketplace/actions/super-linter)

> :warning: **This is a fork of midea_ac_lan done by Georgezhao**

English | [简体中文](README_hans.md)

Control your Midea M-Smart appliances via local area network.

- Automated device discover and configuration based Home Assistant config flow UI.
- Extra sensors and switches.
- Synchronize status with the appliance by long TCP connection in time.

This component inspired from the repository at [@mac-zhou](https://github.com/mac-zhou/midea-msmart) which provides similar functionality for Midea air conditioners. This component include verbatim or adapted portions of the code from his great projects.

Thanks also to [@NeoAcheron](https://github.com/NeoAcheron/midea-ac-py).

⭐If this component is helpful for you, please star it, it encourages me a lot.

***❗Note: Home Assistant 2023.1 or higher required for this integration***

## Supported brands

![ariston](brands/ariston.png) ![beverly](brands/beverly.png) ![bugu](brands/bugu.png) \
![carrier](brands/carrier.png)  ![colmo](brands/colmo.png) ![comfee](brands/comfee.png) \
![electrolux](brands/electrolux.png) ![invertor](brands/invertor.png) ![littleswan](brands/littleswan.png) \
![midea](brands/midea.png) ![netsu](brands/netsu.png) ![ProBreeze](brands/probreeze.png) \
![rotenso](brands/rotenso.png) ![toshiba](brands/toshiba.png) ![vandelo](brands/vandelo.png) \
![wahin](brands/wahin.png)

And more.

## Supported appliances

| Type | Name                       | Documents          |
|------|----------------------------|--------------------|
| 13   | Light                      | [13.md](doc/13.md) |
| 26   | Bathroom Master            | [26.md](doc/26.md) |
| 34   | Sink Dishwasher            | [34.md](doc/34.md) |
| 40   | Integrated Ceiling Fan     | [40.md](doc/40.md) |
| A1   | Dehumidifier               | [A1.md](doc/A1.md) |
| AC   | Air Conditioner            | [AC.md](doc/AC.md) |
| B0   | Microwave Oven             | [B0.md](doc/B0.md) |
| B1   | Electric Oven              | [B1.md](doc/B1.md) |
| B3   | Dish Sterilizer            | [B3.md](doc/B3.md) |
| B4   | Toaster                    | [B4.md](doc/B4.md) |
| B6   | Range Hood                 | [B6.md](doc/B6.md) |
| BF   | Microwave Steam Oven       | [BF.md](doc/BF.md) |
| C2   | Toilet                     | [C2.md](doc/C2.md) |
| C3   | Heat Pump Wi-Fi Controller | [C3.md](doc/C3.md) |
| CA   | Refrigerator               | [CA.md](doc/CA.md) |
| CC   | MDV Wi-Fi Controller       | [CC.md](doc/CC.md) |
| CD   | Heat Pump Water Heater     | [CC.md](doc/CD.md) |
| CE   | Fresh Air Appliance        | [CE.md](doc/CE.md) |
| CF   | Heat Pump                  | [CF.md](doc/CF.md) |
| DA   | Top Load Washer            | [DA.md](doc/DA.md) |
| DB   | Front Load Washer          | [DB.md](doc/DB.md) |
| DC   | Clothes Dryer              | [DC.md](doc/DC.md) |
| E1   | Dishwasher                 | [E1.md](doc/E1.md) |
| E2   | Electric Water Heater      | [E2.md](doc/E2.md) |
| E3   | Gas Water Heater           | [E3.md](doc/E3.md) |
| E6   | Gas Stove                  | [E6.md](doc/E6.md) |
| E8   | Electric Slow Cooker       | [E8.md](doc/E8.md) |
| EA   | Electric Rice Cooker       | [EA.md](doc/EA.md) |
| EC   | Electric Pressure Cooker   | [EC.md](doc/EC.md) |
| ED   | Water Drinking Appliance   | [ED.md](doc/ED.md) |
| FA   | Fan                        | [FA.md](doc/FA.md) |
| FB   | Electric Heater            | [FB.md](doc/FB.md) |
| FC   | Air Purifier               | [FC.md](doc/FC.md) |
| FD   | Humidifier                 | [FD.md](doc/FD.md) |

## Installation

**Search `Midea AC LAN` in HACS not available now, it will be ready later**

Please use manual install as below:

Option 1:

1. make sure you have installed HACS to Home Assistant [HACS install guide](https://hacs.xyz/docs/setup/download)
2. open HACS, click [Custom repositories], Repository input: `https://github.com/wuwentao/midea_ac_lan`,  Category select [Integration]
3. **Restart Home Assistant**.

Option 2:

1. Download `midea_ac_lan.zip` from [Latest Release](https://github.com/wuwentao/midea_ac_lan/releases/latest)
2. copy `midea_ac_lan.zip` to  `/custom_components/midea_ac_lan` in Home Assistant.
3. **Restart Home Assistant**.

Once it done, open `[Settings]`, `[Device & services]`, `[Integrations]`, `[Midea AC Lan]`, do init config and add all your devices.

## Add device

***❗Note: First, set a static IP address for your appliance in the router, in case the IP address of the appliance changes after set-up.***

After installation, search and add component Midea AC LAN in Home Assistant integrations page.

Or click [![Configuration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=midea_ac_lan)

***❗Note: During the configuration process, you may be asked to enter your Midea account and password. It's necessary to retrieve appliance information (Token and Key) from Midea cloud server. After all appliances configured, you can remove the Midea account configuration without affecting the use of the appliance.***

After the account is configured, Click 'ADD DEVICE' once more to add new device. You could repeat the above action to add multiple devices.

### Discover automatically

Using this option, the component could auto-discover and list Midea M-Smart appliances in network or specified IP address, select one and add it in.

You can also use an IP address to search within a specified network, such as `192.168.1.255`.

***❗Note: Discovery automatically requires your appliances and your Home Assistant must be in the same sub-network. Otherwise, devices may not be auto-discovered.  Check this by yourself.***

### Configure manually

If you already know following information, you could add the appliance manually.

- Appliance code
- Appliance type (one of [Supported appliances](README.md#supported-appliances))
- IP address
- Port (default 6444)
- Protocol version
- Token
- Key

### List all appliances only

Using this option, you can list all discoverable Midea M-Smart devices on the network, along with their IDs, types, SNs, and other information.

***❗Note: For certain reasons, not all supported devices may be listed here.***

## Configure

Configure can be found in `Settings -> Devices & Services -> Midea AC LAN -> Devices -> CONFIGURE`.
You can re-set the IP address when device IP changed.
You can also add extra sensor and switch entities or customize your own device.

### IP address

Set the IP address of device. You can reset this when your device IP is changed.

### Refresh interval

Set the interval for actively refreshing the status of a single device (the unit is second) (30 by default and 0 means not refresh actively)
Mostly the status update of Midea devices relies on the active information notification of the device, \
in which condition the status update in HA still works normally even if the refresh interval is set to be "0". \
This component will also actively query the device status at regular intervals, and the default time is 30 seconds. \
Some devices do not have active information notifications when their status changed, so synchronization with the status in HA will be slower. \
If you are very concerned about the synchronization speed of the status, you can try to set a shorter status refresh interval.

***❗Note: shorter refresh interval may mean more power consumption***

### Extra sensor and switch entities

After configuration, one of few main entity (e.g. climate entity) may be generated . If you want to make the attributes to extra sensor and switch entities, click CONFIGURE in Midea AC LAN integration card to choose (if your devices supported).

### Customize

Some types of device have their own configuration items, if your device does not work properly, you may need to customize it. Refer to the device documentation for specific information.

The format of customizations must be JSON.

If multiple customization items need to be configured, the settings must comply with the JSON format.

Example

```json
{"refresh_interval": 15, "fan_speed":  100}
```

## Debug

Turn on the debug log out，config in configuration.yaml

```yaml
logger:
  default: warn
  logs:
    custom_components.midea_ac_lan: debug
```

## Support my works

If you like this integration, why do not you support my works by buying me a coffee?

[![Buy me a coffee](https://www.buymeacoffee.com/assets/img/custom_images/yellow_img.png)](https://www.buymeacoffee.com/georgezhao2010)
