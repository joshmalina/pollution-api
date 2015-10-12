from eve import Eve
import forecast
import rforest
import flask
app = Eve()

@app.route('/forecast')
def index():	
	forest = rforest.forest()
	frcast = forecast.forecast(forest.X_train.columns, forest.rf)
	return flask.json.jsonify({'predictions':frcast.df})

if __name__ == '__main__':
	app.run(debug=True)
