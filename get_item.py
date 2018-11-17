import requests
import json 
import matplotlib.pyplot as plt 
import time 

base_url = "http://services.runescape.com/m=itemdb_oldschool"
db_item_path = "./db/{0}.json"
queries = { 
	"description":"/api/catalogue/detail.json?item={0}",
	"price": "/api/graph/{0}.json"
	}


def get_description(item_id):
	resp = requests.get(base_url+queries["description"].format(item_id))
	print resp
	return json.loads(resp._content)

def get_daily(item_id):
	resp = requests.get(base_url+queries["price"].format(item_id))
	# if debug > 0:
	# 	print resp 
	# 	for k in resp.__dict__.keys():
	# 		print k, resp.__dict__[k]
	# 	print resp.text
	resp = json.loads(resp._content)

	daily = resp["daily"]
	keys = [k for k in sorted(daily.keys())]
	values = [daily[k] for k in keys]

	keys = [int(k) for k in keys]
	values = [int(v) for v in values]
	z = zip(keys,values)
	z = sorted(z,key=lambda x: x[0] )
	keys = [i[0] for i in z]
	values = [i[1] for i in z]
	return keys, values

def write_item_file(item_id):
	x,y =get_daily(item_id)
	with open(db_item_path.format(item_id),"w") as f:
		data = json.dumps({"timestamps":x,"values":y})
		f.write(data)

	
def read_item_file(item_id):
	x,y =get_daily(item_id)
	with open(db_item_path.format(item_id),"r") as f:
		data = json.loads(f.read())
		x = data["timestamps"]
		y = data["values"]
		return x,y


def get_item_id(name):
	with open("item_id_db.json","r") as f:
		data = json.loads(f.read())
		for item in data:
			if item["name"] == name:
				return item["id"]

def get_valid_item_ids():
	with open("item_id_db.json","r") as f:
		data = json.loads(f.read())
		ids = [item["id"] for item in data]
		return ids


def get_name(item_id):
	with open("item_id_db.json","r") as f:
		data = json.loads(f.read())
		for item in data:
			if item["id"] == item_id:
				return item["name"]


from dls.numerics import autocorrelation
import numpy as np 

def plot_covariances(item_ids):
	for i in range(len(item_ids)-1):
		for j in range(i+1,len(item_ids)):
			_,a = get_daily(item_ids[i])
			_,b = get_daily(item_ids[j])
			plt.plot(a,b,'x',label="{0} vs {1}".format(get_name(item_ids[i]),get_name(item_ids[j])))
	plt.legend()
	plt.show()
def plot_prices(ids):

	fig, ax = plt.subplots(1)
	
	xs = []
	ys = [] 
	for i in ids:
		x,y = get_daily(i)
		ax.plot(x,y,'o-',label=get_name(i))
		y = np.asarray(y)
		y = (y-np.mean(y))/np.std(y)
	ax.set_xlabel("Time [epoch]")
	ax.set_ylabel("Price [gp]")
	ax.minorticks_on()
	ax.grid(which="both")
	ax.legend()
	
	plt.show()

SLEEP_TIME = 0.0

def load_database(start_id):
	
	def exponential_backoff(reset=False):
		global SLEEP_TIME
		if reset == True:
			SLEEP_TIME = 0.5
		else:
			time.sleep(SLEEP_TIME)
			SLEEP_TIME = SLEEP_TIME*2.0
			print "new sleep time:", SLEEP_TIME

	for i in get_valid_item_ids():
		if i > start_id:
			written = False
			print "copying item:",i, 
			while written == False:
				try:
					write_item_file(i)
					time.sleep(SLEEP_TIME)
					written = True
					print "done"
					exponential_backoff(reset=True)
				except Exception, e:
					print e
					exponential_backoff()

# load_database(9469)

# plot_prices([9444,3000])

# items = ["Amulet of strength", "Amulet of magic", "Uncut sapphire","Sapphire"]
# ids = [get_item_id(i) for i in items]
