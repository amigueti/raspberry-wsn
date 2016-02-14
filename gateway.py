from xbee import XBee
from digimeshURJC import DigiMesh
from handler import Handler
from sender import Sender
import ConfigParser
import datetime
import serial
import time

Config = ConfigParser.ConfigParser()
Config.read('conf.ini')

PORT = str(Config.get('XBEE','port'))
BAUD_RATE = str(Config.get('XBEE','baud_rate'))
ser = serial.Serial(PORT, BAUD_RATE)

xbee = DigiMesh(ser, escaped=True)

handler = Handler()

print "Iniciando GateWay.\n"
while True:
    try:
        mensaje = xbee.wait_read_frame()
	source = int(mensaje['source_id'].encode('hex'), 16)
	app_id = int(mensaje['application_id'].encode('hex'), 16)
	mac = int(mensaje['source_addr'].encode('hex'), 16)
	date = datetime.datetime.now()

	print " "
	print date.strftime('%d/%m/%y %H:%M:%S') + ' -> ' + str(source) + ' : ' + str(app_id) + ' : ' + str(mac)
	print mensaje

	handler.comprobar(mensaje)
    except KeyboardInterrupt:
        break
        
ser.close()
