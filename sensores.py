import math

class Sensores:

	lista_sensores = {b"\x41":
				{'name':'STR',
				 'structure':
					[{'name':'length',	'len':1},
					{'name':'valor',	'len':None}]},

			 b"\x47":
                                {'name':'LM35',
                                 'structure':
                                        [{'name':'valor',	'len':2}]},
			 b"\x48":
                                {'name':'DS18B20',
                                 'structure':
                                        [{'name':'valor',	'len':4}]},
			 b"\x49":
                                {'name':'LDR',
                                 'structure':
                                        [{'name':'valor',	'len':2}]},
			 b"\x4A":
                                {'name':'HALL',
                                 'structure':
                                        [{'name':'id2',		'len':1},
					{'name':'valor',	'len':1},
					{'name':'hora',		'len':4}]},
			b"\x4B":
                                {'name':'SENSOR_INFO',
                                 'structure':
                                        [{'name':'gpio',         'len':1},
                                        {'name':'sensor',         'len':1}]},
			b"\x4C":
                                {'name':'PTR_AIRE',
                                 'structure':
					[{'name':'valor',       'len':2},
					{'name':'r_100',        'len':2}]},
			b"\x4D":
                                {'name':'PTR_SUELO',
                                 'structure':
                                        [{'name':'valor',       'len':2}]},
			b"\x4E":
                                {'name':'PTR_VENTAN',
                                 'structure':
                                        [{'name':'valor',       'len':2},
					{'name':'r_100',	'len':2}]},
			b"\x4F":
                                {'name':'GMW86P',
                                 'structure':
                                        [{'name':'valor',       'len':2}]},
			b"\x50":
                                {'name':'HMW88-hum',
                                 'structure':
                                        [{'name':'valor',       'len':2}]}
			}


	def descomponer(self, datos, pointer):
		try:
			sensor = self.lista_sensores[datos[pointer]]
			pointer += 1
		except KeyError:
			raise NotImplementedError("API response specifications could not be found; use a derived class which defines 'api_responses'.")

		index = pointer
		info = {'id':sensor['name']}
	        sensor_spec = sensor['structure']
		for field in sensor_spec:
			if field['len'] is not None:
				if index + field['len'] > len(datos):
		                    raise ValueError("Response packet was shorter than expected")

		                field_data = datos[index:index + field['len']]
                		info[field['name']] = field_data

		                index += field['len']
			else:
				field_data = datos[index:2*int(info['length'].encode('hex'), 16)]

		                if field_data:
		                    info[field['name']] = field_data
                		    index += len(field_data)
		                break
		return (index, info)


	def get_sensor(self, pointer):
		return self.lista_sensores[pointer]['name']


	def transformar(self, medida):
		medida['valor'] = int(medida['valor'].encode('hex'), 16)
		if medida['id'] == 'PTR_AIRE':
			medida['r_100'] = int(medida['r_100'].encode('hex'), 16)
			medida['valor'] = float((float(medida['valor'])/float(medida['r_100']))*100)
			a = 3.9083 * (10**-3)
			b = -5.775 * (10**-7)
			r = 100.0
			raiz = (r*a)**2 - (4*r*b)*(r-medida['valor'])
			medida['valor'] = (-(r*a) + math.sqrt(raiz)) / (2*r*b)
		elif medida['id'] == 'HMW88-hum':
			medida['valor'] = ((medida['valor']*3.3)/1023)/0.15
			medida['valor'] = ((25/4) * medida['valor']) - 25
		elif medida['id'] == 'GMW86P':
			medida['valor'] = ((medida['valor']/150)*(10**3)-4) * (100/16)
		return  medida


	def add_sensor(self, gpio, sensor):#, buffer):
		cadena = ''
		print "buscado: " + str(sensor)
		for key, params in self.lista_sensores.iteritems():
			if params['name'] == sensor:
				print "sensor encontrado:"
#				buffer.append("4B")
#				buffer.append("0"+str(gpio))
#				buffer.append(key.encode('hex'))
				cadena += "4B0" + str(gpio) + key.encode('hex')
#		return buffer
		return cadena

	def get_sensor_key(self, sensor):
		for key, params in self.lista_sensores.iteritems():
			if params['name'] == sensor:
				return key
		# raise error
