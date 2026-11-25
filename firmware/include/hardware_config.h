#pragma once

// PROPOSED pins: nothing has been wired or electrically verified yet.
// Verify the exact SuperMini board, MOSFET logic and independent fan driver.
// Avoid C3 strapping GPIO2/8/9 and USB GPIO18/19. GPIO4-7 also serve JTAG.
constexpr int SENSOR_PIN = 4;
constexpr int HEATER_PIN = 5;
constexpr int FAN_PIN = 6;
constexpr bool HEATER_ACTIVE_HIGH = true;
constexpr bool FAN_ACTIVE_HIGH = true;

#ifndef MYMS_OUTPUTS_ENABLED
#define MYMS_OUTPUTS_ENABLED 0
#endif
#ifndef MYMS_SIMULATION
#define MYMS_SIMULATION 0
#endif
static_assert(!(MYMS_OUTPUTS_ENABLED && MYMS_SIMULATION), "Simulation must never drive outputs");
static_assert(SENSOR_PIN != HEATER_PIN && SENSOR_PIN != FAN_PIN && HEATER_PIN != FAN_PIN,
              "Hardware pins must be distinct");
