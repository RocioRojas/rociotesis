import serial
import matplotlib.pyplot as plt
from scipy.signal import lsim
import numpy as np
from scipy.signal import lti
import sys
ser = serial.Serial()  # open serial port
ser.baudrate=115200
ser.timeout=10
ser.port="COM4"
ser.open()


A = np.array([[0, 1E4*0.2340], [-0.0061*1E4, -1E4*1.2927]])
B = np.array([[0.0], [1.2195*1E3]])
C = np.array([[1.0, 0.0]])
D = 0.0
system = lti(A, B, C, D)
u=np.array([0])

while True:
	lect=ser.readline()
	print(lect)
	if lect=='':
		u=np.append(u,0)

	else:
	
		print("antes")
		print(u)

		u=np.append(u,float(int(lect)/100))
		print("despues")
		print(u)
	t = np.linspace(0, 0.1, num=len(u))

	if lect!="":
		tout, y, x = lsim(system, u, t)
		print(y)
		b=int(y[len(y)-1]*100)
		print(b)
		print("enviando...")
		# aux=' '.join(map(str, b))
		#env=ser.write(b)
		env=ser.write((str(b) + "\n").encode())
		print(str(env))

#			plt.plot(t, y)
#			plt.grid(alpha=0.3)
#			plt.xlabel('t')
#			plt.show()
