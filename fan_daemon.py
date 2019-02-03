import serial
import time
import glob

#Connection params
TIMEOUT = 1
CONNECTED = False

#Config params
baudrate = 9600
serialroot = '/dev/ttyUSB'
forecelevel1 = 0
forecelevel2 = 0

#Fan params
sSetpoint1 = 0
sSetpoint2 = 0
sMeasure1 = 0
sMeasure2 = 0

#Functions
def sendAndReceive(command):
	print("ik poog te versturen: " + command)
	ser.write(command.encode("utf-8"))
	print("keepalive")
	recv = ser.readline()
	recv = recv.decode("utf-8")
	print("Received in functie:")
	print(recv)
	return recv

## INITIALISATION

#Read configuration file
try:
	with open('config') as f:
		lines = f.readlines()
		
	for line in lines:
		keyword = line.split('=')[0].strip()
		if not (keyword == ''):
			if(keyword == 'baudrate'):
				baudrate = int(line.split('=')[1].split('\n')[0].strip())
			elif(keyword == 'serialroot'):
				serialroot = line.split('=')[1].split('\n')[0].strip()
			elif(keyword == 'forcelevel1'):
				forecelevel1 = int(line.split('=')[1].split('\n')[0].strip())
			elif(keyword == 'forcelevel2'):
				forecelevel2 = int(line.split('=')[1].split('\n')[0].strip())
			else:
				print("Unknown keyword: " + keyword)
except FileNotFoundError:
	print("No configuration file! Using defaults...")
finally:
	#Open serial port
	try:
		devices = glob.glob(serialroot + "*")
		
		for device in devices:
			print(devices)
			print("Trying to connect to " + device + " with settings:")
			print(device)
			print(baudrate)
			print(TIMEOUT)
			ser = serial.Serial(device,baudrate,timeout=TIMEOUT)
			time.sleep(4)
			a = sendAndReceive('W')
			print(a)
			a = 'nietgoeed'
			if(a.split('\r')[0] == '1337'):
				#Device responds with appropriate ID
				print("Connected with controller on " + device)
				CONNECTED = True
				break
			else:
				#Incorrect response: random other device
				print(device + " replied with incorrect ID")
				ser.close()
				
		print("ik zeg dat ik klaar ben met de for loop")
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
				try:
					recv = sendAndReceive(str(forecelevel1) + 'O')
					if (recv == 'f1:'+str(forecelevel1)):
						sSetpoint1 = forecelevel1
						print("Fan 1 speed set to forced level")
				except serial.SerialException:
					print("Oh fuck, something happened.")
					ser.close()
					quit() 
		
		if (forcelevel2 == 0):
			print("2: temp monitor not implemented")
		else:
			if not (sSetpoint2 == forcelevel2):				
				try:
					recv = sendAndReceive(str(forecelevel2) + 'T')
					if (recv == 'f2:'+str(forecelevel2)):
						sSetpoint2 = forecelevel2
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












