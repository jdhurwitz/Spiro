import serial, time
import scipy
from firebase import firebase
import numpy as np

#Peak Detectorimports
import sys
from numpy import NaN, Inf, arange, isscalar, asarray, array
from matplotlib.pyplot import plot, scatter, show

import plotly.plotly as py
py.sign_in('jdhurwitz', '6lAGIK2hAesxC4z8nKYS')
import plotly.graph_objs as go
from plotly.tools import FigureFactory as FF

import pandas as pd
import scipy
import peakutils

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



#Peak Detector
def peakdet(v, delta, x = None):
    """
    Converted from MATLAB script at http://billauer.co.il/peakdet.html
    
    Returns two arrays
    
    function [maxtab, mintab]=peakdet(v, delta, x)
    %PEAKDET Detect peaks in a vector
    %        [MAXTAB, MINTAB] = PEAKDET(V, DELTA) finds the local
    %        maxima and minima ("peaks") in the vector V.
    %        MAXTAB and MINTAB consists of two columns. Column 1
    %        contains indices in V, and column 2 the found values.
    %      
    %        With [MAXTAB, MINTAB] = PEAKDET(V, DELTA, X) the indices
    %        in MAXTAB and MINTAB are replaced with the corresponding
    %        X-values.
    %
    %        A point is considered a maximum peak if it has the maximal
    %        value, and was preceded (to the left) by a value lower by
    %        DELTA.
    
    % Eli Billauer, 3.4.05 (Explicitly not copyrighted).
    % This function is released to the public domain; Any use is allowed.
    
    """
    maxtab = []
    mintab = []
       
    if x is None:
        x = arange(len(v))
    
    v = asarray(v)
    
    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')
    
    if not isscalar(delta):
        sys.exit('Input argument delta must be a scalar')
    
    if delta <= 0:
        sys.exit('Input argument delta must be positive')
    
    mn, mx = Inf, -Inf
    mnpos, mxpos = NaN, NaN
    
    lookformax = True
    
    for i in arange(len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = x[i]
        if this < mn:
            mn = this
            mnpos = x[i]
        
        if lookformax:
            if this < mx-delta:
                maxtab.append((mxpos, mx))
                mn = this
                mnpos = x[i]
                lookformax = False
        else:
            if this > mn+delta:
                mintab.append((mnpos, mn))
                mx = this
                mxpos = x[i]
                lookformax = True

    return array(maxtab), array(mintab)


#if __name__=="__main__":
 #   from matplotlib.pyplot import plot, scatter, show
  #  series = [0,0,0,2,0,0,0,-2,0,0,0,2,0,0,0,-2,0]
   # maxtab, mintab = peakdet(series,.3)
   # plot(series)
   # scatter(array(maxtab)[:,0], array(maxtab)[:,1], color='blue')
   # scatter(array(mintab)[:,0], array(mintab)[:,1], color='red')
   # show()

def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """
    import numpy as np
    from math import factorial
    
    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError, msg:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')




if (ser.isOpen()):
	try:
		counter = 0

		ser.flushInput() #flush input buffer, discarding all its contents
		ser.flushOutput()#flush output buffer, aborting current output 
		        
#		time.sleep(0.5)  #give the serial port sometime to receive the data
		vector = []
		while True:

			if(counter == 400):
				ser.flushInput()
				ser.flushOutput()
				counter = 0

				#do peak detection
				maxtab, mintab = peakdet(vector, 0.3)

				#Curve smoothing w/ Savitzky-Golay Filter
				x = maxtab[:,0]
				y = maxtab[:,1]
				yhat = savitzky_golay(y, 51, 7)


				print("Printing y")
				print(y)

				print("Printing yhat")
				print(yhat)
				#print(vector)

				xhat = [j for j in range(len(yhat))]
				#plot(x,y)
				#plot(x, yhat, color = 'black')
				#plot(x, peaks_post, color = 'black')

				max_post, min_post = peakdet(yhat, 0.3);


				#scatter(array(peaks_post)[:,0], array(peaks_post)[:,1],color='red')
				#scatter(array(max_post)[:,0], array(max_post)[:,1],color='red')

				cb = np.array(yhat)
				indices = peakutils.indexes(cb, thres = 0.2/max(cb), min_dist=0.1)
				
				trace = go.Scatter(
					x=[j for j in range(len(yhat))],
					y=yhat,
					mode = 'lines',
					name = 'original plot'
				)

				trace2 = go.Scatter(
					x=indices,
					y=[yhat[j] for j in indices],
					mode = 'markers',
					marker = dict(
						size=8,
						color='rgb(255,0,0)',
						symbol='cross'),
					name='Detected Peaks'
				)

				data = [trace, trace2]
				py.iplot(data, filename = "peaks2")

				#exit()

				time.sleep(1)
				vector = []

			  #request R_eq data (Vout = 1, R_eq = 2)
			ser.write("6")
			Rval = ser.readline()
			
			#remove \r and \n
			Rval = Rval[:-2]
			vector.append(float(Rval))

			print(Rval)

			#push to firebase
			#push_result = firebase.post('/user', {'stretch_val':Rval})

			#numOfLines = numOfLines + 1

			#if (numOfLines >= 5):
			#	break

			counter += 1
		

			#ser.close()
	except Exception, e1:
		print "error communicating...: " + str(e1)
		ser.close()
		exit()

else:
	print "cannot open serial port "




