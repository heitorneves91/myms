"""Generate the two module-level MYMS electrical schematic sheets as SVG.

SVG is the editable/vector source artifact. Component and net information is
also supplied in docs/electrical/connections.json; this is not a PCB netlist.
"""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/electrical'
OUT.mkdir(parents=True, exist_ok=True)
INK, POWER, GROUND, SIGNAL, OPTIONAL = '#203640', '#b63832', '#245d83', '#12785d', '#9a6514'

class Sheet:
    def __init__(self, title, subtitle, height=1420):
        self.height = height
        self.items = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="{height}" viewBox="0 0 1800 {height}">',
                      '<rect width="100%" height="100%" fill="white"/>',
                      '<style>text{font-family:DejaVu Sans,Arial,sans-serif;fill:#203640} .wire{fill:none;stroke-width:3;stroke-linecap:round;stroke-linejoin:round}</style>']
        self.text(55, 52, title, 31, weight='bold')
        self.text(55, 88, subtitle, 19)
        self.line([(55, 110), (1745, 110)], '#b7c6cc', 1)

    def text(self, x, y, content, size=20, color=INK, weight='normal', anchor='start'):
        self.items.append(f'<text x="{x}" y="{y}" font-size="{size}" style="fill:{color}" font-weight="{weight}" text-anchor="{anchor}">{escape(content)}</text>')

    def line(self, points, color=INK, width=3, dashed=False):
        p = ' '.join(f'{x},{y}' for x, y in points)
        self.items.append(f'<polyline class="wire" points="{p}" stroke="{color}" stroke-width="{width}"' + (' stroke-dasharray="9 7"' if dashed else '') + '/>')

    def dot(self, x, y, color=INK):
        self.items.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{color}"/>')

    def box(self, x, y, w, h, title='', fill='#f3f7f8', color=INK, dashed=False):
        self.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" stroke="{color}" stroke-width="2"' + (' stroke-dasharray="9 7"' if dashed else '') + '/>')
        if title:
            self.text(x + w / 2, y + 32, title, 20 if len(title) > 14 else 23, color, 'bold', 'middle')

    def ground(self, x, y):
        self.line([(x, y), (x, y+12)], GROUND)
        for yy, half in ((12, 17), (20, 11), (28, 5)):
            self.line([(x-half, y+yy), (x+half, y+yy)], GROUND)
        self.text(x, y+52, 'GND', 16, GROUND, anchor='middle')

    def resistor(self, x, y, ref, value, vertical=True, color=INK):
        if vertical:
            self.line([(x, y-40), (x, y-22)], color)
            self.box(x-9, y-22, 18, 44, fill='white', color=color)
            self.line([(x, y+22), (x, y+40)], color)
            self.text(x+18, y-5, ref, 18, color)
            self.text(x+18, y+19, value, 18, color)
        else:
            self.line([(x-52, y), (x-28, y)], color)
            self.box(x-28, y-10, 56, 20, fill='white', color=color)
            self.line([(x+28, y), (x+52, y)], color)
            self.text(x, y-22, ref + ' ' + value, 18, color, anchor='middle')

    def capacitor(self, x, y, ref, value, rating, polarized=False, color=INK):
        self.line([(x, y-40), (x, y-7)], color)
        self.line([(x-16, y-7), (x+16, y-7)], color)
        self.line([(x-16, y+7), (x+16, y+7)], color)
        self.line([(x, y+7), (x, y+40)], color)
        self.text(x+24, y-13, ref + ' ' + value, 17, color)
        self.text(x+24, y+12, rating, 16, color)
        if polarized:
            self.text(x-28, y-14, '+', 20, color)

    def port(self, x, y, name, color=SIGNAL, end='right'):
        dx = 16 if end == 'right' else -16
        self.line([(x-dx, y-7), (x, y), (x-dx, y+7)], color)
        self.text(x, y-15, name, 18, color, anchor='middle')

    def save(self, name):
        self.text(55, self.height-24, 'MYMS / Rev A / 2026-11-26 — Proposal; verify actual module terminals, ratings and startup behavior. Not a PCB layout.', 16)
        self.items.append('</svg>')
        (OUT / name).write_text('\n'.join(self.items)+'\n')


def fuse(s, x, y, label):
    s.line([(x-55,y),(x-34,y)],POWER)
    s.box(x-34,y-16,68,32,fill='white',color=POWER)
    s.line([(x-25,y),(x+25,y)],POWER,2)
    s.line([(x+34,y),(x+55,y)],POWER)
    s.text(x,y-32,label,18,POWER,anchor='middle')
    s.text(x,y+45,'DC rating: TBD',16,OPTIONAL,anchor='middle')

