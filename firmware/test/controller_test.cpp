#include "controller.h"
#include <cassert>
#include <iostream>
using namespace myms;
Sample valid(float air, float wall, uint32_t now) { return {air, wall, true, now}; }
int main() {
  Controller c;
  assert(c.start(0, valid(24,24,0),45,60,false));
  assert(c.state == State::Idle && !c.heater && !c.fan);
  assert(c.start(0, Sample{},45,60,true));
  assert(c.start(0, valid(24,24,0),NAN,60,true));
  assert(c.start(0, valid(24,24,0),56,60,true));
  assert(c.start(0, valid(24,24,0),45,59,true));
  assert(!c.start(0, valid(24,24,0),45,60,true));
  c.tick(9999, valid(24,24,9999),true);
  assert(c.fan && !c.heater && c.state == State::Preheat);
  c.tick(10000, valid(24,24,10000),true);
  assert(c.heater && c.fan && c.state == State::Drying);
  c.tick(11000, valid(45,24,11000),true); assert(c.heater);
  c.tick(12000, valid(46,24,12000),true); assert(!c.heater);
  c.tick(13000, valid(45,24,13000),true); assert(!c.heater);
  c.tick(14000, valid(44,24,14000),true); assert(c.heater);
  c.tick(60000, valid(44,24,60000),true);
  assert(c.state == State::Cooldown && !c.heater && c.fan);
  c.tick(180000, valid(36,24,180000),true); assert(c.fan);
  c.tick(180001, valid(35,35,180001),true); assert(c.state == State::Idle && !c.fan);
  assert(!c.start(200000, valid(24,24,200000),45,60,true));
  c.tick(210000, valid(24,24,210000),true); assert(c.heater);
  c.tick(213001, valid(24,24,210000),true);
  assert(c.state == State::Fault && !c.heater && c.fan);
  assert(c.start(214000, valid(24,24,214000),45,60,true));
  assert(!c.reset(214000,valid(36,24,214000)));
  assert(c.reset(214000,valid(24,24,214000)));
  c.tick(215000, valid(24,65,215000),true);
  assert(c.state == State::Fault && !c.heater);
  assert(c.reset(216000,valid(24,24,216000)));
  assert(!c.start(0xfffffff0,valid(24,24,0xfffffff0),45,60,true));
  c.tick(0x2710,valid(24,24,0x2710),true); assert(c.heater);
  c.stop(0x3000); assert(!c.heater && c.fan && c.state == State::Cooldown);
  c.tick(0x3001,Sample{},true); assert(c.state == State::Fault);
  Controller rebooted;
  rebooted.tick(0,valid(24,24,0),true);
  assert(rebooted.state == State::Idle && !rebooted.heater && !rebooted.fan);
  std::cout << "Controller scenarios passed\n";
}
