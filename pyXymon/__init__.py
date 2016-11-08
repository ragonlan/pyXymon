#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
from datetime import datetime, date, time
from subprocess import Popen, PIPE
import pprint
import logging, sys
FORMAT = '%(asctime)-15s %(name)s [%(process)d] %(levelname)s: %(message)s'
#logging.basicConfig(stream=sys.stderr, level=logging.INFO, format=FORMAT)
pp = pprint.PrettyPrinter(indent=2)

__version__ = '0.0.1'

color = {
        'blue'  : 5,
        'clear' : 0,
        'green' : 1,
        'purple': 2,
        'yellow': 3,
        'red'   : 4,
        }

validDataType = ('GAUGE', 'COUNTER', 'DERIVE', 'DCOUNTER', 'DDERIVE', 'ABSOLUTE')

class Xymon(object):
    """docstring for ."""
    def __init__(self, type='status', server=None, port=1984, host=None, color='clear', test='test', title=None, text='', lifetime='30', debug=False):
        """
           type : type of message sended to display. default "status"
           server : hostname or IP message is sended to. Display server.
           port : display server port. Default '1984'
           host : hostname them massega is refered to. default machine 'CLIENTNAME'
           color: message severity color. Default 'clear'. options: blue, clear, green, purple, yellow, red
           title : message title
           lifetime: period of time a message has before become purple.
           debug : debug
         """
        if debug is False:
            logging.basicConfig(stream=sys.stderr, level=logging.INFO, format=FORMAT)
        else:
            logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format=FORMAT)

        self.cfgvar = Xymon.LoadConf()
        if server is None:
            server = cfgvar['XYMSRV']
        if host is None:
            host = cfgvar['CLIENTHOSTNAME']
        self.type     = type
        self.server   = server
        self.port     = port
        self.host     = host
        self.color    = color
        self.test     = test
        self.title    = title
        self.text     = text
        self.lifetime = lifetime

    @classmethod
    def guessCfgFile(self):
        """guess witch is the configuration file"""
        cfgfiles = ('/etc/xymon/xymonclient.cfg', '/etc/xymon/xymonserver.cfg','/etc/hobbit/xymonclient.cfg','/etc/hobbit/hobbitclient.cfg')
        for f in cfgfiles:
            if os.path.exists(f):
                return f

    @classmethod
    def LoadConf(self, file=None, vars={}):
        """ Return a dictionary with all variables defined in xymon configuration """
        if file is None:
            file = Xymon.guessCfgFile()
            logging.debug('configfile detected: {0}'.format(file))
        varpattern = re.compile('\$(\w+)(.*)')  # Only varible occurrence at the begining

        for line in open(file, 'r').readlines():
            li = line.strip().partition('#')[0]
            if li:
                parts = li.split('=')
                if len(parts) == 2:
                    varname = parts[0]
                    content = parts[1].strip("\" \t")
                    try:
                        vars[varname] = re.sub(r'\$(\w+)\b', lambda m:(vars[m.group(1)]), content)
                        logging.debug("{0} {1} <<<{2}>>>".format(file, varname, vars[varname]))
                    except KeyError:
                        pass  #inner variable reference is not defined previusly.
                elif parts[0].startswith('include'):
                    parts[0] = parts[0].strip('include ')
                    logging.debug(">>>>{0}".format(parts[0]))
                    vars.update(self.LoadConf( parts[0], vars ))
                    logging.debug("<<<<{0}".format(parts[0]))
        # Second pass to substitue variables referenced
        return vars

    def maxColor(self, color1, color2):
        """ Return most critical color"""
        if not color1 in color or not color2 in color:
            return 0
        if color[color2] > color[color1]:
            return color2
        else:
            return color1
    def clear(self):
        """set color to clear if is more critical than current color"""
        return self.addColor('cleara')

    def green(self):
        """set color to green if is more critical than current color"""
        return self.addColor('green')

    def yellow(self):
        """set color to yellow if is more critical than current color"""
        return self.addColor('yellow')

    def red(self):
        """set color to red if is more critical than current color"""
        return self.addColor('red')
    def addColor(self, color):
        """set colro to 'color' if is more critical than current color"""
        self.color = self.maxColor(self.color, color)

    def colorPrint(self, color, text):
        """add text to message and set 'color' as current color if is more critical"""
        self.text += text;
        return self.addColor(color)

    def colorLine(self, color, text):
        """add color gif in the same line than text and set 'color' as current color if is more critical"""
        self.text += '&' + color + ' ' + text;
        return self.addColor(color)

    def printLine(self, text):
        """add text to message"""
        self.text += text;

    def say(self, text):
        """add text to message witch carrier return"""
        self.text += text + "\n";

    def color(self):
        """return current color"""
        #print(self.color)
        return(self.color)

    def send(self):
        """send message status to display server"""
        date = datetime.now()
        datef = date.strftime("%A %d. %B %Y %H:%M:%S")
        if self.title is None:
            if self.color == 'green':
                self.title = 'test OK'
            else:
                self.title = 'test NOT ok'
        self.title = datef +' - '+ self.title
        if self.type == 'status':
            report = '{0}+{1} {2}.{3} {4} {5} \n {6}'.format(self.type , self.lifetime , self.host , self.test, self.color, self.title, self.text)
        else:
            report = '{0} {1}.{2} {3} \n {4}'.format(self.type , self.host , self.test, self.title, self.text)

        if os.environ.get('XYMON'):
            p = Popen([self.cfgvar['BB'], self.cfgvar['BBDISP'], '@'], stdout=PIPE, stdin=PIPE)
            p.communicate(report)
            logging.debug('{0} {1} {2}'.format(self.cfgvar['BB'], self.cfgvar['BBDISP'], report))
        else:
            logging.info('{0} {1} {2}'.format(self.cfgvar['BB'], self.cfgvar['BBDISP'], report))

