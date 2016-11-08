#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyXymon import Xymon,XymonGraph
import sys

x = Xymon(test='test', server='xymon1.acens.priv', host='pru.server.priv')
vars = x.LoadConf('/etc/xymon/xymonclient.cfg');
x.green()
x.say("test text")
x.colorLine('yellow',"line status")
x.send()


xg=XymonGraph(test='test', server='xymon1.server.priv', host='pru.server.priv')
xg.insert(51, 'ds0')
#xg.show()
xg.send()
