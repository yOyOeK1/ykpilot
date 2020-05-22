import numpy as np
import warnings


def fftPlot(pointsObj, sig, dt=None, plot=True):
	# here it's assumes analytic signal (real signal...)- so only half of the axis is required

	if dt is None:
		dt = 1
		t = np.arange(0, sig.shape[-1])
	else:
		t = np.arange(0, sig.shape[-1]) * dt

	if sig.shape[0] % 2 != 0:
		warnings.warn("signal prefered to be even in size, autoFixing it...")
		t = t[0:-1]
		sig = sig[0:-1]

	sigFFT = np.fft.fft(sig) / t.shape[0]  # divided by size t for coherent magnitude

	freq = np.fft.fftfreq(t.shape[0], d=dt)

	# plot analytic signal - right half of freq axis needed only...
	firstNegInd = np.argmax(freq < 0)
	freqAxisPos = freq[0:firstNegInd]
	sigFFTPos = 2 * sigFFT[0:firstNegInd]  # *2 because of magnitude of analytic signal

	if plot:
		tp = []
		trimFrom = 1
		
		#sigFFT = sigFFT[trimFrom:len(sigFFT)//8]
		
		if len(freqAxisPos) > 200:
			every = 1#int(len(freqAxisPos)/250)
			freqAxisPos = freqAxisPos[trimFrom:len(freqAxisPos)//8]
			vals = np.abs(sigFFTPos)[trimFrom:len(sigFFT)//8]
		else:
			every = 1
			freqAxisPos = freqAxisPos[trimFrom:]
			vals = np.abs(sigFFTPos)[trimFrom:]

		
		xmin = min(freqAxisPos)
		xmax = max(freqAxisPos)
		xdiv = xmax - xmin 
		
		ymin = min( vals )
		ymax = max( vals )
		ydiv = ymax-ymin
	
			
		for i,x in enumerate(freqAxisPos):
			if not i % every:
				tp.append([
					((x-xmin)/xdiv)*90.0,
					((vals[i]-ymin)/ydiv)
					])
		if pointsObj != None:
			pointsObj.points = tp
		#print(len(tp))

	return tp
	

def fftPlotData(pointsObj, sig, plot = True):
	dt = 10

	# build a signal within nyquist - the result will be the positive FFT with actual magnitude
	t = np.arange(0, 1 + dt, dt)
	try:
		return fftPlot(pointsObj, sig, dt=dt, plot=plot)
	except:
		print("x")
	# res in samples (if freqs axis is unknown)
	#fftPlot(sig)
