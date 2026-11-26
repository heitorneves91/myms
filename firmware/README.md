# MYMS ESP32-C3

Open `../myms.code-workspace` in VS Code and install the recommended PlatformIO IDE extension. Start with `simulation` (synthetic sensors) or the default `monitor` (real sensors, outputs disabled). Build, upload and open the 115200-baud serial monitor. Type `info` to see the device's access point and admin address.

Device Wi-Fi password: **`myms1234`**. The admin page and API require **no login**. The serial `info` command repeats Wi-Fi details.

Full setup, GPIO assumptions, control behavior, recording workflow and API: [Firmware guide](../docs/FIRMWARE.md).

```bash
pio run -e monitor
pio run -e simulation -t upload
pio device monitor -b 115200
```

`dryer` enables physical heater/fan outputs. Review `include/hardware_config.h` and actual hardware first: nothing has been wired or physically validated. Application-only uploads preserve recordings with the current partition layout; filesystem uploads/erase operations can delete them.

Firmware **0.2.0** adds manual **Fan only** and **Fan + heater** controls. Fan-only testing needs no sensors; heating remains regulated and requires both sensors, with pre-run/fault/cooldown handling. Manual modes run until stopped, including with the browser closed. Use `simulation` for a demonstration or the reviewed `dryer` configuration for actual outputs; `monitor` continues to disable output commands.

Firmware **0.4.0** enables **Test heater (20 s)** when sensors are unavailable: 10 s fan pre-run, a software-timed 20 s heater pulse and at least 2 min fan cooling, followed by fan-only operation until stopped. It cannot extend/restart an active test. Continuous regulated heat still requires sensors; this test does not establish temperature safety or actual fan operation.

Firmware 0.4.0 removes admin/API authentication and the computer recorder password prompt. The device AP remains password-protected with `myms1234`; local clients that can reach the device can operate its admin/API.
