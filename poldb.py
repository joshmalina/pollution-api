from pymongo import MongoClient, DESCENDING

class Poldb(object):

	# # our collection is called 'pollution_values'
	P_COLL = 'pollution_values'

	# return database, with optional collection
	def __init__(self):
		self.cats = '1'

	def getdb(self):
		MONGODB_URI = 'mongodb://joshuamalina:egroeg499@ds045644.mongolab.com:45644/pollution'
		client = MongoClient(MONGODB_URI).get_default_database()
		return client

	# return the latest hour of polluton predictions
	def getLatestPol(self):
		LAST_TO_FIRST = -1
		db = self.getdb()
		# since we have to sort, not sure if find_one would work, and it may be slower than find?
		cursor = db[Poldb.P_COLL].find().sort('_id', DESCENDING).limit(5)
		return list(cursor)[0]


