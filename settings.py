from pymongo import Connection

RESOURCE_METHODS = ['GET','POST','DELETE']

DOMAIN = {
	'weatherPollution': {
		'schema': {
			'year': {
				'type': 'string'
			},
			'month': {
				'type': 'string' 
			},
			'day': 	{
				'type': 'string'
			},
			'hour': {
				'type': 'string'
			},
			'aqi': {
				'type': 'string'
			}
		}
	}
}

MONGO_HOST = 'localhost' # If your mongo server is locally running
MONGO_PORT = 27017
MONGO_USERNAME = ''
MONGO_PASSWORD = ''
MONGO_DBNAME = 'test'