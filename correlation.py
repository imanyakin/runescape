import numpy as np 
from get_item import db_item_path,read_item_file,plot_covariances,plot_prices,plot_autocorrelations,plot_crosscorrelations
import os,re

def list_file_ids():
	pattern = re.compile(".*json")
	return [f.replace(".json","") for f in os.listdir("./db") if bool(pattern.match(f))==True]  



def correlate(item_ids):
	ij = []
	coefs = []
	for i in range(len(item_ids)-1):
		for j in range(i+1, len(item_ids)):
			id_1 = item_ids[i]
			id_2 = item_ids[j]
			assert(id_1 != id_2)
			_,y1 = read_item_file(id_1)
			_,y2 = read_item_file(id_2)
			ij.append((i,j))
			corr = np.corrcoef(y1,y2)[0,1]
			coefs.append(corr)

	return ij,coefs 

ids = list_file_ids()
#  #metal bars
ids = [2351]

ids = [int(i) for i in ids]
# plot_crosscorrelations(ids)

import matplotlib.pyplot as plt

fig, ax = plt.subplots(1)
def get_spectrum(item_id):
	acs = plot_autocorrelations([item_id],show_plot=False)
	spectrum = np.abs(np.fft.fft(acs))

	# fig, ax = plt.subplots(1)	
	# ax.plot([-len(spectrum)/2+i for i in range(len(spectrum))],spectrum,"-",alpha=0.1)
	# plt.show()

	return spectrum[0:len(spectrum)/2] 


ids = range(2000,6000,2)
spectra = []
for it in ids:
	try:
		outp = get_spectrum(it)
		add = True
		for i in range(len(outp)):

			if np.isnan(outp[i]):
				add = False
				print i
		if add:
			spectra.append(outp)

	except Exception,e:
		print e
	

plt.show()

fig, ax = plt.subplots(1)
spectra = np.array(spectra)
print spectra.shape
mu = np.mean(spectra,axis=0)
plt.plot(mu)
plt.show()
maxima = []
for i in range(spectra.shape[0]):
	ys = np.abs(np.array(spectra[i])-mu)
	plt.plot(ys,alpha=0.1)
	maxima.append(np.sum(ys > 2))
# plt.imshow(spectra)
plt.show()

plt.hist(maxima,bins = 50)

plt.show()
