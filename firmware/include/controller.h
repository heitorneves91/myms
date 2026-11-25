#pragma once
#include <cmath>
#include <cstdint>

namespace myms {
enum class State { Idle, Preheat, Drying, Cooldown, Fault };
inline const char* name(State state) {
  switch (state) {
    case State::Idle: return "idle";
    case State::Preheat: return "fan-prerun";
    case State::Drying: return "drying";
    case State::Cooldown: return "cooldown";
    default: return "fault";
  }
}
struct Sample {
  float air = NAN, wall = NAN;
  bool valid = false;
  uint32_t at = 0;
};

// Initial engineering limits, NOT a validated operating envelope.
// Hysteresis is +/-1 C. Sensor values must be no older than 3 seconds.
class Controller {
 public:
  State state = State::Idle;
  const char* fault = "";
  bool heater = false, fan = false;
  float target = 45;
  uint32_t durationMs = 3600000;
  static constexpr float AIR_LIMIT = 65, WALL_LIMIT = 65, COOL_TEMP = 35;
  static constexpr uint32_t PRERUN_MS = 10000, COOLDOWN_MS = 120000, STALE_MS = 3000;

  bool fresh(const Sample& s, uint32_t now) const {
    return s.valid && std::isfinite(s.air) && std::isfinite(s.wall) &&
           s.air >= -20 && s.wall >= -20 && uint32_t(now - s.at) <= STALE_MS;
  }
  bool tooHot(const Sample& s) const { return s.air >= AIR_LIMIT || s.wall >= WALL_LIMIT; }
  const char* start(uint32_t now, const Sample& s, float requested, uint32_t seconds, bool enabled) {
    if (state != State::Idle) return "Controller must be idle";
    if (!enabled) return "Outputs disabled in monitor build; use simulation or reviewed dryer build";
    if (!std::isfinite(requested) || requested < 25 || requested > 55 || seconds < 60 || seconds > 86400)
      return "Target must be 25-55 C and duration 60-86400 seconds";
    if (!fresh(s, now)) return "Assign both sensors and wait for fresh readings";
    if (tooHot(s)) return "Sensors exceed initial engineering limits";
    target = requested;
    durationMs = seconds * 1000;
    started = changed = now;
    state = State::Preheat;
    fan = true;
    heater = false;
    return nullptr;
  }
  void stop(uint32_t now) {
    heater = false;
    if (state == State::Preheat || state == State::Drying) {
      state = State::Cooldown;
      changed = now;
      fan = true;
    }
  }
  bool reset(uint32_t now, const Sample& s) {
    if (state != State::Fault || !fresh(s, now) || s.air > COOL_TEMP || s.wall > COOL_TEMP) return false;
    state = State::Idle;
    fault = "";
    heater = fan = false;
    return true;
  }
  void tick(uint32_t now, const Sample& s, bool enabled) {
    bool valid = fresh(s, now);
    if (state != State::Fault && ((valid && tooHot(s)) ||
        ((state == State::Preheat || state == State::Drying || state == State::Cooldown) && !valid))) {
      fault = valid ? "Overtemperature" : "Sensor invalid or stale";
      state = State::Fault;
      heater = false;
      fan = enabled;
      return;
    }
    if (state == State::Fault) { heater = false; fan = enabled; return; }
    if (state == State::Idle) { heater = fan = false; return; }
    if (!enabled) { heater = fan = false; state = State::Idle; return; }
    fan = true;
    if ((state == State::Preheat || state == State::Drying) && uint32_t(now - started) >= durationMs) stop(now);
    if (state == State::Preheat && uint32_t(now - changed) >= PRERUN_MS) state = State::Drying;
    if (state == State::Drying) {
      if (s.air <= target - 1) heater = true;
      if (s.air >= target + 1) heater = false;
    }
    if (state == State::Cooldown) {
      heater = false;
      if (valid && uint32_t(now - changed) >= COOLDOWN_MS && s.air <= COOL_TEMP && s.wall <= COOL_TEMP) {
        state = State::Idle;
        fan = false;
      }
    }
  }
  uint32_t remaining(uint32_t now) const {
    if (state != State::Preheat && state != State::Drying) return 0;
    uint32_t elapsed = now - started;
    return elapsed >= durationMs ? 0 : (durationMs - elapsed + 999) / 1000;
  }
 private:
  uint32_t started = 0, changed = 0;
};
}  // namespace myms
