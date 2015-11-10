import forecast
import rforest
import poldb
from flask import Flask, json
from decorators import crossdomain
from bson import json_util
application = Flask(__name__)

application.debug = True

@application.route('/')
def hello_world():
    return "Hello pol!"

@application.route('/forecast')
@crossdomain(origin='*')
def index():
	# upon user request, lets call the twitter api, and see if the last time
	# is the one in the db (last time not including 24 hour summaries)
	# if its in the db, return that row, otherwise, build out the predictions

	# on the other hand, lets make predictions as a cron job every 60 minutes,
	# and just simply return the latest row to the user
	forest = rforest.forest(train=False)
	frcast = forecast.forecast(forest.X_train.columns, forest.rf)
	return json.jsonify(frcast.df)

# lets grab the latest row of predictions
@application.route('/getLatest')
@crossdomain(origin='*')
def getLatest():
	db = poldb.Poldb()
	return json.jsonify(db.getLatestPol())

# @application.route('/getErrors')
# @crossdomain(origin='*')
# def getErrors():
# 	db = poldb.Poldb()
# 	return json.jsonify(db.getErrors())

@application.route('/getLatestErrors')
@crossdomain(origin='*')
def getLatestErrors():
	db = poldb.Poldb()	
	return json_util.dumps(db.getLatestErrors())



# for production, must have host='0.0.0.0'
if __name__ == '__main__':
	application.run(host='0.0.0.0', debug=True)

