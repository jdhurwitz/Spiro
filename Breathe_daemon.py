import serial, time
from firebase import firebase

ser = serial.Serial()
ser.port = "/dev/tty.HC-06-DevB"
ser.baudrate = 9600
ser.bytesize = serial.EIGHTBITS #number of bits per bytes
ser.parity = serial.PARITY_NONE #set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE #number of stop bits
#ser.timeout = None          #block read

ser.timeout = 1            #non-block read
#ser.timeout = 2              #timeout block read
ser.xonxoff = False     #disable software flow control
ser.rtscts = False     #disable hardware (RTS/CTS) flow control
ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
ser.writeTimeout = 2     #timeout for write


#initialize firebase
firebase = firebase.FirebaseApplication('https://breathe-c0d8a.firebaseio.com/')

if(ser.isOpen()):
	ser.close()

try:
	ser.open()
except Exception, e:
	print("Failed to open serial connection. Error: " + str(e))
	exit()

if (ser.isOpen()):
	try:
		counter = 0

		ser.flushInput() #flush input buffer, discarding all its contents
		ser.flushOutput()#flush output buffer, aborting current output 
		        
#		time.sleep(0.5)  #give the serial port sometime to receive the data
		while True:
			cur_val = 
			if(counter == 1000):
				ser.flushInput()
				ser.flushOutput()
				counter = 0

			  #request R_eq data (Vout = 1, R_eq = 2)
			ser.write("6")
			Rval = ser.readline()
			print(Rval)

			#push to firebase
			push_result = firebase.post('/user', {'stretch_val':Rval})

			#numOfLines = numOfLines + 1

			#if (numOfLines >= 5):
			#	break

			counter += 1
		

			#ser.close()
	except Exception, e1:
		print "error communicating...: " + str(e1)
	except KeyboardInterrupt:
		ser.close()
		exit()

else:
	print "cannot open serial port "