from subprocess import call
import datetime
import ConfigParser

class Mqtt:


	def send(self, lista_medidas, source):
		Config = ConfigParser.ConfigParser()
		Config.read('conf.ini')
		
		print "Transmitoiendo a IBM"
		for medida in lista_medidas:
			hora = datetime.datetime.fromtimestamp(medida['hora']-7200).strftime('%Y-%m-%d %H:%M:%S')
			trama = str(source) + ';' + str(hora) + ';' + str(medida['id']) + ';' + str(int(medida['valor'].encode('hex'), 16)) + ';'
			call(["mosquitto_pub",
				"-h",
				str(Config.get('MQTT','broker')),
				"-t",
				str(Config.get('MQTT','topic')),
				"-m",
				trama,
				"-p",
				str(Config.get('MQTT','puerto')),
				"-i",
				str(Config.get('MQTT','user'))
			])
