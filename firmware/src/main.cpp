#include <Arduino.h>
#include <ArduinoJson.h>
#include <DallasTemperature.h>
#include <LittleFS.h>
#include <OneWire.h>
#include <Preferences.h>
#include <WebServer.h>
#include <WiFi.h>
#include <esp_system.h>
#include <esp_timer.h>
#include <sys/time.h>
#include <time.h>
#include "controller.h"
#include "hardware_config.h"
#include "web_ui.h"

using namespace myms;
constexpr bool SIM = MYMS_SIMULATION;
constexpr bool OUTPUTS = MYMS_OUTPUTS_ENABLED && !SIM;
constexpr bool CONTROL = OUTPUTS || SIM;
constexpr size_t MAX_SENSORS = 8, MAX_FILE = 512 * 1024, MAX_STORAGE = 1536 * 1024;
constexpr size_t MAX_SESSIONS = 24;
const char* VERSION = "0.4.0";
// Owner-requested Wi-Fi password. The admin page/API intentionally has no login.
constexpr char AP_PASSWORD[] = "myms1234";
static_assert(sizeof(AP_PASSWORD) >= 9 && sizeof(AP_PASSWORD) <= 64,
              "Wi-Fi password must contain 8-63 characters");
WebServer server(80);
Preferences prefs;
OneWire wire(SENSOR_PIN);
DallasTemperature sensors(&wire);
Controller controller;
Sample sample;
SemaphoreHandle_t controlMutex;
DeviceAddress addresses[MAX_SENSORS];
String roms[MAX_SENSORS], airRom, wallRom, deviceId, ssid;
float readings[MAX_SENSORS];
size_t sensorCount = 0;
bool fsReady = false;
File recording;
String recordingName, recordingError;
uint32_t logStarted = 0, logLast = 0, logInterval = 5000, logDuration = 3600000, logRows = 0;
uint32_t lastSerial = 0;

