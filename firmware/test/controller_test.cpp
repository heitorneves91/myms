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

  Controller manual;
  assert(manual.manualFan(0,false));
  assert(manual.manualHeat(0,valid(24,24,0),45,false));
  assert(manual.state == State::Idle && !manual.fan && !manual.heater);
  assert(!manual.manualFan(0,true));
  manual.tick(100000,Sample{},true); // Fan-only testing needs no temperature sensors.
  assert(manual.state == State::ManualFan && manual.fan && !manual.heater);
  assert(manual.remaining(100000)==0);
  assert(manual.manualHeat(100000,Sample{},45,true));
  assert(manual.manualHeat(100000,valid(24,24,100000),56,true));
  assert(manual.state == State::ManualFan && !manual.heater);
  manual.stop(100001);
  assert(manual.state == State::Idle && !manual.fan);
  assert(!manual.manualHeat(200000,valid(24,24,200000),45,true));
  manual.tick(209999,valid(24,24,209999),true);
  assert(manual.state == State::ManualPrerun && !manual.heater && manual.fan);
  manual.tick(210000,valid(24,24,210000),true);
  assert(manual.state == State::ManualHeat && manual.heater && manual.fan);
  manual.tick(211000,valid(46,24,211000),true); assert(!manual.heater);
  manual.tick(212000,valid(44,24,212000),true); assert(manual.heater);
  manual.tick(90200000,valid(24,24,90200000),true); // No cycle timer in manual mode.
  assert(manual.state == State::ManualHeat && manual.heater && manual.remaining(90200000)==0);
  assert(manual.manualHeat(90200000,valid(24,24,90200000),45,true)); // Cannot restart/bypass pre-run.
  assert(!manual.manualFan(90200000,true));
  assert(manual.state == State::Cooldown && !manual.heater && manual.fan);
  assert(!manual.manualFan(90200001,true));
  manual.stop(90200002);
  assert(manual.state == State::Cooldown && manual.fan); // Repeated commands cannot bypass cooldown.
  manual.tick(90320000,valid(36,24,90320000),true); assert(manual.fan);
  manual.tick(90320001,valid(35,35,90320001),true); assert(manual.state == State::Idle && !manual.fan);
  assert(!manual.manualFan(90330000,true));
  assert(!manual.manualHeat(90330001,valid(24,24,90330001),45,true)); // Upgrade fan-only to heat.
  manual.tick(90340001,valid(24,24,90340001),true); assert(manual.heater);
  manual.tick(90343002,valid(24,24,90340001),true);
  assert(manual.state == State::Fault && !manual.heater && manual.fan);
  assert(manual.manualFan(90343003,true));
  assert(manual.manualHeat(90343003,valid(24,24,90343003),45,true));
  assert(manual.reset(90344000,valid(24,24,90344000)));
  assert(!manual.manualHeat(0xfffffff0,valid(24,24,0xfffffff0),45,true));
  manual.tick(0x2700,valid(24,24,0x2700),true); assert(manual.state == State::ManualHeat && manual.heater);
  manual.tick(0x2800,valid(65,24,0x2800),true);
  assert(manual.state == State::Fault && !manual.heater && manual.fan);
  assert(manual.reset(0x2900,valid(24,24,0x2900)));
  assert(!manual.manualFan(0x3000,true));
  manual.tick(0x3001,valid(24,65,0x3001),true);
  assert(manual.state == State::Fault && !manual.heater && manual.fan);

  Controller test;
  assert(test.testHeat(0,Sample{},false));
  assert(test.state == State::Idle && !test.heater && !test.fan);
  assert(!test.testHeat(0,Sample{},true));
  test.tick(9999,Sample{},true);
  assert(test.state == State::TestPrerun && !test.heater && test.fan);
  assert(test.testHeat(9999,Sample{},true)); // Repeated requests cannot restart the clock.
  test.tick(10000,Sample{},true);
  assert(test.state == State::HeaterTest && test.heater && test.fan);
  assert(test.testRemaining(10000)==20);
  test.tick(14999,Sample{},true); assert(test.heater);
  test.tick(15000,Sample{},true); assert(test.heater && test.testRemaining(15000)==15);
  test.tick(29999,Sample{},true); assert(test.heater);
  test.tick(30000,Sample{},true);
  assert(test.state == State::TestCooldown && !test.heater && test.fan);
  assert(test.testHeat(30001,Sample{},true));
  assert(test.manualHeat(30001,Sample{},45,true));
  assert(!test.manualFan(30001,true));
  test.stop(30002);
  test.tick(149999,Sample{},true); assert(test.state == State::TestCooldown && test.fan);
  test.tick(150000,Sample{},true);
  assert(test.state == State::ManualFan && !test.heater && test.fan);
  test.stop(150001); assert(test.state == State::Idle && !test.fan);
  assert(!test.testHeat(200000,Sample{},true));
  test.tick(210000,Sample{},true); assert(test.heater);
  test.stop(210001); assert(test.state == State::TestCooldown && !test.heater && test.fan);
  test.tick(330001,valid(40,24,330001),true); assert(test.state == State::TestCooldown);
  test.tick(330002,valid(35,24,330002),true); assert(test.state == State::ManualFan);
  test.stop(330003);
  assert(!test.testHeat(0xfffffff0,Sample{},true));
  test.tick(0x2700,Sample{},true); assert(test.heater);
  test.tick(0x751f,Sample{},true); assert(test.heater);
  test.tick(0x7520,Sample{},true); assert(!test.heater && test.state == State::TestCooldown);
  Controller wrapPulse;
  assert(!wrapPulse.testHeat(0xffffd8e0,Sample{},true));
  wrapPulse.tick(0xfffffff0,Sample{},true); assert(wrapPulse.heater);
  wrapPulse.tick(19983,Sample{},true); assert(wrapPulse.heater);
  wrapPulse.tick(19984,Sample{},true); assert(!wrapPulse.heater);
  Controller hotTest;
  Sample partialHot = valid(65,NAN,0); partialHot.valid=false;
  assert(hotTest.testHeat(0,partialHot,true));
  assert(!hotTest.testHeat(0,Sample{},true));
  hotTest.tick(10000,Sample{},true); assert(hotTest.heater);
  hotTest.tick(10001,partialHot,true);
  assert(hotTest.state == State::Fault && !hotTest.heater && hotTest.fan);
  std::cout << "Controller scenarios passed\n";
}
