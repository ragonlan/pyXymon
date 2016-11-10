#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyXymon import Xymon, XymonGraph
import sys

x = Xymon(test='test', server='xymon1.acens.priv',
          host='pru.server.priv', debug=False)
x.green()
x.say("test text")
#vars = x.LoadConf('/etc/xymon/xymonclient.cfg');
x.colorLine('yellow', "Xymon client home is " + x.cfgvar['XYMONCLIENTHOME'])
x.red()
x.send()


xg = XymonGraph(test='test', server='xymon1.server.priv',
                host='pru.server.priv', rrdname='/dev/sda1')
xg.insert(51, 'ds0')
out = xg.show()
print(">>" + out + "<<")
xg.send()
