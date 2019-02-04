import serial
import time
import glob
import subprocess
import os

##PARAMETER DEFINITION
#Connection params
TIMEOUT = 1
CONNECTED = False
ser = None

#Arbitrary conventions
fan_ids = ('O', 'T')

#Config params (overridden by config file)
baudrate = 9600
serialroot = '/dev/ttyUSB'
forcelevel1 = -1 #-1 to disable force level
forcelevel2 = -1

#Fan speed curve params (overridden by config file)
ub_temp = [100, 100] #Fans all out at 100 degrees
lb_temp = [50, 50] #Until here, idle speeds
lb_speed = [50, 50] #Idle speed, for when below lb_temp degrees
ub_speed = [3000, 3000] #Max speed, defined by Arduino code (very nonlinear).

#Fan params
sSetpoint1 = -1 #speed setpoint
sSetpoint2 = -1
sMeasure1 = 0 #measured speed
sMeasure2 = 0

#Functions
def sendAndReceive(command):
	global CONNECTED

	try:
		ser.write(command.encode("utf-8"))
		recv = ser.readline()
		recv = recv.decode("utf-8")
	except UnicodeDecodeError:
		recv = 'non-utf-8'
	except serial.SerialException:
		print("Connection error.")
		ser.close()
		CONNECTED = False
		recv = 'Connection reset'
		#Try to make a connection again...
		time.sleep(3)
		makeSerialConnection()
	finally:
		return recv

