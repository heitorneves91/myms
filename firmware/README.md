# MYMS ESP32-C3

Open `../myms.code-workspace` in VS Code and install the recommended PlatformIO IDE extension. Start with `simulation` (synthetic sensors) or the default `monitor` (real sensors, outputs disabled). Build, upload and open the 115200-baud serial monitor. Type `info` to see the device's access point and admin credentials.

Device Wi-Fi password: **`myms1234`**. Admin login: **`admin` / `myms1234`**. This memorable default replaces generated passwords when this firmware is uploaded.

Full setup, GPIO assumptions, control behavior, recording workflow and API: [Firmware guide](../docs/FIRMWARE.md).

```bash
pio run -e monitor
pio run -e simulation -t upload
pio device monitor -b 115200
```

`dryer` enables physical heater/fan outputs. Review `include/hardware_config.h` and actual hardware first: nothing has been wired or physically validated. Application-only uploads preserve recordings with the current partition layout; filesystem uploads/erase operations can delete them.
