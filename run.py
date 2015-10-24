import forecast
import rforest
from flask import Flask, json
from decorators import crossdomain
application = Flask(__name__)

application.debug = True

@application.route('/')
def hello_world():
    return "Hello pol!"

@application.route('/forecast')
#@crossdomain(origin='http://localhost:9000')
#@crossdomain(origin='http://pollution-ng.herokuapp.com')
@crossdomain(origin='*')
def index():	
	forest = rforest.forest(train=False)
	frcast = forecast.forecast(forest.X_train.columns, forest.rf)
	#return flask.json.jsonify({'predictions':frcast.df})
	return json.jsonify(frcast.df)

if __name__ == '__main__':
	application.run(host='0.0.0.0', debug=True)