def readGPUTemp():
	p = subprocess.Popen("sensors", stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	#Radeon 295X2 has two GPUs. Dividing with split('radeon-pci') makes sure
	#that the first occurence of any temperature (denoted by the degree circle)
	#corresponds to the Radeon GPU temperature. The actual number is enclosed 
	#between a + and a °. Finally discard the decimals and  convert to integer.
	temp1 = int(output.decode('utf-8').split('radeon-pci')[1].split('°')[0].split('+')[1].split('.')[0])
	temp2 = int(output.decode('utf-8').split('radeon-pci')[2].split('°')[0].split('+')[1].split('.')[0])
	return (temp1, temp2)
	
def tempToSpeed(temp, fan):
	lbt = lb_temp[fan-1]
	lbs = lb_speed[fan-1]
	ubt = ub_temp[fan-1]
	ubs = ub_speed[fan-1]
	
	if temp < lbt:
		speed = lbs
	elif temp < (ubt - lbt)*1/5:
		#speed = (ubs - lbs)*1/5
		speed = 20
	elif temp < (ubt - lbt)*2/5:
		#speed = (ubs - lbs)*2/5
		speed = 30
	elif temp < (ubt - lbt)*3/5:
		#speed = (ubs - lbs)*3/5
		speed = 50
	elif temp < (ubt - lbt)*4/5:
		#speed = (ubs - lbs)*4/5
		speed = 80
	elif temp > ubt:
		speed = ubs
		
	return speed
		
def setFanSpeed(level, fan):
	recv = sendAndReceive(str(level) + fan_ids[fan-1])
	if (recv == fan_ids[fan-1] + ':' + str(level) + '\r\n'):
		return True
	else:
		print("Received unexpected result: " + recv)
		return False

	
def readConfig(initialisation):
	global baudrate
	global serialroot
	global forcelevel1
	global forcelevel2
	global ub_temp
	global lb_temp
	global lb_speed
	global ub_speed

	try:
		with open('config') as f:
			lines = f.readlines()
			
		for line in lines:
			keyword = line.split('=')[0].strip()
			if not keyword == '': #empty lines
				if not keyword.split('=')[0][0] == '#': #commented lines
					value = line.split('=')[1].split('\n')[0].strip()
					#Serial communication configuration params
					if(keyword == 'baudrate'):
						baudrate = int(value)
					elif(keyword == 'serialroot'):
						serialroot = value
					#Force fan speeds
					elif(keyword == 'forcelevel1'):
						forcelevel1 = int(value)
					elif(keyword == 'forcelevel2'):
						forcelevel2 = int(value)
					#Fan speed curve configuration params
					elif(keyword == 'ub_temp1'):
						ub_temp[0] = int(value)
					elif(keyword == 'lb_temp1'):
						lb_temp[0] = int(value)
					elif(keyword == 'lb_speed1'):
						lb_speed[0] = int(value)
					elif(keyword == 'ub_speed1'):
						ub_speed[0] = int(value)
					elif(keyword == 'ub_temp2'):
						ub_temp[1] = int(value)
					elif(keyword == 'lb_temp2'):
						lb_temp[1] = int(value)
					elif(keyword == 'lb_speed2'):
						lb_speed[1] = int(value)
					elif(keyword == 'ub_speed2'):
						ub_speed[1] = int(value)
					#Unparseable garbage
					else:
						if not (keyword == ''):
							print("Unknown keyword: " + keyword)
	except FileNotFoundError:
		print("No configuration file (in " + os.getcwd() + ")! Using defaults...")
		pass
	finally:
		if initialisation:
			print("Configuration:")
			print(str(serialroot) + '*')
			print(str(baudrate) + ' baud')
			print("ub_temp: " + str(ub_temp))
			print("lb_temp: " + str(lb_temp))
			print("lb_speed: " + str(lb_speed))
			print("ub_speed: " + str(ub_speed))
			print('force fan1: ' + str(forcelevel1))
			print('force fan2: ' + str(forcelevel2) + "\n")
		
def makeSerialConnection():
	global ser
	global CONNECTED
	
	try:
		devices = glob.glob(serialroot + "*")
		
		for device in devices:
			print("Trying to connect to " + device + "...")
			ser = serial.Serial(device,baudrate,timeout=TIMEOUT)
			time.sleep(3)
			a = sendAndReceive('W')
			print(a.split('\r')[0])
			if(a.split('\r')[0] == '1337'):
				#Device responds with appropriate ID
				print("Connected to controller on " + device + "\n")
				CONNECTED = True
				break
			else:
				#Incorrect response: random other device
				print(device + " replied with incorrect ID")
				ser.close()
				
	except serial.SerialException:
		print("Unexpected serial error. Giving up.")
		ser.close()
		CONNECTED = False
		pass
	finally:
		if not CONNECTED:
			print("Could not connect to any device. Exiting...")
			os._exit(1)

## INITIALISATION
readConfig(True)
makeSerialConnection()

## MAIN ROUTINE
try:	
	while True:
		temps = readGPUTemp()
		avgtemp = (temps[0] + temps[1])/2
		
		if (forcelevel1 == -1):
			if not tempToSpeed(avgtemp, 1) == sSetpoint1:
				print("Adjusting fan 1 speed for temp. " + str(avgtemp) + " with speed: " + str(tempToSpeed(avgtemp, 1)))
				if setFanSpeed(tempToSpeed(avgtemp, 1), 1):
					sSetpoint1 = tempToSpeed(avgtemp, 1)
					print("Fan 1 speed adjusted to " + str(tempToSpeed(avgtemp, 1)))
		else:
			if not (sSetpoint1 == forcelevel1):
				print("Setting forcelevel1...")
				if setFanSpeed(forcelevel1, 1):
					sSetpoint1 = forcelevel1
					print("Fan 1 forced to " + str(forcelevel1))
					
		if (forcelevel2 == -1):
			if not tempToSpeed(avgtemp, 2) == sSetpoint2:
				print("Adjusting fan 2 speed for temp. " + str(avgtemp) + " with speed: " + str(tempToSpeed(avgtemp, 2)))
				if setFanSpeed(tempToSpeed(avgtemp, 2), 2):
					sSetpoint2 = tempToSpeed(avgtemp, 2)
					print("Fan 2 speed adjusted to " + str(tempToSpeed(avgtemp, 2)))
		else:
			if not (sSetpoint2 == forcelevel2):
				print("Setting forcelevel2...")
				if setFanSpeed(forcelevel2, 2):
					sSetpoint2 = forcelevel2
					print("Fan 2 forced to " + str(forcelevel2))

		#update configuration file
		readConfig(False)
		time.sleep(1)				
except KeyboardInterrupt:
	print("Stopping...")
	pass
finally:
	ser.close()












