# Sungrow Export Limit

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

_Integration with [sungrow_http_config](https://github.com/ross-w/sungrow_http_config)._

**This integration will set up the following platforms.**

| Platform | Description                                                |
| -------- | ---------------------------------------------------------- |
| `switch` | Switch Sungrow Export Limit on or off                      |
| `number` | Control the export limit value in watts                    |

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `sungrow_export_limit`.
1. Download _all_ the files from the `custom_components/sungrow_export_limit/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Integration blueprint"

## Configuration is done in the UI

During setup, you will need to provide:
- **Host**: The IP address or hostname of your Sungrow inverter
- **Export Limit**: The export limit value in watts (e.g., 500W = 500)
- **Connection Mode**: Choose between "modbus" or "http" (default) connection methods

## Usage

After installation, you'll have two entities for each Sungrow inverter:

1. **Switch Entity**: Turns the export limit on or off. When turned off, the inverter will not limit export power.
2. **Number Entity**: Controls the export limit value in watts. This value is only applied when the switch is on. The minimum value is 10 watts (1 dekawatt), as the inverter does not accept lower values.

You can adjust the export limit value at any time using the number entity. The new value will be applied immediately if the switch is on, or will be applied the next time the switch is turned on.

**Note**: Setting an export limit of 0 dekawatts in the underlying module will result in the export limit being disabled. The minimum export limit is therefore 1 dekawatt (10 watts).

<!---->

## Contributions are welcome

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***
[license-shield]: https://img.shields.io/github/license/ross-w/sungrow-export-limit-ha
[commits-shield]: https://img.shields.io/github/commit-activity/y/ross-w/sungrow-export-limit-ha.svg?style=for-the-badge
[commits]: https://github.com/ross-w/sungrow-export-limit-ha/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[releases-shield]: https://img.shields.io/github/release/ross-w/sungrow-export-limit-ha.svg?style=for-the-badge
[releases]: https://github.com/ross-w/sungrow-export-limit-ha/releases
[maintenance-shield]: https://img.shields.io/maintenance/yes/2025
