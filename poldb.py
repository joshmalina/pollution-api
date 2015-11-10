from pymongo import MongoClient, DESCENDING
from numpy import mean, std

class Poldb(object):

	# # our collection is called 'pollution_values'
	P_COLL = 'pollution_values'
	AVE_ERR_COLL = 'ave_errors'
	AVE_ERR_BY_VALUE_COLL = 'ave_errors_by_val'

	# return database, with optional collection
	def __init__(self):
		self.cats = '1'

	def getdb(self):
		MONGODB_URI = 'mongodb://joshuamalina:egroeg499@ds045644.mongolab.com:45644/pollution'
		client = MongoClient(MONGODB_URI).get_default_database()
		return client

	# return the latest hour of polluton predictions
	def getLatestPol(self):
		db = self.getdb()
		# since we have to sort, not sure if find_one would work, and it may be slower than find?
		cursor = db[Poldb.P_COLL].find().sort('_id', DESCENDING).limit(5)
		return list(cursor)[0]

	# aggregates errors by what time is predicted for
	def getErrors(self):
		db = self.getdb()		
		# build a dictionary of all recorded times and actual pollution values
		db[Poldb.P_COLL].find({},{"currently":1})

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
		errors_by_val = dict()
		raw_errors = []
		# for each time we predicted
		for i in db[Poldb.P_COLL].aggregate(pipeline4):
		    # lookup the actual value of the date the prediction is made for
			actual = db[Poldb.P_COLL].find_one({"_id": i["_id"]}, {"currently":1, "_id":0})
		    # if it exists (i.e. we've caught up to it), calculate the errors
			if actual:
		        # iterate through all the prediction n-1, n-2 that have been made for that time
				for j in i["diffAndVal"]:
					actual_val = actual.get("currently")
		            # calcualte the error
					err = abs(j["val"] - actual_val)
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
					if actual_val in errors_by_val:
						errors_by_val[actual_val].append(err)
					else:
						errors_by_val[actual_val] = [err]
					raw_errors.append({'error': err, 'howFarOut': timeOfErr, 'actual': actual_val})
		ave_errors = {str(key): self.remapDict(value) for key, value in errors.iteritems()}
		ave_errors_by_val = {str(key): self.remapDict(value) for key, value in errors_by_val.iteritems()}
		self.addErrors(ave_errors, ave_errors_by_val)		
		#return {"ave_errors_by_val": ave_errors_by_val, "ave_errors": ave_errors}

	def fromMiliToHours(self, militime):
		return militime / 1000 / 60 / 60   

	def remapDict(self, dictEntry):
		return {"avg": mean(dictEntry), "std": std(dictEntry), "count":len(dictEntry)}

	# once per day, let's add the errors to two different collections in the database to reduce
	# cost
	def addErrors(self, ave_errors, ave_errors_by_val):
		db = self.getdb()		
		col_ave = db[Poldb.AVE_ERR_COLL]
		# drop currently stored ave_errors
		col_ave.drop()
		# add most recent ave_errors
		col_ave.insert_one(ave_errors)
		# drop currently stored ave_errors_by_val
		col_ave_by_val = db[Poldb.AVE_ERR_BY_VALUE_COLL]
		col_ave_by_val.drop()
		# add most recent ave_errors_by_val
		col_ave_by_val.insert_one(ave_errors_by_val)

	def getLatestErrors(self):
		db = self.getdb()
		# since we have to sort, not sure if find_one would work, and it may be slower than find?
		cursor_ave = db[Poldb.AVE_ERR_COLL].find().sort('_id', DESCENDING).limit(1)
		cursor_ave_by_val = db[Poldb.AVE_ERR_BY_VALUE_COLL].find().sort('_id', DESCENDING).limit(1)
		return {"ave_errors_by_val": list(cursor_ave_by_val)[0], "ave_errors": list(cursor_ave)[0]}


	





