from xbee import XBee
from digimeshURJC import DigiMesh
from handler import Handler
from sender import Sender
from sensores import Sensores
import ConfigParser
import datetime
import serial
import time
from xbee.base import TimeoutException
from Adafruit.Adafruit_ADS1x15.Adafruit_ADS1x15 import ADS1x15
import RPi.GPIO as GPIO
import struct


GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


Config = ConfigParser.ConfigParser()
Config.read('conf.ini')

PORT = str(Config.get('XBEE','port'))
BAUD_RATE = str(Config.get('XBEE','baud_rate'))
TIMEOUT = int(Config.get('MOTA','timeout'))
ser = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT)

frame_buffer = list()
xbee = DigiMesh(ser, escaped=True)
sender = Sender()
sensores = Sensores()
handler = Handler()


class Mota:

	def __init__(self):
		self.num_sensores = 0
		self.num_seq = 1
		self.contador = 0
		self.contador_interrupciones = 0
		self.mensaje = ''
		self.mensaje_interrupcion = ''


	def interrupcion_hall(self, channel):
		print "se ha disparado el gpio: " + str(channel)
		dt = datetime.datetime.now()
                hora = time.mktime(dt.timetuple())
                epoch = struct.pack(">i", hora)

		#comprobamos el estado del sensor
		medida = GPIO.input(channel)
		#obtenemos el id del del sensor
		if channel == 14:
			print "El estado del sensor es: " + str(medida)
			sensor = "HALL"
			gpio = 3
		elif channel == 2:
			sensor = 'sensor'+str(2)
			gpio = 2
		elif channel == 3:
			sensor = 'sensor'+str(3)
			gpio = 3
		#creamos la estructura: id_sensor + gpio_sensor + hora + estado
		cadena = sensores.get_sensor_key(sensor) + struct.pack(">h", gpio)[1] + epoch + struct.pack(">h", int(medida))[1]
		self.contador_interrupciones +=1
		self.mensaje_interrupcion += cadena
		print "cadena interrupciones: "
		print self.mensaje_interrupcion
		print self.mensaje_interrupcion.encode("HEX")


	def xbee_awake(self, channel):
		print "\tse ha despertado el xbee"
		mensaje, num_sensores = self.tomar_medidas()
		self.mensaje += mensaje
		self.num_sensores += num_sensores
		self.contador += 1
		if self.contador == 3:
			self.mensaje = struct.pack(">h", self.num_sensores)[1] + self.mensaje		
			sender.send_30(struct.pack(">h", self.num_seq)[1], self.mensaje)
			self.contador = 0
			self.num_sensores = 0
			self.mensaje = ''
			self.num_seq += 1
			print "seq: " + str(self.num_seq)
			if self.num_seq == 256:
				self.num_seq = 1

		if self.contador_interrupciones >= 2:
			mensaje = struct.pack(">h", self.contador_interrupciones)[1] + self.mensaje_interrupcion
			sender.send_40(mensaje)
			self.contador_interrupciones = 0
			self.mensaje_interrupcion = ''


	def conectar_red(self):
		num_sensores = 0
		mensaje = ''
		i = 1

		# Rellenamos el buffer con los sensores especificados en 'conf.ini'
		while i<7:
			sensor = 'sensor'+str(i)
			if Config.get('MOTA',sensor)!='NULL':
				num_sensores += 1
				mensaje += sensores.add_sensor(i, Config.get('MOTA',sensor))
			i += 1

		# Generamos la cadena hexadecimal que transmitiremos
		mensaje = bytearray.fromhex('0' + str(num_sensores) + mensaje)

		# Enviamos un mensaje para obtener los parametros del gateway
		try:
			sender.send_20(mensaje)
			mensaje = xbee.wait_read_frame(timeout=5)
			handler.comprobar(mensaje)
		except TimeoutException:
			print ("no hemos recibido respuesta")
		

	def medida_adc1115(self, sensor):
		pga = 1024
		sps = 32
		if (sensor==1):
			adc = ADS1x15(address=0x48, ic=0x01)
		else:
			adc = ADS1x15(address=0x49 ,ic=0x01)
		v1 = adc.readADCDifferential01(pga, sps)
		time.sleep(0.01)
		v2 = adc.readADCDifferential23(pga, sps)
		r1 = float((v1*100)/v2)
		return r1


	def tomar_medidas(self):
		dt = datetime.datetime.now()
	        hora = time.mktime(dt.timetuple())
		epoch = struct.pack(">i", hora)
		numero_sensores = 1
		medicion = ''
		i = 1
		while i<7:
	                sensor = Config.get('MOTA','sensor'+str(i))
                	if sensor !='NULL':
				numero_sensores += 1
				if sensor == 'PTR_AIRE':
					#medida = 1023
					medida = self.medida_adc1115(i)
					print "\tptr: " + str(medida)
				else:
					#medida = 1023
					medida = self.medida_adc1115(i)
					print "\totro: " + str(medida)
				medicion += sensores.get_sensor_key(sensor) + struct.pack(">h", int(medida*100))
			i += 1
		# Generamos la cadena hexadecimal que transmitiremos
		mensaje = epoch + medicion
		return mensaje, numero_sensores



print "Iniciando Mota"
mota = Mota()

try:
#	GPIO.wait_for_edge(17, GPIO.RISING)
#	mota.conectar_red()
	GPIO.add_event_detect(17, GPIO.RISING, callback=mota.xbee_awake)
	GPIO.add_event_detect(14, GPIO.BOTH, callback=mota.interrupcion_hall, bouncetime=300)

	while True:
		time.sleep(0.1)
except KeyboardInterrupt:
	print ("finalizando!")
	ser.close()
