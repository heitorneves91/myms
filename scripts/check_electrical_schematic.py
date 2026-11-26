"""Check net consistency and firmware agreement; not circuit/thermal simulation."""
from collections import Counter
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
d = json.loads((ROOT / 'docs/electrical/connections.json').read_text())
config = (ROOT / 'firmware/include/hardware_config.h').read_text()
for function, symbol in [('sensor','SENSOR_PIN'),('heater','HEATER_PIN'),('fan','FAN_PIN')]:
    pin = int(re.search(rf'constexpr int {symbol} = (\d+);', config)[1])
    assert pin == d['firmware_pins'][function]
endpoints = [pin for pins in d['nets'].values() for pin in pins]
assert all(n == 1 for n in Counter(endpoints).values()), 'Pin assigned to multiple nets'
for rail in ['+24V_BUS', '+5V_EXT', '+5V_BOARD', '+3V3', 'GND', 'SW_HEAT', 'SW_FAN']:
    assert rail in d['nets']
assert 'U2.OUT-' not in d['nets']['GND'] and 'U3.OUT-' not in d['nets']['GND']
assert {'U1.OUT+', 'JP1.1', 'C5.+'} <= set(d['nets']['+5V_EXT'])
assert {'ESP.5V', 'U4.6', 'JP1.2'} <= set(d['nets']['+5V_BOARD'])
assert {'D1.K', 'FAN.+'} <= set(d['nets']['FAN_POS'])
assert {'D1.A', 'FAN.-'} <= set(d['nets']['SW_FAN'])
assert 'TH1.2' in d['nets']['HEATER_POS'] and 'TH1.2' not in d['nets']['FAN_POS']
assert {'TEMP1.2', 'TEMP2.2', 'R1.2', 'ESP.GPIO4'} <= set(d['nets']['DQ_BUS'])
for cap in ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']:
    assert not any(pin.startswith(cap + '.') for pin in d['nets']['DQ_BUS'])
assert set(d['no_connect']) == {'U4.1', 'U4.8'}
for name in ['01-power.svg', '02-control-and-sensors.svg']:
    document = ET.parse(ROOT / 'docs/electrical' / name)
    assert document.getroot().tag.endswith('svg')
print('Firmware pins, net assignments, switched returns, diode polarity, USB jumper and SVG syntax passed')
