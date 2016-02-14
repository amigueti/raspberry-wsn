from digimeshURJC import DigiMesh
import ConfigParser
import datetime
import serial
import time 

class Sender:

	def iniciar(self):
		PORT = '/dev/ttyUSB0'
                BAUD_RATE = 38400
                ser = serial.Serial(PORT, BAUD_RATE)
                xbee = DigiMesh(ser,escaped=True)
		return (xbee, ser)

	def send_ack(self, destino, seq, estado):
		xbee, ser = self.iniciar()
		#seq = int(seq.encode('hex'), 16)
		#estado = int(estado.encode('hex'), 16)
		#mensaje = str(seq) + '/' + str(estado) + '/'
		#xbee.send('tx', dest_addr='\x00'+destino, app_id = '\x01', data=mensaje)
		xbee.send('ack', dest_addr='\x00'+destino, app_id = '\x01', ack_seq = seq, ack_estado = '\x01')
		ser.close()

	def send_10(self, source, destino):
		Config = ConfigParser.ConfigParser()
		Config.read('conf.ini')
		mac_gateway = str(Config.get('XBEE','mac_gateway'))
		xbee, ser = self.iniciar()
		date = datetime.datetime.now()
		date = date.strftime('%y:%m:%d:0%w:%H:%M:%S')
		mensaje = mac_gateway + '/' + str(source) +  '/' + date + '/' + '1' +'/'
		xbee.send('tx', dest_addr='\x00'+destino, app_id = '\x10', data=mensaje)
		ser.close()

	def send_15(self):
                xbee, ser = self.iniciar()
                date = datetime.datetime.now()
                date = date.strftime('%y:%m:%d:0%w:%H:%M:%S')
                mensaje = "mwnsaje de prueba"
                xbee.send('tx', dest_addr='\x00\x00\x00\x00\x00\x00\xFF\xFF', data=mensaje)
                ser.close()


	def send_20(self, mensaje):
		xbee, ser = self.iniciar()
#		mensaje = int(time.time())
		#mensaje = bytearray.fromhex('014B0149')
		#mensaje = bytearray.fromhex(mensaje)
		#xbee.send('tx', dest_addr='\x00\x00\x00\x00\x00\x00\xFF\xFF', app_id = '\x20', data=mensaje)
		xbee.send('tx', dest_addr='\x00\x13\xA2\x00\x40\x52\x40\x5D', app_id = '\x20', data=mensaje)
		ser.close()


	def send_30(self, seq, mensaje):
		xbee, ser = self.iniciar()
		xbee.send('tx', dest_addr='\x00\x13\xA2\x00\x40\x52\x40\x5D', app_id = '\x30', data=mensaje, frag_num=seq)
		ser.close()

		
	def send_40(self):
		xbee, ser = self.iniciar()
                date = datetime.datetime.now()
                date = date.strftime('%y:%m:%d:0%w:%H:%M:%S')
#		xbee.send('tx', dest_addr='\x00\x00\x00\x00\x00\x00\xFF\xFF', data=mensaje)
#		xbee.send('tx', dest_addr='\x00\x13\xA2\x00\x40\x52\x42\x59', data=mensaje)
		xbee.send('tx', dest_addr='\x00\x13\xA2\x00\x40\x52\x42\x59', data=mensaje)
		ser.close()
