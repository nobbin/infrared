'''
makeir.py - Generates a lirc remote definition for range of IR codes for testing Yamaha RX-V767 & friends receivers


Copyright by Ian Burns <ian.burns138@gmail.com>

makeir is free software; you can redistribute it and/or modify
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
cause it to catch fire/etc. Do this at your own risk. I am not 
responsible for any damage that occurs through the use of this program.

If you don't know what you are doing, don't use it.
***************************************************************** 


Use in conjunction with sendir.py

Invocation:
First edit this file and set the offset. The three ranges of interest 
that I know of are 0x5EA1xxxx, 0x7E81xxxx and 0xFE80xxxx. There may be others.

Then run:
python makeir.py > test.lircd

test.lircd needs to then be included into your lircd.conf (/etc/lirc/lircd.conf), and restart lircd

After this, you can use sendir.py to send the codes in the range to the receiver.
'''


# Yamaha IR code range
#offset=0x5EA10000
#offset=0x7E810000
offset=0xFE800000

# Generate all 65536 codes in the range
start=0x0000
end=0x10000

header="\
begin remote\n\
\n\
  name  test\n\
  bits           32\n\
  flags SPACE_ENC|CONST_LENGTH\n\
  eps            30\n\
  aeps          100\n\
\n\
  header       8980  4448\n\
  one           598  1645\n\
  zero          598   524\n\
  ptrail        594\n\
  repeat       8964  2224\n\
  gap          107495\n\
  toggle_bit_mask 0x0\n\
\n\
      begin codes\n\
"

footer="\
      end codes\n\
\n\
end remote\n\
"

print header
for i in range(start, end):
	print "        TEST%04X    0x%08X" % (i, i + offset)
print footer

