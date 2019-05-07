from flask import Flask, render_template, redirect, request
from werkzeug import secure_filename
import paramiko
import os

UPLOAD_FOLDER = '/home/pi/Desktop/FlaskParamiko/uploaded_files'
#ALLOWED_EXTENSIONS = set(['txt']) #TRY LATER

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
	return render_template('index.html')
	
@app.route('/getFile', methods = ['POST'])
def get_file():

	#FILE UPLOADING
	f = request.files['file']
	filename = secure_filename(f.filename)
	print(filename)
	f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	print(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	
	start_printing(filename)
	print("olakase")
	
	return ''
	
def start_printing(filename):
	ssh_client = paramiko.SSHClient()										#Inicia un cliente SSH

	ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())		#Establece la política para permitir la conexión con el host (confiar en el host)

	ssh_client.connect('11.0.1.24', 22, 'pi', 'inmateriis')					#Se conecta al host mediante SSH ('contraseña' = contraseña del servidor, de OctoPrint en este caso)

	sftp = ssh_client.open_sftp()											#Crea un objeto SFTPClient() para transferir archivos

	##########
	##### Funciones
	##########
																
	#Conecta la impresora con el servidor OctoPrint
	def connect():
		stdin, stdout, stderr = ssh_client.exec_command('cd oprint; cd local; cd bin; cd OctoControl; bash 8connect')
																			#8connect -> conecta la impresora con el servidor OctoPrint
								
		print(stderr.read())												#Imprime el error, si se obtiene alguno
		print(stdout.read())												#Imprime la salida del comando
		
		
	#Sube un archivo de impresión (.gcode) local al servidor OctoPrint
	def upload_file():
		local_path = "/home/pi/Desktop/FlaskParamiko/uploaded_files/" + filename
		remote_path = "/home/pi/.octoprint/uploads/" + filename				#Creamos las rutas de manera dinámica con el nombre de cada archivo
																			#para evitar poner la ruta y el nombre del archivo estático en sftp.put
			
		sftpout = sftp.put(local_path, remote_path)							#Copia un archivo local en el servidor SFTP (OctoPrint)
																			
		print(sftpout)														#Imprime un objeto de tipo "SFTPAttributes" que contiene atributos del archivo copiado


	#Establece la temperatura de la punta
	def set_nozzle_temp():
		stdin, stdout, stderr = ssh_client.exec_command('cd oprint; cd local; cd bin; cd OctoControl; bash 8settemp 230')
																			#8settemp -> establece la temperatura de la punta
		print(stderr.read())
		print(stdout.read())
		
	#Establece la temperatura de la cama
	def set_bed_temp():
		stdin, stdout, stderr = ssh_client.exec_command('cd oprint; cd local; cd bin; cd OctoControl; bash 8setbed 110')
																			#8setbed -> establece la temperatura de la cama
		print(stderr.read())
		print(stdout.read())

	#Selecciona el arhivo a imprimir
	def select_file():
		stdin, stdout, stderr = ssh_client.exec_command('cd oprint; cd local; cd bin; cd OctoControl; bash 8fselect ring.gcode')
																			#8fselect -> selecciona el archivo .gcode de la ruta /home/pi/.octoprint/uploads
		print(stderr.read())
		print(stdout.read())

	#Imprime el archivo seleccionado
	def start_printing():
		ssh_client.exec_command('cd oprint; cd local; cd bin; cd OctoControl; bash 8print')
																			#8print -> comienza el trabajo de impresión del archivo seleccionado


	##########
	##### Ejecución de funciones
	##########

	#Conectar impresora
	#OJO!! Utilizar solo una vez al encender la impresora y despuès comentar o eliminar la linea. Si se usa una segunda vez, la impresora se reinicia
	#connect()

	#Subir archivo
	upload_file()

	#Establecer temperatura de la punta
	#set_nozzle_temp()

	#Establecer temperatura de la cama
	#set_bed_temp()

	#Seleccionar archivo
	#select_file()

	#Imprimir
	#start_printing()
	
	sftp.close()															#Cierra la conexión SFTP
	ssh_client.close()														#Cierra la conexión SSH


if __name__ == '__main__':
	app.run(debug = True, host = '0.0.0.0')
	
	
	
	
	
	
	
	
	
	
