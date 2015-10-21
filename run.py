#from eve import Eve
import forecast
import rforest
from flask import Flask, json
from decorators import crossdomain
#app = Eve()
app = Flask(__name__)

app.debug = True

@app.route('/')
def hello_world():
    return "Hello world!"

@app.route('/forecast')
@crossdomain(origin='http://localhost:9000')
def index():	
	forest = rforest.forest(train=False)
	frcast = forecast.forecast(forest.X_train.columns, forest.rf)
	#return flask.json.jsonify({'predictions':frcast.df})
	return json.jsonify(frcast.df)

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
