'''
yamahanec2lirc.py - Converts Yamaha/NEC IR codes into LIRC format.



Copyright by Ian Burns <ian.burns138@gmail.com>

yamahanec2lirc is free software; you can redistribute it and/or modify
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



Invocation:
python yamahanec2lirc.py <infile> <device> <product> <id_code> > <output_file>
eg python yamahanec2lirc.py yamaha_rxv.csv RECEIVER 767 1 > yamaha_rxv767.lircd


Notes on input file:
CSV format, in similar form to the files in doc/yamaha_rxv

Column 1: Device - The device the code applies to. eg Receiver, Tuner
Column 2: Function Group - This groups the codes into similar functions
Column 3: Function Name - This is the remote code name
Column 4: Zone - The receiver zone that the code applies to
Column 5: ID1 Code - This is the remote code in Yamaha/NEC format. The receiver supports two different code sets, I assume so you could have two receivers and not have the remotes interfere with one another
Column 6: ID2 Code - See column 5
Column 7: Comment - This specifies which products the code will work with. If blank, then will appear in all product lirc remote definitions, otherwise will be filtered by products specified
Column 8: Export Comment - Comments in this column will appear as comments above the code in the lirc remote definition. If prefixed with # then the code itself will be commented out.

The program generates codes for the device specified (ie when device matches the name in device column).

It generates a remote definition for the following:
<Device>_<Product>_ALL - Where the Zone column contains "ALL" or "-", the code will be added to this remote definition
<Device>_<Product>_MAIN - Where the Zone column contains "MAIN", the code will be added to this remote definition
<Device>_<Product>_ZONEx - Where the Zone column matches each zone (ZONE2, ZONE3, etc), the code will be added to this remote definition

eg RECEIVER_767_ALL, RECEIVER_767_MAIN, RECEIVER_767_ZONE2

Remote code names are named like <Function Group>_<Function Name>, eg ZONE_CONTROL_PARTY_OFF

'''
import re
import csv
import sys

def flip_bits(nibble):
	rn = 0x00
	for i in range(0, 4):
		if (nibble & (0x01 << i) != 0):
			rn |= (0x08 >> i)
	return rn

def swap_n_flip(byte):
	hn = (byte & 0xF0) >> 4
	ln = (byte & 0x0F)
	hn = flip_bits(hn)
	ln = flip_bits(ln)
	
	swapped = hn | (ln << 4)
	return swapped


def lirc_to_yamahanec_code(lirccode):
	"""Convert lirc code to yamaha/nec IR code"""
	#( "KEY_VOLUMEUP", 0x5EA158A7, "7A-1A" ),
	b1 = (lirccode >> 24) & 0xFF
	b2 = (lirccode >> 16) & 0xFF
	b3 = (lirccode >> 8) & 0xFF
	b4 = (lirccode >> 0) & 0xFF
	
	yncode = ""
	if (0xFF - b1 == b2):
		yncode += "%02X" % swap_n_flip(b1)
	else:
		yncode += "%02X%02X" % (swap_n_flip(b1), swap_n_flip(b2))
	yncode += "-"
	if (0xFF - b3 == b4):
		yncode += "%02X" % swap_n_flip(b3)
	else:
		yncode += "%02X%02X" % (swap_n_flip(b3), swap_n_flip(b4))
		
	return yncode


def yamahanec_code_to_lirc(yncode):
	"""Convert yamaha/nec IR code to lirc format"""
	# Match "7A-037C" style codes
	m = re.match("([0-9a-fA-F]{2})-([0-9a-fA-F]{2})([0-9a-fA-F]{2})", yncode)
	if (m is not None and m.group(1) is not None and m.group(2) is not None and m.group(3) is not None):
		b1 = int(m.group(1), 16)
		b2 = int(m.group(2), 16)
		b3 = int(m.group(3), 16)
		b1s = swap_n_flip(b1)
		b2s = swap_n_flip(b2)
		b3s = swap_n_flip(b3)
		code = (b1s << 24) | ((0xFF - b1s) << 16) | (b2s << 8) | (b3s << 0)
	else:
		# Match "7E-6C" style codes
		m = re.match("([0-9a-fA-F]{2})-([0-9a-fA-F]{2})", yncode)
		if (m is not None and m.group(1) is not None and m.group(2) is not None):
			b1 = int(m.group(1), 16)
			b2 = int(m.group(2), 16)
			b1s = swap_n_flip(b1)
			b2s = swap_n_flip(b2)
			code = (b1s << 24) | ((0xFF - b1s) << 16) | (b2s << 8) | ((0xFF - b2s) << 0)
		else:
			# Match "7F01-5B24" style codes
			m = re.match("([0-9a-fA-F]{2})([0-9a-fA-F]{2})-([0-9a-fA-F]{2})([0-9a-fA-F]{2})", yncode)
			if (m is not None and m.group(1) is not None and m.group(2) is not None and m.group(3) is not None and m.group(4) is not None):
				b1 = int(m.group(1), 16)
				b2 = int(m.group(2), 16)
				b3 = int(m.group(3), 16)
				b4 = int(m.group(4), 16)
				b1s = swap_n_flip(b1)
				b2s = swap_n_flip(b2)
				b3s = swap_n_flip(b3)
				b4s = swap_n_flip(b4)
				code = (b1s << 24) | (b2s << 16) | (b3s << 8) | (b4s << 0)
			else:
				# Match "7F01-56" style codes
				m = re.match("([0-9a-fA-F]{2})([0-9a-fA-F]{2})-([0-9a-fA-F]{2})", yncode)
				if (m is not None and m.group(1) is not None and m.group(2) is not None and m.group(3) is not None):
					b1 = int(m.group(1), 16)
					b2 = int(m.group(2), 16)
					b3 = int(m.group(3), 16)
					b1s = swap_n_flip(b1)
					b2s = swap_n_flip(b2)
					b3s = swap_n_flip(b3)
					code = (b1s << 24) | (b2s << 16) | (b3s << 8) | ((0xFF - b3s) << 0)
				else:
					raise Exception("Invalid code format: \"%s\"" % (yncode))
	return code

