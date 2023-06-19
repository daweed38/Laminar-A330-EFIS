#!/usr/bin/env python3
# -*-coding:Utf-8 -*

# System Modules Import
import os
import sys
import time
import threading
import hashlib
import pickle
import socket
import struct
from datetime import datetime

# Sim Open Interface Module Import
from XPUtils import find_xp
from SimOpInt import SimOpInt
from SimOpIntCli import SimOpIntCli
from ObjEncoders import EncoderWorker as worker

configdir = 'Config/A3xxefis/'
configfile = 'A3xxefis.json'
outData = {}
inData = {}
clithread = None
cypherInOld = ''
cypherOutOld = ''
debug = 0

beacon = find_xp()
XPUDPSock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Sim Open Interface Creation
efis = SimOpInt(configdir, configfile, 0)

# Device Management
LEDPACK1 = efis.getDevice('LEDPACK1')
LEDPACK1.start()

# Displays Objects
qnhcptdsp = efis.getObject('displays', 'qnhcptdsp')
qnhfodsp = efis.getObject('displays', 'qnhfodsp')

# Annunciatos Objects
efis0qnhswl = efis.getObject('annunciators', 'efis0qnhswl')
efis1qnhswl = efis.getObject('annunciators', 'efis1qnhswl')

# Switch Light
efis0fdswl = efis.getObject('swlights', 'efis0fdswl')
efis0ilsswl = efis.getObject('swlights', 'efis0ilsswl')
efis0cstrswl = efis.getObject('swlights', 'efis0cstrswl')
efis0wptswl = efis.getObject('swlights', 'efis0wptswl')
efis0vordswl = efis.getObject('swlights', 'efis0vordswl')
efis0ndbswl = efis.getObject('swlights', 'efis0ndbswl')
efis0arptswl = efis.getObject('swlights', 'efis0arptswl')
efis1fdswl = efis.getObject('swlights', 'efis1fdswl')
efis1ilsswl = efis.getObject('swlights', 'efis1ilsswl')
efis1cstrswl = efis.getObject('swlights', 'efis1cstrswl')
efis1wptswl = efis.getObject('swlights', 'efis1wptswl')
efis1vordswl = efis.getObject('swlights', 'efis1vordswl')
efis1ndbswl = efis.getObject('swlights', 'efis1ndbswl')
efis1arptswl = efis.getObject('swlights', 'efis1arptswl')

# Push Buttons
efis0fdsw = efis.getObject('pushbtns', 'efis0fdsw')
efis0ilssw = efis.getObject('pushbtns', 'efis0ilssw')
efis0cstrsw = efis.getObject('pushbtns', 'efis0cstrsw')
efis0wptsw = efis.getObject('pushbtns', 'efis0wptsw')
efis0vordsw = efis.getObject('pushbtns', 'efis0vordsw')
efis0ndbsw = efis.getObject('pushbtns', 'efis0ndbsw')
efis0arptsw = efis.getObject('pushbtns', 'efis0arptsw')
efis0stdsw = efis.getObject('pushbtns', 'efis0stdsw')
efis0stdsw.setValue('push')


efis1fdsw = efis.getObject('pushbtns', 'efis1fdsw')
efis1ilssw = efis.getObject('pushbtns', 'efis1ilssw')
efis1cstrsw = efis.getObject('pushbtns', 'efis1cstrsw')
efis1wptsw = efis.getObject('pushbtns', 'efis1wptsw')
efis1vordsw = efis.getObject('pushbtns', 'efis1vordsw')
efis1ndbsw = efis.getObject('pushbtns', 'efis1ndbsw')
efis1arptsw = efis.getObject('pushbtns', 'efis1arptsw')
efis1stdsw = efis.getObject('pushbtns', 'efis1stdsw')
efis1stdsw.setValue('push')

# VOR / ADF Switches
efis0adfvor1sw = efis.getObject('dblswitches', 'efis0adfvor1sw')
efis0adfvor2sw = efis.getObject('dblswitches', 'efis0adfvor2sw')

efis1adfvor1sw = efis.getObject('dblswitches', 'efis1adfvor1sw')
efis1adfvor2sw = efis.getObject('dblswitches', 'efis1adfvor2sw')

# Rotary Switches
efis0rosersw = efis.getObject('rotswitches', 'efis0rosersw')
efis0zoomrsw = efis.getObject('rotswitches', 'efis0zoomrsw')