struct Guard {
  Guard() { xSemaphoreTake(controlMutex, portMAX_DELAY); }
  ~Guard() { xSemaphoreGive(controlMutex); }
};
String romString(const uint8_t* address) {
  char text[17];
  for (int i = 0; i < 8; i++) snprintf(text + 2 * i, 3, "%02x", address[i]);
  return text;
}
void drive(bool heater, bool fan) {
  if (!OUTPUTS) return;
  digitalWrite(HEATER_PIN, heater == HEATER_ACTIVE_HIGH ? HIGH : LOW);
  digitalWrite(FAN_PIN, fan == FAN_ACTIVE_HIGH ? HIGH : LOW);
}
bool temperatureValid(float value) {
  // 85 C is the DS18B20 power-up sentinel; above controller limits anyway.
  return isfinite(value) && value >= -20 && value <= 125 && value != 85;
}
void controlTask(void*) {
  uint32_t requested = millis();
  if (!SIM) sensors.requestTemperatures();
  for (;;) {
    uint32_t now = millis();
    if (uint32_t(now - requested) >= 1000) {
      float next[MAX_SENSORS];
      if (SIM) {
        Guard guard;
        float air = isfinite(sample.air) ? sample.air : 24;
        float wall = isfinite(sample.wall) ? sample.wall : 24;
        next[0] = air + (controller.heater ? 0.16f : (24 - air) * (controller.fan ? .012f : .003f));
        next[1] = wall + (next[0] - wall) * .04f;
      } else {
        for (size_t i = 0; i < sensorCount; i++) next[i] = sensors.getTempC(addresses[i]);
      }
      {
        Guard guard;
        sample = Sample{};
        for (size_t i = 0; i < sensorCount; i++) {
          readings[i] = temperatureValid(next[i]) ? next[i] : NAN;
          if (roms[i] == airRom) sample.air = readings[i];
          if (roms[i] == wallRom) sample.wall = readings[i];
        }
        sample.valid = isfinite(sample.air) && isfinite(sample.wall);
        sample.at = now;
      }
      if (!SIM) sensors.requestTemperatures();
      requested = now;
    }
    {
      Guard guard;
      controller.tick(now, sample, CONTROL);
      drive(controller.heater, controller.fan);
    }
    vTaskDelay(pdMS_TO_TICKS(20));
  }
}
bool checkMutation() {
  // Retain cross-origin form protection without requiring an admin login.
  if (server.header("X-MYMS-Request") != "1") {
    server.send(403, "application/json", "{\"error\":\"Missing X-MYMS-Request header\"}");
    return false;
  }
  return true;
}
void replyError(int status, const String& message) {
  StaticJsonDocument<256> doc;
  doc["error"] = message;
  String body;
  serializeJson(doc, body);
  server.send(status, "application/json", body);
}
void ok() { server.send(200, "application/json", "{\"ok\":true}"); }
bool body(JsonDocument& doc) {
  if (server.arg("plain").length() > 1024) { replyError(413, "Request too large"); return false; }
  if (deserializeJson(doc, server.arg("plain"))) { replyError(400, "Invalid JSON"); return false; }
  return true;
}
bool idle() { Guard guard; return controller.state == State::Idle; }
void number(JsonVariant target, float value) {
  if (isfinite(value)) target.set(value); else target.set(nullptr);
}
void fillStatus(JsonDocument& doc) {
  uint32_t now = millis();
  doc["version"] = VERSION;
  doc["device_id"] = deviceId;
  doc["simulation"] = SIM;
  doc["outputs_enabled"] = OUTPUTS;
  doc["control_enabled"] = CONTROL;
  doc["uptime_s"] = static_cast<uint64_t>(esp_timer_get_time()) / 1000000;
  doc["reset_reason"] = static_cast<int>(esp_reset_reason());
  doc["free_heap"] = ESP.getFreeHeap();
  doc["flash_bytes"] = ESP.getFlashChipSize();
  doc["ap_ssid"] = ssid;
  doc["ap_ip"] = WiFi.softAPIP().toString();
  doc["wifi_connected"] = WiFi.status() == WL_CONNECTED;
  doc["wifi_ip"] = WiFi.localIP().toString();
  if (WiFi.status() == WL_CONNECTED) doc["wifi_rssi"] = WiFi.RSSI();
  time_t utc = time(nullptr);
  if (utc >= 1700000000) doc["utc_s"] = utc;
  else doc["utc_s"] = nullptr;
  {
    Guard guard;
    doc["state"] = name(controller.state);
    doc["fault"] = controller.fault;
    number(doc["air_c"], sample.air);
    number(doc["wall_c"], sample.wall);
    doc["sensors_fresh"] = controller.fresh(sample, now);
    doc["sensor_age_ms"] = now - sample.at;
    doc["air_rom"] = airRom;
    doc["wall_rom"] = wallRom;
    if (controller.testMode()) doc["target_c"] = nullptr;
    else doc["target_c"] = controller.target;
    doc["heater_test_limit_s"] = Controller::HEATER_TEST_MS / 1000;
    doc["heater_test_remaining_s"] = controller.testRemaining(now);
    doc["remaining_s"] = controller.remaining(now);
    doc["heater"] = controller.heater;
    doc["fan"] = controller.fan;
    JsonArray list = doc.createNestedArray("sensors");
    for (size_t i = 0; i < sensorCount; i++) {
      JsonObject item = list.createNestedObject();
      item["rom"] = roms[i];
      number(item["temperature_c"], readings[i]);
    }
  }
  JsonObject log = doc.createNestedObject("recording");
  log["active"] = bool(recording);
  log["file"] = recordingName;
  log["rows"] = logRows;
  log["error"] = recordingError;
  log["interval_s"] = logInterval / 1000;
  log["remaining_s"] = recording ? (logDuration - min(logDuration, uint32_t(now - logStarted))) / 1000 : 0;
  log["fs_ready"] = fsReady;
  log["used_bytes"] = fsReady ? LittleFS.usedBytes() : 0;
  log["total_bytes"] = fsReady ? LittleFS.totalBytes() : 0;
}
String csvRow() {
  StaticJsonDocument<4096> status;
  fillStatus(status);
  char row[384];
  String utc = status["utc_s"].isNull() ? "" : status["utc_s"].as<String>();
  String air = status["air_c"].isNull() ? "" : String(status["air_c"].as<float>(), 3);
  String wall = status["wall_c"].isNull() ? "" : String(status["wall_c"].as<float>(), 3);
  String target = status["target_c"].isNull() ? "" : String(status["target_c"].as<float>(), 2);
  snprintf(row, sizeof(row), "1,%s,%s,%s,%llu,%lu,%s,%s,%s,%s,%d,%d,%s,%d\n",
    deviceId.c_str(), recordingName.c_str(), utc.c_str(),
    (unsigned long long)(esp_timer_get_time() / 1000), (unsigned long)(millis() - logStarted),
    air.c_str(), wall.c_str(), status["state"].as<const char*>(), target.c_str(),
    status["heater"].as<bool>(), status["fan"].as<bool>(), status["fault"].as<const char*>(), SIM);
  return row;
}
void closeRecording(const String& error = "") {
  if (recording) { recording.flush(); recording.close(); }
  recordingError = error;
}
void recordTick() {
  if (!recording) return;
  uint32_t now = millis();
  if (uint32_t(now - logStarted) >= logDuration) { closeRecording(); return; }
  if (uint32_t(now - logLast) < logInterval) return;
  logLast = now;
  String row = csvRow();
  if (recording.size() + row.length() > MAX_FILE || LittleFS.usedBytes() + row.length() > MAX_STORAGE) {
    closeRecording("Storage limit reached; download and delete old sessions"); return;
  }
  if (recording.print(row) != row.length()) { closeRecording("Filesystem write failed"); return; }
  recording.flush();
  logRows++;
}
bool csvPath(const String& path) {
  if (!path.startsWith("/session-") || !path.endsWith(".csv") || path.length() > 64) return false;
  for (size_t i = 1; i < path.length(); i++) {
    char c = path[i];
    if (!(isalnum(static_cast<unsigned char>(c)) || c == '-' || c == '.')) return false;
  }
  return true;
}
size_t sessionCount() {
  size_t count = 0;
  File root = LittleFS.open("/");
  File file = root.openNextFile();
  while (file) { if (!file.isDirectory()) count++; file = root.openNextFile(); }
  return count;
}
void routes() {
  const char* headers[] = {"X-MYMS-Request"};
  server.collectHeaders(headers, 1);
  server.on("/", HTTP_GET, [] {
    server.sendHeader("Cache-Control", "no-store");
    server.send_P(200, "text/html", WEB_UI);
  });
  server.on("/api/status", HTTP_GET, [] {
    StaticJsonDocument<4096> doc;
    fillStatus(doc);
    String json;
    serializeJson(doc, json);
    server.sendHeader("Cache-Control", "no-store");
    server.send(200, "application/json", json);
  });
  server.on("/api/start", HTTP_POST, [] {
    if (!checkMutation()) return;
    StaticJsonDocument<1024> doc;
    if (!body(doc)) return;
    if (!doc["target_c"].is<float>() || !doc["duration_s"].is<uint32_t>()) { replyError(400, "Numeric target and integer duration required"); return; }
    const char* error;
    {
      Guard guard;
      error = controller.start(millis(), sample, doc["target_c"], doc["duration_s"], CONTROL);
    }
    if (error) replyError(409, error); else ok();
  });
  server.on("/api/stop", HTTP_POST, [] {
    if (!checkMutation()) return;
    { Guard guard; controller.stop(millis()); drive(controller.heater, controller.fan); }
    ok();
  });
  server.on("/api/manual", HTTP_POST, [] {
    if (!checkMutation()) return;
    StaticJsonDocument<1024> doc;
    if (!body(doc)) return;
    String mode = doc["mode"] | "";
    if (mode != "fan" && mode != "heat" && mode != "test-heat") { replyError(400, "Mode must be fan, heat or test-heat"); return; }
    if (mode == "heat" && !doc["target_c"].is<float>()) { replyError(400, "Numeric target required for manual heat"); return; }
    const char* error;
    {
      Guard guard;
      if (mode == "fan") error = controller.manualFan(millis(), CONTROL);
      else if (mode == "test-heat") error = controller.testHeat(millis(), sample, CONTROL);
      else error = controller.manualHeat(millis(), sample, doc["target_c"], CONTROL);
      // Stop heat immediately when switching to fan/cooldown; never write a
      // raw output override that bypasses the controller task.
      drive(controller.heater, controller.fan);
    }
    if (error) replyError(409, error); else ok();
  });
  server.on("/api/reset-fault", HTTP_POST, [] {
    if (!checkMutation()) return;
    bool reset;
    { Guard guard; reset = controller.reset(millis(), sample); }
    if (reset) ok(); else replyError(409, "Fault reset requires fresh sensors at or below 35 C");
  });
  server.on("/api/sensors", HTTP_POST, [] {
    if (!checkMutation()) return;
    if (!idle()) { replyError(409, "Stop and cool down before changing sensor roles"); return; }
    StaticJsonDocument<1024> doc;
    if (!body(doc)) return;
    String air = doc["air_rom"] | "", wall = doc["wall_rom"] | "";
    bool foundAir = false, foundWall = false;
    for (size_t i = 0; i < sensorCount; i++) { foundAir |= roms[i] == air; foundWall |= roms[i] == wall; }
    if (!foundAir || !foundWall || air == wall) { replyError(400, "Choose two distinct discovered sensors"); return; }
    {
      Guard guard;
      airRom = air; wallRom = wall;
      sample = Sample{};
    }
    if (!SIM) { prefs.putString("air_rom", air); prefs.putString("wall_rom", wall); }
    ok();
  });
  server.on("/api/clock", HTTP_POST, [] {
    if (!checkMutation()) return;
    StaticJsonDocument<1024> doc;
    if (!body(doc)) return;
    if (!doc["utc_s"].is<int64_t>()) { replyError(400, "Integer UTC epoch required"); return; }
    int64_t epoch = doc["utc_s"];
    if (epoch < 1700000000 || epoch > 4102444800LL) { replyError(400, "UTC epoch out of range"); return; }
    timeval tv = {static_cast<time_t>(epoch), 0};
    settimeofday(&tv, nullptr);
    ok();
  });
  server.on("/api/wifi", HTTP_POST, [] {
    if (!checkMutation()) return;
    if (!idle() || recording) { replyError(409, "Wi-Fi changes require idle controller and stopped recording"); return; }
    StaticJsonDocument<1024> doc;
    if (!body(doc)) return;
    String network = doc["ssid"] | "", key = doc["password"] | "";
    if (network.length() > 32 || key.length() > 63 || (key.length() && key.length() < 8)) { replyError(400, "Invalid Wi-Fi credentials"); return; }
    prefs.putString("wifi_ssid", network); prefs.putString("wifi_key", key);
    WiFi.disconnect(false, false);
    if (network.length()) WiFi.begin(network.c_str(), key.c_str());
    ok();
  });
  server.on("/api/record/start", HTTP_POST, [] {
    if (!checkMutation()) return;
    if (!fsReady || recording) { replyError(409, "Initialize storage first; only one recording at a time"); return; }
    StaticJsonDocument<1024> doc;
    if (!body(doc)) return;
    if (!doc["interval_s"].is<uint32_t>() || !doc["duration_s"].is<uint32_t>()) { replyError(400, "Integer interval and duration required"); return; }
    uint32_t interval = doc["interval_s"], duration = doc["duration_s"];
    if (interval < 1 || interval > 3600 || duration < interval || duration > 604800) { replyError(400, "Interval 1-3600 s; duration between interval and 604800 s"); return; }
    if (LittleFS.usedBytes() >= MAX_STORAGE - 4096) { replyError(409, "Storage full; download and delete sessions"); return; }
    if (sessionCount() >= MAX_SESSIONS) { replyError(409, "24-session limit reached; download and delete sessions"); return; }
    uint32_t sequence = prefs.getUInt("session_seq", 0) + 1;
    prefs.putUInt("session_seq", sequence);
    recordingName = "/session-" + String(sequence) + "-" + String(esp_random(), HEX) + ".csv";
    recording = LittleFS.open(recordingName, "w");
    if (!recording) { replyError(500, "Cannot create CSV"); return; }
    const char* header = "schema,device_id,session,utc_s,uptime_ms,elapsed_ms,air_c,wall_c,state,target_c,heater_command,fan_command,fault,simulation\n";
    if (recording.print(header) != strlen(header)) { closeRecording("Header write failed"); replyError(500, recordingError); return; }
    recordingError = ""; logRows = 0;
    logInterval = interval * 1000; logDuration = duration * 1000;
    logStarted = millis(); logLast = logStarted - logInterval;
    recordTick(); ok();
  });
  server.on("/api/record/stop", HTTP_POST, [] { if (checkMutation()) { closeRecording(); ok(); } });
  server.on("/api/files", HTTP_GET, [] {
    DynamicJsonDocument doc(8192);
    JsonArray files = doc.createNestedArray("files");
    if (fsReady) {
      File root = LittleFS.open("/");
      File file = root.openNextFile();
      while (file) {
        String path = String("/") + file.name();
        if (path.startsWith("//")) path.remove(0, 1);
        if (csvPath(path)) {
          JsonObject entry = files.createNestedObject();
          entry["name"] = path; entry["bytes"] = file.size();
          entry["active"] = recording && path == recordingName;
        }
        file = root.openNextFile();
      }
    }
    String json; serializeJson(doc, json); server.send(200, "application/json", json);
  });
  server.on("/api/file", HTTP_GET, [] {
    String path = server.arg("name");
    if (!fsReady || !csvPath(path) || !LittleFS.exists(path)) { replyError(404, "CSV not found"); return; }
    if (recording) { replyError(409, "Stop recording before downloading files to avoid gaps in the CSV"); return; }
    File file = LittleFS.open(path, "r");
    server.sendHeader("Content-Disposition", "attachment; filename=\"" + path.substring(1) + "\"");
    server.streamFile(file, "text/csv");
    file.close();
  });
  server.on("/api/file/delete", HTTP_POST, [] {
    if (!checkMutation()) return;
    StaticJsonDocument<1024> doc;
    if (!body(doc)) return;
    String path = doc["name"] | "";
    if (!fsReady || !csvPath(path) || !LittleFS.exists(path)) { replyError(404, "CSV not found"); return; }
    if (recording && path == recordingName) { replyError(409, "Cannot delete active recording"); return; }
    if (LittleFS.remove(path)) ok(); else replyError(500, "Delete failed");
  });
  server.on("/api/storage/initialize", HTTP_POST, [] {
    if (!checkMutation()) return;
    if (!idle() || recording || fsReady) { replyError(409, "Initialization only allowed for unmounted storage while idle"); return; }
    StaticJsonDocument<1024> doc;
    if (!body(doc)) return;
    if (doc["confirm"].as<String>() != "ERASE RECORDINGS") { replyError(400, "Explicit erase confirmation required"); return; }
    if (LittleFS.format()) fsReady = LittleFS.begin(false);
    if (fsReady) ok(); else replyError(500, "Filesystem initialization failed");
  });
  server.onNotFound([] { replyError(404, "Not found"); });
}
void setup() {
  // Set output latches before enabling GPIO. External hardware must also default off at reset.
  if (OUTPUTS) {
    digitalWrite(HEATER_PIN, HEATER_ACTIVE_HIGH ? LOW : HIGH);
    digitalWrite(FAN_PIN, FAN_ACTIVE_HIGH ? LOW : HIGH);
    pinMode(HEATER_PIN, OUTPUT); pinMode(FAN_PIN, OUTPUT);
  }
  Serial.begin(115200);
  controlMutex = xSemaphoreCreateMutex();
  if (!controlMutex) { drive(false, false); abort(); }
  prefs.begin("myms", false);
  WiFi.persistent(false);
  WiFi.mode(WIFI_AP_STA);
  uint64_t mac = ESP.getEfuseMac();
  char id[13]; snprintf(id, sizeof(id), "%012llx", (unsigned long long)mac);
  deviceId = id; ssid = "MYMS-" + deviceId.substring(6);
  airRom = prefs.getString("air_rom", ""); wallRom = prefs.getString("wall_rom", "");
  if (SIM) {
    sensorCount = 2; roms[0] = "2800000000000001"; roms[1] = "2800000000000002";
    airRom = roms[0]; wallRom = roms[1];
  } else {
    sensors.begin(); sensors.setResolution(12); sensors.setWaitForConversion(false);
    DeviceAddress address;
    for (uint8_t i = 0; i < sensors.getDeviceCount() && sensorCount < MAX_SENSORS; i++) {
      if (sensors.getAddress(address, i) && address[0] == 0x28 && OneWire::crc8(address, 7) == address[7]) {
        memcpy(addresses[sensorCount], address, 8);
        roms[sensorCount++] = romString(address);
      }
    }
  }
  for (size_t i = 0; i < MAX_SENSORS; i++) readings[i] = NAN;
  fsReady = LittleFS.begin(false);  // Never silently format existing measurement data.
  if (!fsReady) recordingError = "Storage uninitialized or cannot mount; initialize explicitly in admin";
  WiFi.softAP(ssid.c_str(), AP_PASSWORD);
  String network = prefs.getString("wifi_ssid", "");
  if (network.length()) WiFi.begin(network.c_str(), prefs.getString("wifi_key", "").c_str());
  if (xTaskCreate(controlTask, "myms-control", 4096, nullptr, 2, nullptr) != pdPASS) {
    drive(false, false); abort();
  }
  routes(); server.begin();
  Serial.printf("\nMYMS %s | %s | %s\nAP: %s | http://192.168.4.1\nWi-Fi password: %s | Admin: no login\n",
    VERSION, SIM ? "SIMULATION" : (OUTPUTS ? "DRYER" : "MONITOR: outputs disabled"), deviceId.c_str(), ssid.c_str(), AP_PASSWORD);
  Serial.println("Type 'info' then Enter to repeat connection details. Sensors discovered only at boot.");
}
void loop() {
  server.handleClient();
  recordTick();
  if (Serial.available()) {
    static String command;
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (command == "info") Serial.printf("AP %s http://192.168.4.1 | Wi-Fi password: %s | Admin: no login\n", ssid.c_str(), AP_PASSWORD);
      command = "";
    } else if (command.length() < 32) command += c;
  }
  if (uint32_t(millis() - lastSerial) >= 5000) {
    lastSerial = millis();
    Controller snapshot;
    Sample temperatures;
    { Guard guard; snapshot = controller; temperatures = sample; }
    // Do not hold the control mutex while a disconnected USB host might block output.
    Serial.printf("[%lu ms] %s air=%.2f wall=%.2f heat=%d fan=%d fault=%s\n", (unsigned long)millis(), name(snapshot.state), temperatures.air, temperatures.wall, snapshot.heater, snapshot.fan, snapshot.fault);
  }
  delay(2);
}
