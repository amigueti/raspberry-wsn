#from database import DataBase
from sensores import Sensores
from sender import Sender
from mqtt import Mqtt
import ConfigParser
import datetime
#import MySQLdb


class Handler:

	def __init__(self):
		self.sensores = Sensores()
		self.sender = Sender()
		#self.database = DataBase()
		self.mqtt = Mqtt()
		self.Config = ConfigParser.ConfigParser()


	def manejar_10(self, datos):
		#try:
		time = datos['data'].split('/')[2]
		cfgfile = open("gateway.ini",'w')
		self.Config.add_section('Router-Params')
		self.Config.set('Router-Params','mac',datos['data'].split('/')[0])
		self.Config.set('Router-Params','source',datos['data'].split('/')[1])
		self.Config.set('Router-Params','refresco',datos['data'].split('/')[3])
		self.Config.write(cfgfile)
		cfgfile.close()


	def manejar_20(self, datos):
		numero_sensores = 0
		pointer = 0
		lista_sensores = []
		numero_sensores = int(datos['data'][pointer].encode('hex'))
		pointer += 1
		j = 0
		while (j<numero_sensores):
			(pointer, sensores_valores) = self.sensores.descomponer(datos['data'], pointer)
			sensores_valores['sensor'] = self.sensores.get_sensor(sensores_valores['sensor'])
			lista_sensores.append(sensores_valores)
			j = j+1

		resultado = self.database.comprobar_mota("00"+datos['source_addr'].encode('hex'))

		if (resultado == None):
			resultado = self.database.get_highest()
			if (resultado[0] == None):
				source = 1
			else:
				source = resultado[0] +1
	                self.database.insertar_mota(datos, source, numero_sensores, datetime.datetime.now())
			self.database.insertar_sensores(source, lista_sensores)
		else:
			source = resultado[0]
			self.database.update_mota(datetime.datetime.now(), source, 0)

		source = str(source)

		if len(source) == 1:
			source = "000" + source
		elif len(source) == 2:
			source = "00" + source
		elif len(source) == 3:
                        source = "0" + source

		self.sender.send_10(source, datos['source_addr'])

		##
		print lista_sensores
		##


	def manejar_30(self, datos):
		numero_sensores = 0
                pointer = 0
		lista_medidas = []
                numero_sensores = int(datos['data'][pointer].encode('hex'), 16)
		num_seq = int(datos['frag_num'].encode('hex'), 16)
                pointer += 1
		guardar = False

		resultado = self.database.comprobar_mota("00"+datos['source_addr'].encode('hex'))
		# mensaje consecutivo
		if ((num_seq==resultado[1]+1) or ((num_seq==1) and (resultado[1]==255))):
			guardar = True
			self.sender.send_ack(datos['source_addr'], datos['frag_num'], 1)
		# mensaje no consecutivo
		elif (num_seq>resultado[1]+1):
			print("Se han perdido mensajes... Habra que recuperarlos.")
			guardar = True
			self.sender.send_ack(datos['source_addr'], datos['frag_num'], 2)
			self.database.insertar_retrasos(datos['source_id'].encode('hex'), resultado[1], num_seq)
		# mensaje repetido
		else:
			self.sender.send_ack(datos['source_addr'], datos['frag_num'], 3)

		if guardar:
			j = 0
			while (j < 3):
				hora = datos['data'][pointer:pointer+4]
				pointer +=4
				hora = int(hora.encode('hex'), 16)
				i = 0
				while (i < (numero_sensores/3)-1):
					(pointer, sensores_valores) = self.sensores.descomponer(datos['data'], pointer)
					sensores_valores.update({'hora':hora})
					lista_medidas.append(sensores_valores)
					i += 1
				j += 1

			## Transformar medidas ##
			for medida in lista_medidas:
				#print medida
				medida = self.sensores.transformar(medida)
				#print medida

			## DATABASE ##
			self.database.insertar_medida(datos, lista_medidas)
			self.database.update_mota(datetime.datetime.now(), datos['source_id'].encode('hex'), num_seq)

			## MQTT ##
			self.Config.read('conf.ini')
			if self.Config.get('MQTT','activado')=='True':
				self.mqtt.send(lista_medidas, datos['source_id'].encode('hex'))


	def manejar_40(self, datos):
		numero_sensores = 0
                pointer = 0
                lista_medidas = []
                numero_sensores = int(datos['data'][pointer].encode('hex'), 16)
                pointer += 1
                j = 0
		while (j<numero_sensores/2):
			(pointer, sensores_valores) = self.sensores.descomponer(datos['data'], pointer)
			sensores_valores['hora'] = int(sensores_valores['hora'].encode('hex'), 16)
			sensores_valores['id'] = sensores_valores['id'] + '-' +  sensores_valores['id2'].encode('hex')
                        lista_medidas.append(sensores_valores)
                        j += 1

		##
		print lista_medidas
		##
		self.database.insertar_medida(datos, lista_medidas)



	def comprobar(self, datos):
		if datos['application_id'] == '\x10':
                	self.manejar_10(datos)
	        elif datos['application_id'] == '\x20':
        	        self.manejar_20(datos)
	        elif datos['application_id'] == '\x30':		#mensajes sincronos
			self.manejar_30(datos)
		elif datos['application_id'] == '\x40':
			self.manejar_40(datos)
	        else:
        	        print 'mensaje no reconocido'