efis1rosersw = efis.getObject('rotswitches', 'efis1rosersw')
efis1zoomrsw = efis.getObject('rotswitches', 'efis1zoomrsw')
# Rotary Encoder
qnhcptenc = worker(efis.getObject('rotenc', 'qnhcptenc'))
qnhcptenc.start()
qnhcptdata = qnhcptenc.getValue()

qnhfoenc = worker(efis.getObject('rotenc', 'qnhfoenc'))
qnhfoenc.start()
qnhfodata = qnhfoenc.getValue()

# TCP Client Creation
intname = efis.getConfigOption('INT','intname')
xpladdr = efis.getConfigOption('NETWORK','xpladdr')
xplport = efis.getConfigOption('NETWORK','xplport')

print(f"Interface Name: {intname}. Network Configuration : Connecting XP Server at Addr {xpladdr} on Port : {xplport}")

simopintcli = SimOpIntCli(name=intname, srvaddr=xpladdr, srvport=xplport, debug=0)

thrcli = threading.Thread(target=simopintcli.mainLoop)
thrcli.start()
simopintcli.run()

while True:
    try:
        # Output Management
        cypherIn = hashlib.md5(pickle.dumps(simopintcli.getInData())).hexdigest()
        if cypherIn != cypherInOld:
            # print(f"Input Data : {simopintcli.getInData()}")

            # ----- Displays -----
            if 'displays' in simopintcli.getInData():
                displays = simopintcli.getInData()['displays']
                
                if 'qnhcptdsp' in displays:
                    if displays['qnhcptdsp']['nodeconds']['standard'] == 1:
                        qnhcptdsp.writeDisplay('std ', 0)
                    else:
                        if displays['qnhcptdsp']['nodeconds']['inhghpa'] == 1:
                            qnhcptdsp.writeDisplay(round(displays['qnhcptdsp']['nodeval'] * 33.863889), 0)
                        else:
                            qnhcptdsp.writeDisplay(displays['qnhcptdsp']['nodeval'], 1)

                if 'qnhfodsp' in displays:
                    if displays['qnhfodsp']['nodeconds']['standard'] == 1:
                        qnhfodsp.writeDisplay('std ', 0)
                    else:
                        if displays['qnhfodsp']['nodeconds']['inhghpa'] == 1:
                            qnhfodsp.writeDisplay(round(displays['qnhfodsp']['nodeval'] * 33.863889), 0)
                        else:
                            qnhfodsp.writeDisplay(displays['qnhfodsp']['nodeval'], 1)

            # ----- Annunciatos ----
            if efis0qnhswl.getValue() != 'ON':
                efis0qnhswl.setLightState('ON')

            if efis1qnhswl.getValue() != 'ON':
                efis1qnhswl.setLightState('ON')

            # ----- Switches Lights -----
            if 'swlights' in simopintcli.getInData():
                swlights = simopintcli.getInData()['swlights']

                if 'efis0fdswl' in swlights:
                    if swlights['efis0fdswl']['nodeval'] == 0:
                        efis0fdswl.setLightState('OFF')
                    else:
                        efis0fdswl.setLightState('ON')

                if 'efis0ilsswl' in swlights:
                    if swlights['efis0ilsswl']['nodeval'] == 0:
                        efis0ilsswl.setLightState('OFF')
                    else:
                        efis0ilsswl.setLightState('ON')
                    
                if 'efis0cstrswl' in swlights:
                    if swlights['efis0cstrswl']['nodeval'] == 0:
                        efis0cstrswl.setLightState('OFF')
                    else:
                        efis0cstrswl.setLightState('ON')
                    
                if 'efis0wptswl' in swlights:
                    if swlights['efis0wptswl']['nodeval'] == 0:
                        efis0wptswl.setLightState('OFF')
                    else:
                        efis0wptswl.setLightState('ON')
                    
                if 'efis0vordswl' in swlights:
                    if swlights['efis0vordswl']['nodeval'] == 0:
                        efis0vordswl.setLightState('OFF')
                    else:
                        efis0vordswl.setLightState('ON')
                    
                if 'efis0ndbswl' in swlights:
                    if swlights['efis0ndbswl']['nodeval'] == 0:
                        efis0ndbswl.setLightState('OFF')
                    else:
                        efis0ndbswl.setLightState('ON')
                    
                if 'efis0arptswl' in swlights:
                    if swlights['efis0arptswl']['nodeval'] == 0:
                        efis0arptswl.setLightState('OFF')
                    else:
                        efis0arptswl.setLightState('ON')
                    
                if 'efis1fdswl' in swlights:
                    if swlights['efis1fdswl']['nodeval'] == 0:
                        efis1fdswl.setLightState('OFF')
                    else:
                        efis1fdswl.setLightState('ON')
                    
                if 'efis1ilsswl' in swlights:
                    if swlights['efis1ilsswl']['nodeval'] == 0:
                        efis1ilsswl.setLightState('OFF')
                    else:
                        efis1ilsswl.setLightState('ON')
                    
                if 'efis1cstrswl' in swlights:
                    if swlights['efis1cstrswl']['nodeval'] == 0:
                        efis1cstrswl.setLightState('OFF')
                    else:
                        efis1cstrswl.setLightState('ON')

                if 'efis1wptswl' in swlights:    
                    if swlights['efis1wptswl']['nodeval'] == 0:
                        efis1wptswl.setLightState('OFF')
                    else:
                        efis1wptswl.setLightState('ON')

                if 'efis1vordswl' in swlights:    
                    if swlights['efis1vordswl']['nodeval'] == 0:
                        efis1vordswl.setLightState('OFF')
                    else:
                        efis1vordswl.setLightState('ON')

                if 'efis1ndbswl' in swlights:    
                    if swlights['efis1ndbswl']['nodeval'] == 0:
                        efis1ndbswl.setLightState('OFF')
                    else:
                        efis1ndbswl.setLightState('ON')

                if 'efis1arptswl' in swlights:    
                    if swlights['efis1arptswl']['nodeval'] == 0:
                        efis1arptswl.setLightState('OFF')
                    else:
                        efis1arptswl.setLightState('ON')

            cypherInOld = cypherIn

        # ----- EFIS CPT -----
        # Push Button
        if efis0fdsw.getSwitchState() == 1:
            msg_efis0fdsw = struct.pack('<4sx500s', b'CMND', efis0fdsw.getNode().encode('utf-8'))
            XPUDPSock.sendto(msg_efis0fdsw, (beacon['ip'], beacon['port']))

        if efis0ilssw.getSwitchState() == 1:
            msg_efis0ilssw = struct.pack('<4sx500s', b'CMND', efis0ilssw.getNode().encode('utf-8'))
            XPUDPSock.sendto(msg_efis0ilssw, (beacon['ip'], beacon['port']))

        if efis0cstrsw.getSwitchState() == 1:
            msg_efis0cstrsw = struct.pack('<4sx500s', b'CMND', efis0cstrsw.getNode().encode('utf-8'))
            XPUDPSock.sendto(msg_efis0cstrsw, (beacon['ip'], beacon['port']))

        if efis0wptsw.getSwitchState() == 1:
            msg_efis0wptsw = struct.pack('<4sx500s', b'CMND', efis0wptsw.getNode().encode('utf-8'))
            XPUDPSock.sendto(msg_efis0wptsw, (beacon['ip'], beacon['port']))

        if efis0vordsw.getSwitchState() == 1:
            msg_efis0vordsw = struct.pack('<4sx500s', b'CMND', efis0vordsw.getNode().encode('utf-8'))
            XPUDPSock.sendto(msg_efis0vordsw, (beacon['ip'], beacon['port']))

        if efis0ndbsw.getSwitchState() == 1:
            msg_efis0ndbsw = struct.pack('<4sx500s', b'CMND', efis0ndbsw.getNode().encode('utf-8'))
            XPUDPSock.sendto(msg_efis0ndbsw, (beacon['ip'], beacon['port']))

        if efis0arptsw.getSwitchState() == 1:
            msg_efis0arptsw = struct.pack('<4sx500s', b'CMND', efis0arptsw.getNode().encode('utf-8'))
            XPUDPSock.sendto(msg_efis0arptsw, (beacon['ip'], beacon['port']))

        if efis0stdsw.getSwitchState() == 1:
            if efis0stdsw.getValue() == 'push':
                efis0stdsw.setValue('pull')
                cmdref = efis0stdsw.getNode()['pull']
            else:
                efis0stdsw.setValue('push')
                cmdref = efis0stdsw.getNode()['push']

            msg_efis0stdsw = struct.pack('<4sx500s', b'CMND', cmdref.encode('utf-8'))
            XPUDPSock.sendto(msg_efis0stdsw, (beacon['ip'], beacon['port']))


        # Double Switch
        if efis0adfvor1sw.readSwitch() != None:
            msg_efis0adfvor1sw = struct.pack('<4sxf500s', b'DREF', float(efis0adfvor1sw.getSwitchState()), efis0adfvor1sw.getNode().encode('utf-8'))
            XPUDPSock.sendto(msg_efis0adfvor1sw, (beacon['ip'], beacon['port']))

        if efis0adfvor2sw.readSwitch() != None:
            msg_efis0adfvor2sw = struct.pack('<4sxf500s', b'DREF', float(efis0adfvor2sw.getSwitchState()), efis0adfvor2sw.getNode().encode('utf-8'))
            XPUDPSock.sendto(msg_efis0adfvor2sw, (beacon['ip'], beacon['port']))

        # Rotary Switch
        if efis0rosersw.getSwitchState() is not None:
            if efis0rosersw.getDirection() == 'left':
                # print(f"Rotary Switch efis0rosersw Turn on the Left {efis0rosersw.getNode('left')}")
                msg_efis0rosersw = struct.pack('<4sx500s', b'CMND', efis0rosersw.getNode('left').encode('utf-8'))
                XPUDPSock.sendto(msg_efis0rosersw, (beacon['ip'], beacon['port']))

            elif efis0rosersw.getDirection() == 'right':
                # print(f"Rotary Switch efis0rosersw Turn on the Right {efis0rosersw.getNode('right')}")
                msg_efis0rosersw = struct.pack('<4sx500s', b'CMND', efis0rosersw.getNode('right').encode('utf-8'))
                XPUDPSock.sendto(msg_efis0rosersw, (beacon['ip'], beacon['port']))


        if efis0zoomrsw.getSwitchState() is not None:
            msg_efis0zoomrsw = struct.pack('<4sxf500s', b'DREF', float(efis0zoomrsw.getCurrentPosition()), efis0zoomrsw.getNode('dref').encode('utf-8'))
            XPUDPSock.sendto(msg_efis0zoomrsw, (beacon['ip'], beacon['port']))

        
        # Rotary Encoder
        """
        delta = qnhcptenc.get_delta()
        if delta != 0:
            if delta > 0:
                print(f"DELTA : {delta} => {qnhcptenc.getNode('incr')}")
                msg_qnhcptenc = struct.pack('<4sx500s', b'CMND', qnhcptenc.getNode('incr').encode('utf-8'))
            elif delta < 0:
                print(f"DELTA : {delta} => {qnhcptenc.getNode('decr')}")
                msg_qnhcptenc = struct.pack('<4sx500s', b'CMND', qnhcptenc.getNode('decr').encode('utf-8'))
            XPUDPSock.sendto(msg_qnhcptenc, (beacon['ip'], beacon['port']))

        """

        delta = qnhcptenc.get_delta()
        if delta != 0:
            if delta > 0:
                qnhcptdir = 'incr'
                cmdref = qnhcptenc.encoder.getNode('incr')
            elif delta < 0:
                qnhcptdir = 'decr'
                cmdref = qnhcptenc.encoder.getNode('decr')
        else:
            qnhcptdir = ''

        if qnhcptdir != '':
            msg = struct.pack('<4sx500s', b'CMND', cmdref.encode('utf-8'))
            XPUDPSock.sendto(msg, (beacon['ip'], beacon['port']))


        # ----- EFIS 1 -----
        # Push Button
        if efis1fdsw.getSwitchState() == 1:
            msg_efis1fdsw = struct.pack('<4sx500s', b'CMND', efis1fdsw.getNode().encode('utf-8'))
            XPUDPSock.sendto(msg_efis1fdsw, (beacon['ip'], beacon['port']))

        if efis1ilssw.getSwitchState() == 1:
            msg_efis1ilssw = struct.pack('<4sx500s', b'CMND', efis1ilssw.getNode().encode('utf-8'))
            XPUDPSock.sendto(msg_efis1ilssw, (beacon['ip'], beacon['port']))

        if efis1cstrsw.getSwitchState() == 1:
            msg_efis1cstrsw = struct.pack('<4sx500s', b'CMND', efis1cstrsw.getNode().encode('utf-8'))
            XPUDPSock.sendto(msg_efis1cstrsw, (beacon['ip'], beacon['port']))

        if efis1wptsw.getSwitchState() == 1:
            msg_efis1wptsw = struct.pack('<4sx500s', b'CMND', efis1wptsw.getNode().encode('utf-8'))
            XPUDPSock.sendto(msg_efis1wptsw, (beacon['ip'], beacon['port']))

        if efis1vordsw.getSwitchState() == 1:
            msg_efis1vordsw = struct.pack('<4sx500s', b'CMND', efis1vordsw.getNode().encode('utf-8'))
            XPUDPSock.sendto(msg_efis1vordsw, (beacon['ip'], beacon['port']))

        if efis1ndbsw.getSwitchState() == 1:
            msg_efis1ndbsw = struct.pack('<4sx500s', b'CMND', efis1ndbsw.getNode().encode('utf-8'))
            XPUDPSock.sendto(msg_efis1ndbsw, (beacon['ip'], beacon['port']))

        if efis1arptsw.getSwitchState() == 1:
            msg_efis1arptsw = struct.pack('<4sx500s', b'CMND', efis1arptsw.getNode().encode('utf-8'))
            XPUDPSock.sendto(msg_efis1arptsw, (beacon['ip'], beacon['port']))

        if efis1stdsw.getSwitchState() == 1:
            if efis1stdsw.getValue() == 'push':
                efis1stdsw.setValue('pull')
                cmdref = efis1stdsw.getNode()['pull']
            else:
                efis1stdsw.setValue('push')
                cmdref = efis1stdsw.getNode()['push']

            msg_efis1stdsw = struct.pack('<4sx500s', b'CMND', cmdref.encode('utf-8'))
            XPUDPSock.sendto(msg_efis1stdsw, (beacon['ip'], beacon['port']))

        # Double Switches
        if efis1adfvor1sw.readSwitch() != None:
            msg_efis1adfvor1sw = struct.pack('<4sxf500s', b'DREF', float(efis1adfvor1sw.getSwitchState()), efis1adfvor1sw.getNode().encode('utf-8'))
            XPUDPSock.sendto(msg_efis1adfvor1sw, (beacon['ip'], beacon['port']))

        if efis1adfvor2sw.readSwitch() != None:
            msg_efis1adfvor2sw = struct.pack('<4sxf500s', b'DREF', float(efis1adfvor2sw.getSwitchState()), efis1adfvor2sw.getNode().encode('utf-8'))
            XPUDPSock.sendto(msg_efis1adfvor2sw, (beacon['ip'], beacon['port']))

        # Rotary Switches
        if efis1rosersw.getSwitchState() is not None:
            if efis1rosersw.getDirection() == 'left':
                # print(f"Rotary Switch efis1rosersw Turn on the Left {efis1rosersw.getNode('left')}")
                msg_efis1rosersw = struct.pack('<4sx500s', b'CMND', efis1rosersw.getNode('left').encode('utf-8'))
                XPUDPSock.sendto(msg_efis1rosersw, (beacon['ip'], beacon['port']))

            elif efis1rosersw.getDirection() == 'right':
                # print(f"Rotary Switch efis1rosersw Turn on the Right {efis1rosersw.getNode('right')}")
                msg_efis1rosersw = struct.pack('<4sx500s', b'CMND', efis1rosersw.getNode('right').encode('utf-8'))
                XPUDPSock.sendto(msg_efis1rosersw, (beacon['ip'], beacon['port']))

        if efis1zoomrsw.getSwitchState() is not None:
            msg_efis1zoomrsw = struct.pack('<4sxf500s', b'DREF', float(efis1zoomrsw.getCurrentPosition()), efis1zoomrsw.getNode('dref').encode('utf-8'))
            XPUDPSock.sendto(msg_efis1zoomrsw, (beacon['ip'], beacon['port']))

        # Rotary Encoder
        """
        delta = qnhfoenc.get_delta()
        if delta != 0:
            if delta > 0:
                print(f"DELTA : {delta} => {qnhfoenc.getNode('incr')}")
                msg_qnhfoenc = struct.pack('<4sx500s', b'CMND', qnhfoenc.getNode('incr').encode('utf-8'))
            elif delta < 0:
                print(f"DELTA : {delta} => {qnhfoenc.getNode('decr')}")
                msg_qnhfoenc = struct.pack('<4sx500s', b'CMND', qnhfoenc.getNode('decr').encode('utf-8'))
            XPUDPSock.sendto(msg_qnhfoenc, (beacon['ip'], beacon['port']))
        """

        delta = qnhfoenc.get_delta()
        if delta != 0:
            if delta > 0:
                qnhfodir = 'incr'
                cmdref = qnhfoenc.encoder.getNode('incr')
            elif delta < 0:
                qnhfodir = 'decr'
                cmdref = qnhfoenc.encoder.getNode('decr')
        else:
            qnhfodir = ''

        if qnhfodir != '':
            msg = struct.pack('<4sx500s', b'CMND', cmdref.encode('utf-8'))
            XPUDPSock.sendto(msg, (beacon['ip'], beacon['port']))


        time.sleep(0.005)

    except KeyboardInterrupt as e:
        print(f"Keyboard Interruption {e}")
        break

simopintcli.shutdown()
simopintcli.intsock.close()

LEDPACK1.stop()