s = Sheet('MYMS — Electrical schematic / 1 of 2', '24 V power distribution, existing LM2596 module, independent heater and fan switching')
s.box(55,170,285,170,'PSU1: existing supply')
s.text(197,240,'24 V DC / 10 A',22,anchor='middle')
s.text(197,275,'Mains stays outside',18,anchor='middle')
s.text(325,218,'+',24,POWER)
s.text(325,308,'−',24,GROUND)
s.line([(340,210),(395,210)],POWER)
fuse(s,450,210,'F0: main fuse')
s.line([(505,210),(555,210)],POWER)
s.items.append('<circle cx="555" cy="210" r="5" fill="white" stroke="#b63832" stroke-width="2"/><circle cx="625" cy="210" r="5" fill="white" stroke="#b63832" stroke-width="2"/>')
s.line([(560,205),(615,183)],POWER)
s.text(590,164,'S1: DC switch',18,POWER,anchor='middle')
s.line([(625,210),(710,210),(710,1070)],POWER)
s.text(710,175,'+24V_BUS',21,POWER,anchor='middle')
s.line([(340,300),(410,300),(410,365)],GROUND)
s.ground(410,365)
s.text(55,410,'GND STAR',21,GROUND,weight='bold')
s.text(55,442,'Separate heavy load returns',18)
s.text(55,470,'from ESP/sensor ground wires.',18)
# Optional input reservoir is across unswitched load return, never across a switched minus.
s.line([(710,250),(560,250),(560,330)],OPTIONAL)
s.dot(710,250,POWER)
s.capacitor(560,370,'C6','100 µF','50 V / optional',True,OPTIONAL)
s.line([(560,410),(560,430)],GROUND)
s.ground(560,430)

def module(y, name, trigger):
    s.box(1120,y-50,300,235,name)
    for dy, label, color in ((0,'VIN+',POWER),(65,'VIN−',GROUND),(125,'TRIG/PWM',SIGNAL),(170,'signal GND',GROUND)):
        s.text(1135,y+dy+7,label,18,color)
    s.text(1405,y+7,'OUT+',18,POWER,anchor='end')
    s.text(1405,y+72,'OUT−',18,INK,anchor='end')
    s.line([(1030,y+65),(1120,y+65)],GROUND)
    s.line([(1030,y+65),(1030,y+170),(1120,y+170)],GROUND)
    s.dot(1030,y+170,GROUND)
    s.line([(1030,y+170),(1030,y+194)],GROUND)
    s.ground(1030,y+194)
    s.line([(950,y+125),(1020,y+125)],SIGNAL)
    s.items.append(f'<path d="M 1020 {y+125} Q 1030 {y+110} 1040 {y+125}" fill="none" stroke="{SIGNAL}" stroke-width="3"/>')
    s.line([(1040,y+125),(1120,y+125)],SIGNAL)
    s.port(950,y+125,trigger,end='left')
    s.line([(1420,y),(1540,y)],POWER)
    s.line([(1420,y+65),(1540,y+65)],INK)

