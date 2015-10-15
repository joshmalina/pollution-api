from eve import Eve
import forecast
import rforest
import flask
from decorators import crossdomain
app = Eve()

@app.route('/forecast')
@crossdomain(origin='http://localhost:9000')
def index():	
	forest = rforest.forest(train=False)
	frcast = forecast.forecast(forest.X_train.columns, forest.rf)
	#return flask.json.jsonify({'predictions':frcast.df})
	return flask.json.jsonify(frcast.df)

if __name__ == '__main__':
	app.run(debug=True)
