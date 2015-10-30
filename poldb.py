from pymongo import MongoClient, DESCENDING
from numpy import mean, std

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

	def getErrors(self):
		db = self.getdb()		
		# build a dictionary of all recorded times and actual pollution values
		db[Poldb.P_COLL].find({},{"currently":1})
		# aggregate the data set to expose the predictions for each time
		# an example object
		# {u'_id': datetime.datetime(2015, 11, 9, 6, 0),
  			#u'diffAndVal': [
  				#{u'diff': 864000000L, u'val': 194.53},
  				#{u'diff': 860400000L, u'val': 197.75},
  				#{u'diff': 856800000L, u'val': 88.46385714285717},
  				#{u'diff': 853200000L, u'val': 89.06785714285714}
		#   ]
		#},
		pipeline4 = [
			# make a new object for each prediction n+1, n+2, ... n+240
			{ "$unwind" : "$predictions" },
			{ "$project" : 
		     {
		       # include a measure of how far in the past the prediction was made
		       "timeDiff" : { "$subtract": ["$predictions.t_obj", "$_id"]},
		       "_id":0,
		       "madeFor" : "$predictions.t_obj",
		       "estimate": "$predictions.p"            
		     }
		    },
		    {
		    	# regroup to organize around when the prediction is supposed to take place
		        "$group" : { "_id": "$madeFor", "diffAndVal": {"$push": {"diff":"$timeDiff", "val":"$estimate"} } }
		    }
		]
		# initialize empty errors dictionary
		errors = dict()
		# for each time we predicted
		for i in db[Poldb.P_COLL].aggregate(pipeline4):
		    # lookup the actual value of the date the prediction is made for
			actual = db[Poldb.P_COLL].find_one({"_id": i["_id"]}, {"currently":1, "_id":0})
		    # if it exists (i.e. we've caught up to it), calculate the errors
			if actual:
		        # iterate through all the prediction n-1, n-2 that have been made for that time
				for j in i["diffAndVal"]:
		            # calcualte the error
					err = abs(j["val"] - actual.get("currently"))
		            # find the distance at which it occured
					timeOfErr = j["diff"]
		            # convert it to hours
					timeOfErr = self.fromMiliToHours(timeOfErr)
		            # now abstract from time made and reorganize according to
		            # distance from event
		            # if we have a space for this distance i.e. 1 hour away, append
					if timeOfErr in errors:
						errors[timeOfErr].append(err)
		            # otherwise start a new array for that distance    
					else:
						errors[timeOfErr] = [err]
		ave_errors = dict()
        # now that we have the raw errors for each distance, let's calculuate some statistics
		for key, value in errors.iteritems():
        	# grab mean and standard deviation    
			ave_errors[key] = {"avg":mean(value), "std":std(value)}
		return ave_errors

	def fromMiliToHours(self, militime):
		return militime / 1000 / 60 / 60   