# Heater branch. TH1 cuts only heater positive, leaving fan and logic powered.
s.dot(710,340,POWER)
s.line([(710,340),(805,340)],POWER)
s.box(805,317,200,46,fill='#fff7e9',color=OPTIONAL,dashed=True)
s.text(905,347,'TH1: NC cutout',18,OPTIONAL,anchor='middle')
s.text(905,293,'Trip / DC current rating: deferred',16,OPTIONAL,anchor='middle')
s.line([(1005,340),(1120,340)],POWER)
module(340,'U2: heater MOSFET','HEAT_TRIG')
s.box(1540,310,210,120,'HEATER',fill='#fff1ee')
s.text(1645,383,'24 V / 120 W',20,anchor='middle')
s.text(1645,410,'5 A nominal',17,anchor='middle')
s.text(1510,326,'+',18,POWER)
s.text(1480,450,'SW_HEAT',16,anchor='middle')
# Fan branch.
s.dot(710,725,POWER)
s.line([(710,725),(790,725)],POWER)
fuse(s,845,725,'F2: fan branch')
s.line([(900,725),(1120,725)],POWER)
module(725,'U3: fan MOSFET','FAN_TRIG')
s.box(1540,695,210,120,'FAN',fill='#eef7fa')
s.text(1645,768,'24 V',22,anchor='middle')
s.text(1645,795,'Current: verify label',16,anchor='middle')
s.text(1510,711,'+',18,POWER)
s.text(1480,818,'SW_FAN',16,anchor='middle')
# D1: cathode stripe at the positive fan terminal, anode to switched minus.
s.dot(1480,725,POWER);s.dot(1480,790,INK)
s.line([(1480,725),(1480,745)],INK)
s.line([(1466,745),(1494,745)],INK)
s.items.append('<polygon points="1480,748 1466,773 1494,773" fill="white" stroke="#203640" stroke-width="2"/>')
s.line([(1480,773),(1480,790)],INK)
s.text(1448,845,'D1: fan turn-off clamp',17,OPTIONAL)
s.text(1448,870,'SB560 candidate: 5 A / 60 V',16,OPTIONAL)
s.text(1448,894,'Stripe/cathode → fan +',16,OPTIONAL)
s.text(1448,918,'Verify fan datasheet / current.',16,OPTIONAL)
# Logic branch and power selection.
s.dot(710,1070,POWER)
s.line([(710,1070),(790,1070)],POWER)
fuse(s,845,1070,'F1: logic branch')
s.line([(900,1070),(1120,1070)],POWER)
s.box(1120,1020,300,170,'U1: LM2596 module')
s.text(1135,1077,'IN+',18,POWER);s.text(1135,1150,'IN−',18,GROUND)
s.text(1405,1077,'OUT+',18,POWER,anchor='end');s.text(1405,1150,'OUT−',18,GROUND,anchor='end')
s.text(1270,1110,'Set / measure 5.0 V',19,anchor='middle')
s.line([(1030,1143),(1120,1143)],GROUND);s.ground(1030,1143)
s.line([(1420,1143),(1450,1143)],GROUND);s.ground(1450,1143)
s.line([(1420,1070),(1575,1070)],POWER)
s.text(1485,1048,'+5V_EXT',18,POWER,anchor='middle')
s.items.append('<circle cx="1575" cy="1070" r="5" fill="white" stroke="#b63832" stroke-width="2"/><circle cx="1640" cy="1070" r="5" fill="white" stroke="#b63832" stroke-width="2"/>')
s.line([(1581,1065),(1630,1049)],POWER)
s.text(1605,1020,'JP1: removable link',17,POWER,anchor='middle')
s.line([(1640,1070),(1730,1070)],POWER)
s.port(1730,1070,'+5V_BOARD',POWER)
s.line([(1490,1070),(1490,1130)],OPTIONAL);s.dot(1490,1070,POWER)
s.capacitor(1490,1170,'C5','220 µF','16 V / optional',True,OPTIONAL)
s.ground(1490,1210)
s.text(55,1110,'Three branches share GND.',20,GROUND,weight='bold')
s.text(55,1145,'Never connect SW_HEAT or SW_FAN',18)
s.text(55,1173,'directly to GND: that bypasses switching.',18)
s.box(55,1290,1690,75,fill='#fff7e9',color=OPTIONAL)
s.text(75,1318,'JP1 OPEN before connecting a powered USB cable. USB can then power ESP + driver; 24 V still powers the loads.',19,OPTIONAL)
s.text(75,1346,'Fuse values depend on fan/PTC inrush and wire/connector ratings. TH1 selection remains deferred; no bypass is specified.',18,OPTIONAL)
s.save('01-power.svg')

s = Sheet('MYMS — Electrical schematic / 2 of 2', 'GPIO4 sensors / GPIO5 heater / GPIO6 fan — 3.3 V sensor bus; proposed 5 V trigger drive', height=1380)
s.box(80,270,300,615,'ESP32-C3 SuperMini')
s.text(230,332,'USB-C development board',17,anchor='middle')
s.line([(230,220),(230,270)],POWER);s.port(230,220,'+5V_BOARD',POWER)
s.text(240,264,'5V pin',17,POWER)
s.line([(230,885),(230,915)],GROUND);s.ground(230,915)
for y,label in ((385,'GPIO4 / data'),(485,'3V3'),(665,'GPIO5 / heat'),(860,'GPIO6 / fan')):
    s.text(365,y+7,label,19,anchor='end')
