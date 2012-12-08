'''
sendir.py - Sends a range of IR codes via lircd to a Yamaha RX-V767 & friends receiver 
            and monitors the CTS line of a serial port looking for a state change (low to high).
            Used to discover which codes will turn on the receiver.


Copyright by Ian Burns <ian.burns138@gmail.com>

sendir is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


*****************************************************************
WARNING: Sending unknown IR codes to your receiver could brick it/
cause it to catch fire/etc. Do this at your own risk. 

Wiring up dodgy cables from the receiver to a serial port may
also blow up you receiver and/or serial port. Do this at your own risk.

I am not responsible for any damage that occurs through the use of this program.

If you don't know what you are doing, don't use it.
***************************************************************** 


Use in conjunction with makeir.py.
Relies on the codes created by makeir.py having been loaded by lircd.
Requires pyserial to be installed (http://pyserial.sourceforge.net/)

Hardware:
You will need an IR blaster to send the codes to the receiver.
You will need a cable to connect either the trigger output from the receiver, 
or the HDMI +5v line to the CTS input on the serial port.

Invocation:
python sendir.py <start> <end> <serport>
eg python sendir.py 0x0000 0x10000 /dev/ttyUSB0

Sends each code from start to end (ie TESTxxxx) using irsend, and 
halts execution when a CTS low to high transition occurs.
Will print "CTS change detected at TESTxxxx" when this occurs.

You can restart to continue the search by changing the start parameter to 1+ 
the one that caused the receiver to turn on. 
'''

import os
import time
import sys
import serial

start = int(sys.argv[1], 16)
end = int(sys.argv[2], 16)
serport = sys.argv[3]

ser = serial.Serial(port=serport)
if (ser.getCTS()):
	print "CTS is already high"
	sys.exit(1)

print "testing from 0x%04x to 0x%04x" % (start, end)
raw_input("hit enter to start")


for i in range(start, end):
	cmd = "irsend SEND_ONCE test TEST%04X" % (i)
	print cmd
	os.system(cmd)
	time.sleep(1.0)
	if (ser.getCTS()):
		print "CTS change detected at TEST%04X" % (i)
		sys.exit(0)

print "done, no CTS change detected"