class XymonGraph(Xymon):
    def __init__(self, server=None, port=1984, host=None, test='test', rrdname=None, datatype='GAUGE', min='0', max='U', heartbeat=600):
        """
        server : hostname or IP message is sended to. Display server.
        port : display server port. Default '1984'
        host : hostname them massega is refered to. default machine 'CLIENTNAME'
        test : test name
        rrdname : rrdname is addaded to test in rrd name: test,rrdname.rrd
        datatype : define type of data store in rrd
        min : min value for data
        max : max value for data
        heartbeat : max time betwen data
        """
        self.cfgvar = Xymon.LoadConf()
        if server is None:
            server = cfgvar['XYMSRV']
        if host is None:
            host = cfgvar['CLIENTHOSTNAME']

        self.server   = server
        self.port     = port
        self.host     = host
        self.test     = test.replace('/','_')
        self.datatype = datatype
        self.min      = min
        self.max      = max
        self.heartbeat = heartbeat
        if rrdname is not None:
            self.rrdname = rrdname.replace('/','_')
        else:
            self.rrdname = None
        if self.datatype not in validDataType:
            raise ValueError('Invalid datatype parameter')
        self.data = dict()

    def insert(self, dataval, dataname='ds0', datatype='GAUGE'):
        if datatype not in validDataType:
            raise ValueError('invalid datatype parameter "{0}"'.format(datatype))
        self.data[self.rrdname] = dict()
        self.data[self.rrdname][dataname] = [datatype, dataval]
        logging.debug('rrdname={0}:dataname={1} dataval={2} datatype={3}'.format(self.datatype, dataname, dataval, datatype))

    def show(self):
        output = 'data {0}.trends\n'.format(self.host)
        if self.rrdname is None:
            output += '[{0}.rrd]\n'.format(self.test)
        else:
            output += '[{0},{1}.rrd]\n'.format(self.test, self.rrdname)

        for rrdname, dataDict in self.data.iteritems():
            for dataname, dataArray in dataDict.iteritems():
                output += 'DS:{0}:{1}:{2}:{3}:{4}\t{5}\n'.format(dataname, dataArray[0], self.heartbeat, self.min, self.max,  dataArray[1] )
        logging.debug(output)
        #print output
        return output

    def send(self):
        report = self.show()
        if os.environ.get('XYMON'):
            p = Popen([self.cfgvar['BB'], self.cfgvar['BBDISP'], '@'], stdout=PIPE, stdin=PIPE)
            p.communicate(report.encode('utf8'))
            logging.debug('{0} {1} {2}'.format(self.cfgvar['BB'], self.cfgvar['BBDISP'], report.encode('utf8')))
        else:
            logging.info('{0} {1} {2}'.format(self.cfgvar['BB'], self.cfgvar['BBDISP'], report.encode('utf8')))
