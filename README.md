[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://hacs.xyz)
# Blueair Filter Integration for Home Assistant
A simple BlueAir sensor and fan integration for HomeAssistant.

The basic sensor integration uses a modified [unofficial BlueAir client](https://github.com/thedjinn/blueair-py) by @thedjinn gather information from the sensors and control the fan with @spikeyGG's implementation on BlueAir filters 

## Installation
### Recommended
- Install with [HACS](https://hacs.xyz/).
### Manual
- Copy custom_components/blueair to your HomeAssistant base config directory (the place where configuration.yaml lives)


## Configuration
The integration is configured through the Home Assistant UI. No need to edit yaml files today.

- Configuration -> Devices and Services -> Add Integration
- Search BlueAir, and enter your username and password
  
## Compatibility 
A note on compatibility and testing, I only have 280i filters. The API response from Blueair is different for other series of filters, and these differences may break the integration. Several people have contributed patches to make this integration work with other BlueAir models, and I'm really grateful for that help.

I'm relatively confident we are correctly supporting

:heavy_check_mark: Classic 280i

:heavy_check_mark: Classic 605

Other classic, and classic i models should be similar enough that I would expect them to work (Classic 480i, Classic 505 etc.).

If you have a filter from the [Protect](https://www.blueair.com/us/protect-family.html), [Dust Magnet](https://www.blueair.com/us/dustmagnet-family.html) or [Blue](https://www.blueair.com/us/blue-family.html) product lines (I'm not even sure if these are all connected devices) and are willing to share API responses and help up build support for these products please feel free to open an [Issue](https://github.com/mmaarrkk02/hass-blueair/issues) :)


![HASS BlueAir Device](https://raw.githubusercontent.com/mmaarrkk02/hass-blueair/main/device.png)

This project was forked from [aijayadams/hass-blueair](https://github.com/aijayadams/hass-blueair) as the original author has ceased maintaining it. Therefore, modifications have been made independently.


***

[commits-shield]: https://img.shields.io/github/commit-activity/y/mmaarrkk02/hass-blueair.svg?style=for-the-badge
[commits]: https://github.com/mmaarrkk02/hass-blueair/commits/main
[license-shield]: https://img.shields.io/github/license/mmaarrkk02/hass-blueair.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Bren%20Dahl%20%40dahlb-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/mmaarrkk02/hass-blueair.svg?style=for-the-badge
[releases]: https://github.com/mmaarrkk02/hass-blueair/releases