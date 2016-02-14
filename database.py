import MySQLdb
import datetime
from sensores import Sensores

class DataBase:

	def iniciar_db(self):
		db = MySQLdb.connect("localhost","root","urjc","gateway" )
                cursor = db.cursor()
		return [db, cursor]


	def cerrar_db(self, db, cursor):
		cursor.close()
                db.close()


	def comprobar_mota(self, mac_addr):
		(db, cursor) = self.iniciar_db()
		cursor.execute("""SELECT source, last_seq FROM waspmotes WHERE mac=(%s)""", mac_addr)
		results = cursor.fetchone()
		self.cerrar_db(db, cursor)
		return results


	def get_highest(self):
		(db, cursor) = self.iniciar_db()
		cursor.execute("""SELECT MAX(source) FROM waspmotes""")
                results = cursor.fetchone()
                self.cerrar_db(db, cursor)
                return results


	def update_mota(self, hora, source, seq):
		(db, cursor) = self.iniciar_db()
		cursor.execute (""" UPDATE waspmotes SET ultima_hora=%s, last_seq=%s  WHERE source=%s """,
			(hora.strftime('%Y-%m-%d %H:%M:%S'),
			seq,
			source)
			)
		db.commit()
		self.cerrar_db(db, cursor)


	def insertar_mota(self, datos, source_addr, numero_sensores, hora):
		(db, cursor) = self.iniciar_db()
		cursor.execute("""INSERT INTO waspmotes (source, mac, num_sensores, last_seq, ultima_hora) VALUES (%s,%s,%s,%s,%s)""",
			(source_addr,
			"00"+datos['source_addr'].encode('hex'),
			numero_sensores,
			0,
			hora.strftime('%Y-%m-%d %H:%M:%S'))
			)
		db.commit()
		self.cerrar_db(db, cursor)

		
	def insertar_medida(self, datos, lista_medidas):
		(db, cursor) = self.iniciar_db()
		sensores = Sensores()

                for medida in lista_medidas:
 	               cursor.execute("""INSERT INTO medidas (mota, sensor, valor, hora) VALUES (%s,%s,%s,%s)""",
        		               (int(datos['source_id'].encode('hex'), 16),
                                        medida['id'],
					medida['valor'],
                                        #int(medida['valor'].encode('hex'), 16),
                                        datetime.datetime.fromtimestamp(medida['hora']-7200).strftime('%Y-%m-%d %H:%M:%S'))
                                        )
                       db.commit()

                self.cerrar_db(db, cursor)


	def insertar_sensores(self, source, lista_sensores):
		(db, cursor) = self.iniciar_db()

		for medida in lista_sensores:
			cursor.execute("""INSERT INTO sensores (source, sensor, gpio) VALUES (%s,%s,%s)""",
					(source,
                                        medida['sensor'],
                                        int(medida['gpio'].encode('hex')))
                                        )
			db.commit()
		self.cerrar_db(db, cursor)


	def insertar_retrasos(self, source, inicio, final):
		(db, cursor) = self.iniciar_db()
		inicio = inicio +1
		while inicio < final:
			cursor.execute("""INSERT INTO tramas_perdidas (source, num_seq) VALUES (%s,%s)""",
                                        (source,
                                        inicio)
                                        )
                        db.commit()
			inicio = inicio +1
		self.cerrar_db(db, cursor)