s.line([(380,485),(500,485)],POWER);s.port(500,485,'+3V3',POWER)
# Sensor bus: the second sensor is in parallel, not a second pull-up bus.
s.line([(380,385),(620,385),(620,570),(1380,570)],SIGNAL)
s.text(640,598,'DQ_BUS — no capacitor from DQ to GND',18,SIGNAL)
s.line([(900,220),(1680,220)],POWER);s.port(900,220,'+3V3',POWER,end='left')
s.line([(900,220),(900,350)],POWER);s.dot(900,220,POWER)
s.resistor(900,390,'R1','4.7 kΩ',color=SIGNAL)
s.line([(900,430),(900,570)],SIGNAL);s.dot(900,570,SIGNAL)
for index,x in ((1,1040),(2,1420)):
    s.box(x,280,220,180,f'TEMP{index}: DS18B20')
    s.text(x+110,330,'TO-92 / 3-wire power',16,anchor='middle')
    s.text(x+12,387,'DQ (2)',18,SIGNAL)
    s.text(x+110,356,'VDD (3)',18,POWER,anchor='middle')
    s.text(x+110,440,'GND (1)',18,GROUND,anchor='middle')
    s.line([(x+110,220),(x+110,280)],POWER);s.dot(x+110,220,POWER)
    s.line([(x-40,570),(x-40,385),(x,385)],SIGNAL);s.dot(x-40,570,SIGNAL)
    s.line([(x+110,460),(x+110,480)],GROUND);s.ground(x+110,480)
    # Local supply bypass: place beside each sensor, not on its data line.
    cx=x+245
    s.line([(cx,220),(cx,295)],POWER);s.dot(cx,220,POWER)
    s.capacitor(cx,335,'C'+str(index),'100 nF','10 V+')
    s.ground(cx,375)
# GPIO default-off bias, also useful when verified modules permit direct drive.
for y,ref,net in ((665,'R2','GPIO_HEAT'),(860,'R3','GPIO_FAN')):
    s.line([(380,y),(520,y)],SIGNAL);s.port(520,y,net)
    s.dot(465,y,SIGNAL)
    s.line([(465,y),(465,y+30)],SIGNAL)
    s.resistor(465,y+70,ref,'10 kΩ')
    s.ground(465,y+110)
# Non-inverting 5 V buffer. Pinout is for TC4427A 8-pin PDIP/SOIC/MSOP.
s.box(790,700,360,345,'U4: TC4427A',fill='#fff7e9',color=OPTIONAL,dashed=True)
s.text(970,765,'PROPOSED 5 V gate/trigger buffer',17,OPTIONAL,anchor='middle')
s.text(970,798,'Non-inverting / 8-pin package',17,anchor='middle')
s.text(805,857,'2: IN A',18);s.text(805,957,'4: IN B',18)
s.text(1135,857,'7: OUT A',18,anchor='end');s.text(1135,957,'5: OUT B',18,anchor='end')
s.line([(970,650),(970,700)],POWER);s.port(970,650,'+5V_BOARD',POWER)
s.text(990,687,'6: VDD',17,POWER)
s.line([(970,1045),(970,1075)],GROUND);s.ground(970,1075)
s.text(990,1060,'3: GND',17,GROUND)
s.text(970,1025,'1, 8: NC (leave unconnected)',16,anchor='middle')
for y,net in ((850,'GPIO_HEAT'),(950,'GPIO_FAN')):
    s.line([(680,y),(790,y)],SIGNAL);s.port(680,y,net,end='left')
for y,ref,net,pull in ((850,'R4','HEAT_TRIG','R6'),(950,'R5','FAN_TRIG','R7')):
    s.line([(1150,y),(1208,y)],SIGNAL)
    s.resistor(1260,y,ref,'100 Ω',False,SIGNAL)
    end=1720 if y==850 else 1520
    s.line([(1312,y),(end,y)],SIGNAL);s.port(end,y,net)
    px=1680 if y==850 else 1430
    s.dot(px,y,SIGNAL);s.line([(px,y),(px,y+28)],SIGNAL)
    s.resistor(px,y+68,pull,'10 kΩ')
    s.ground(px,y+108)
# Driver decoupling, both directly across its local 5 V and ground pins.
s.line([(1190,660),(1510,660)],POWER);s.port(1190,660,'+5V_BOARD',POWER,end='left')
for x,ref,val in ((1240,'C3','100 nF'),(1470,'C4','4.7 µF')):
    s.line([(x,660),(x,680)],POWER);s.dot(x,660,POWER)
    s.capacitor(x,720,ref,val,'≥10 V ceramic')
    s.ground(x,760)
s.box(55,1170,1690,135,fill='#f3f7f8')
s.text(75,1200,'Same net labels are electrically connected. All GND symbols share PSU negative; GPIO pins never receive 5 V.',19)
s.text(75,1230,'U4 is a proposed addition: AOD4184A low on-resistance is specified at 4.5/10 V gate drive, not at ESP32 3.3 V.',18)
s.text(75,1260,'Direct GPIO → module TRIG is an alternative only after verifying the exact board at 3.3 V, load current and startup.',18)
s.text(75,1290,'Sensor orientation: flat marked face toward you, legs down → left GND, middle DQ, right VDD. Confirm your actual package.',18)
s.save('02-control-and-sensors.svg')
print('Generated two electrical schematic SVG sheets')