# Key name, expected lirc code, yamaha-nec code
test_codes = [ \
  ( "KEY_BDDVD", 0x5EA100FE, "7A-007F" ),
  ( "KEY_TV", 0x5EA1C03E, "7A-037C" ),
  ( "KEY_CD", 0x5EA1609E, "7A-0679" ),
  ( "KEY_RADIO", 0x5EA1906E, "7A-0976" ),	
  ( "KEY_6", 0xFE806A95, "7F01-56" ),
  ( "KEY_7", 0xFE80EA15, "7F01-57" ),
  ( "KEY_8", 0xFE801AE5, "7F01-58" ),
  ( "KEY_9", 0xFE809A65, "7F01-59" ),
  ( "KEY_VOLUMEUP", 0x5EA158A7, "7A-1A" ),
  ( "KEY_VOLUMEDOWN", 0x5EA1D827, "7A-1B" ),
  ( "KEY_MUTE", 0x5EA138C7, "7A-1C" ),
  ( "KEY_FM", 0xFE801AE4, "7F01-5827" ),
  ( "KEY_AM", 0xFE80AA54, "7F01-552A" ),
  ( "KEY_PRESETUP", 0xFE80DA24, "7F01-5B24" ),
  ( "KEY_PRESETDOWN", 0xFE807A84, "7F01-5E21" )
]


def test():
	"""Check that the conversions match what is expected"""
	for test in test_codes:
		code = yamahanec_code_to_lirc(test[2])
		if (code != test[1]):
			raise Exception("Error converting y->l %s" % (test[0]))
		code = lirc_to_yamahanec_code(test[1])
		if (code != test[2]):
			raise Exception("Error converting %s l->y" % (test[0]))

test()


# Command line
if (len(sys.argv) != 5):
	raise Exception("Invalid number of command line arguments.\nCheck the top of the file for instructions.")
	
infile = sys.argv[1]
device = sys.argv[2]
product = sys.argv[3]
id_code = int(sys.argv[4])

COL_DEVICE = 0
COL_FNGRP = 1
COL_FNNAME = 2
COL_ZONE = 3
COL_ID1 = 4
COL_ID2 = 5
COL_PRODUCT = 6
COL_EXPORTCOMMENT = 7


def parse_file(zone):
	csvfile = open(infile, 'rb')
	csvreader = csv.reader(csvfile, delimiter=',', quotechar='\"')
	for row in csvreader:
		if (row[COL_DEVICE] == device and 
		    (row[COL_ZONE] == zone or (zone == "ALL" and row[COL_ZONE] == "-")) and 
		    (row[COL_PRODUCT] == "" or row[COL_PRODUCT].find(product) >= 0)):			
			if (id_code == 1):
				yncode = row[COL_ID1]
			else:
				yncode = row[COL_ID2]
			try:
				lirc_code = yamahanec_code_to_lirc(yncode)
			except:
				print "Failed at %s_%s for zone %s" % (row[COL_FNGRP], row[COL_FNNAME], zone) 
				raise
			key_name = "%s_%s" % (row[COL_FNGRP], row[COL_FNNAME])
			
			# Print comment row
			if (row[COL_EXPORTCOMMENT] != ""):
				s = row[COL_EXPORTCOMMENT]
				if (s.startswith("#")):
					s = s[1:]
				print "# %s" % (s)

			# If export comment row starts with # then comment out the IR code
			if (row[COL_EXPORTCOMMENT].startswith("#")):
				comment_out = "#"
			else:
				comment_out = ""
			
			print "%s            %s 0x%08X" % (comment_out, key_name.ljust(30), lirc_code)
	csvfile.close()


header="\
begin remote\n\
\n\
  name  %s\n\
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

zones = [ "ALL", "MAIN", "ZONE2" ]

for zone in zones:
	remote_name = "%s_%s_%s" % (device, product, zone) 

	print header % (remote_name)
	parse_file(zone)
	print footer
	

# Reverse lookup - lirc to yamaha/nec
#print "z2 KEY_PLUS10: %s" % lirc_to_yamahanec_code(0xFE80DE21)
#print "m KEY_PLUS10: %s" % lirc_to_yamahanec_code(0xFE80DA25)
#print "Self test1: %s" % lirc_to_yamahanec_code(0x5ea1FB04)
#print "Self test2: %s" % lirc_to_yamahanec_code(0x5ea1FB84)
#print "Zone2 on: %s" % lirc_to_yamahanec_code(0x7e815da2)
#print "Main on: %s" % lirc_to_yamahanec_code(0x7e817e81)

