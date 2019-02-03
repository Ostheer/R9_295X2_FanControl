import serial
import time
import glob

#Connection params
TIMEOUT = 1
CONNECTED = False

#Config params
baudrate = 9600
serialroot = '/dev/ttyUSB'
forcelevel1 = 0
forcelevel2 = 0

#Fan params
sSetpoint1 = 0
sSetpoint2 = 0
sMeasure1 = 0
sMeasure2 = 0

#Functions
def sendAndReceive(command):
	ser.write(command.encode("utf-8"))
	recv = ser.readline()
	try:
		recv = recv.decode("utf-8")
	except UnicodeDecodeError:
		recv = 'non-utf-8'
	return recv

## INITIALISATION

#Read configuration file
try:
	with open('config') as f:
		lines = f.readlines()
		
	for line in lines:
		keyword = line.split('=')[0].strip()
		if(keyword == 'baudrate'):
			baudrate = int(line.split('=')[1].split('\n')[0].strip())
		elif(keyword == 'serialroot'):
			serialroot = line.split('=')[1].split('\n')[0].strip()
		elif(keyword == 'forcelevel1'):
			forcelevel1 = int(line.split('=')[1].split('\n')[0].strip())
		elif(keyword == 'forcelevel2'):
			forcelevel2 = int(line.split('=')[1].split('\n')[0].strip())
		else:
			if not (keyword == ''):
				print("Unknown keyword: " + keyword)
			
	print("Configuration:")
	print(str(serialroot) + '*')
	print(str(baudrate) + ' baud')
	print('force fan1: ' + str(forcelevel1))
	print('force fan2: ' + str(forcelevel2))
	print('')
	
except FileNotFoundError:
	print("No configuration file! Using defaults...")
finally:
	#Open serial port
	try:
		devices = glob.glob(serialroot + "*")
		devices.reverse()
		
		for device in devices:
			print("Trying to connect to " + device + "...")
			ser = serial.Serial(device,baudrate,timeout=TIMEOUT)
			time.sleep(3)
			a = sendAndReceive('W')
			print(a)
			if(a.split('\r')[0] == '1337'):
				#Device responds with appropriate ID
				print("Connected to controller on " + device)
				CONNECTED = True
				break
			else:
				#Incorrect response: random other device
				print(device + " replied with incorrect ID")
				ser.close()
				
	except serial.SerialException:
		#dingen hier?
		print("Unexpected serial error. Giving up.")
		ser.close()
		pass
	finally:
		if not CONNECTED:
			print("Could not connect to any device. Exiting...")
			quit()



##MAIN ROUTINE

try:	
	while True:
		
		if (forcelevel1 == 0):
			print("1: temp monitor not implemented")
		else:
			if not (sSetpoint1 == forcelevel1):
				print("Setting forcelevel1...")
				try:
					recv = sendAndReceive(str(forcelevel1) + 'O')
					if (recv == 'f1:'+str(forcelevel1)+'\r\n'):
						sSetpoint1 = forcelevel1
						print("Fan 1 speed set to forced level")
				except serial.SerialException:
					print("Oh fuck, something happened.")
					ser.close()
					quit() 
		
		if (forcelevel2 == 0):
			print("2: temp monitor not implemented")
		else:
			if not (sSetpoint2 == forcelevel2):
				print("Setting forcelevel2...")
				try:
					recv = sendAndReceive(str(forcelevel2) + 'T')
					if (recv == 'f2:'+str(forcelevel2)+'\r\n'):
						sSetpoint2 = forcelevel2
						print("Fan 2 speed set to forced level")
				except serial.SerialException:
					print("Oh fuck, something happened.")
					ser.close()
					quit() 				
					
		time.sleep(1)
except KeyboardInterrupt:
	print("Stopping...")
	pass
finally:
	ser.close()












