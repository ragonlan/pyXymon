# pyXymon
Library to send message status and graf data to xymon server

# Example

```python
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

# rrd file name will be test.rrd
xg=XymonGraph(test='test', server='xymon1.server.priv', host='pru.server.priv')
xg.insert(51, 'ds0')
#xg.show()
xg.send()
```

```python
# rrd file name become test,side1.rrd
xg=XymonGraph(test='test', server='xymon1.server.priv', host='pru.server.priv', rrdname='side1') 
xg.insert(51, 'ds0')
#xg.show()
xg.send()
```
