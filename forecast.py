from requests import get
from pandas import DataFrame, get_dummies, concat
from numpy import zeros
import twitter
import datetime
from pymongo import MongoClient

class forecast(object):    
    
    # when users navigate here, we load the forest
    def __init__(self, colnames, randomforest):
        # these keys might need to be regotten from time to time
        self.api = twitter.Api(consumer_key='hjnVjCeTGhG9ReoG35MyDerx1',consumer_secret='oPTjLl5nEBWqVfxGC5Db04uDWzzhVVh3hRUb643jmkZrn7zhIW', access_token_key='3173034274-Lj194JwBIoHIAMQDrUXvZw2YlFNsgNMYd4xVz1R',access_token_secret='pLQbEnbbr8YJRFmMvfoWdVwWwBfYN0UjSrBOHA01yC39M')
        self.forestColumnNames = colnames
        self.frst = randomforest
        API_KEY = 'a3d4db71573f30f9'
        url = 'http://api.wunderground.com/api/'+API_KEY+'/hourly10day/q/Beijing/Beijing.json'
        content = get(url).json()
        self.raw = content['hourly_forecast']
        self.df = self.prepForRF()
        
    def day_to_int(self, day_string):
        dayvals = {
            'Sunday': 0,
            'Monday': 1,
            'Tuesday': 2,
            'Wednesday': 3,
            'Thursday': 4, 
            'Friday': 5, 
            'Saturday': 6
        }
        return dayvals.get(day_string, 'nothing')
        
    def extractRow(self, one):   
        date = one['FCTTIME']
        return dict(mday=date['mday'], wday=self.day_to_int(date['weekday_name']), pressurei=one['mslp']['english'], dewpti=one['dewpoint']['english'], hum=one['humidity'], tempm=one['temp']['metric'], wdird=one['wdir']['degrees'], wspdm=one['wspd']['metric'], wdire=one['wdir']['dir'])
         
    def extractRows(self):
        return DataFrame([self.extractRow(x) for x in self.raw])

    def extract(self, row):
        DATEAREA = 0
        POLAREA = -2              
        return str(row.text.split(';')[DATEAREA]), int(row.text.split(';')[POLAREA])   

    def get_prev_pol(self):
        tweets_raw = self.api.GetUserTimeline(screen_name='@BeijingAir')
        last_time, last_pol = self.extract(tweets_raw[0])

        # it's possible that the last one is the 24 hour average, so we need to grab the one before
        if len(last_time) > 17:
            last_time, last_pol = self.extract(tweets_raw[1])
        
        # format this into a time struct
        adate = datetime.datetime.strptime(last_time, "%m-%d-%Y %H:%M")

        # instantiate an empty list of times
        tms = []

        # create a list of 240 hours into the future
        # want to incorporate this for loop in addPredictions so we are not looping twice
        for i in xrange(1, 241):
            tms.append(adate + datetime.timedelta(hours=i))            
        # make the times look good, aka Wednesday at 2pm
        times_formatted = map(lambda x: x.strftime("%A at %I:%M%p"), tms)

        t_raw = map(lambda x: x.strftime("%Y-%m-%d %H:%M"), tms)        
        # return a dictionary of the five most recent pollution values + 240 times for the future
        return {'p':last_pol, 'collected_at': adate, 't_obj': tms}

    def addToDB(self, document):
        MONGODB_URI = 'mongodb://joshuamalina:egroeg499@ds045644.mongolab.com:45644/pollution'
        client = MongoClient(MONGODB_URI)
        # access database
        db = client.get_default_database()
        # access collection
        collectn = db.pollution_values
        # check for already existing
        #cursor = collectn.find({document['_id']: {"$exists": True}}).limit(1)
        cursor = collectn.find({"_id" : document['_id']})

        if cursor.count() == 0:
            return collectn.insert_one(document)

    # def updatePrevPol(self, pollution_val, for_what_time):
    #     remote_connection = ''
    #     client = MongoClient()
    #     # access database
    #     db = client.pollution
    #     # access collection
    #     collectn = db.pollution_values        
    #     result = collectn.update_one(
    #         {"_id": for_what_time},
    #         {
    #             "$set": {
    #                 "actual": pollution_val
    #             }
    #         }
    #     )
    
    def imputeVals(self, df):
        # any missing values in the test frame need to be imputed with all zeroes
        cols_to_add = self.forestColumnNames - df.columns
        for (idx, val) in enumerate(cols_to_add):
            df[val] = zeros(df.shape[0])        
        return df

    def addPredictions(self, df, vals):
        NAMES_OF_PREV = ['nminus5Val']
        values = vals['p']
        currently = vals['p']
        # lets store this current hours actual pollution value in the db
        # not sure where this will be necessary anymore
        #self.updatePrevPol(pollution_val=values, for_what_time=vals['collected_at']) 
        # instantiate an empty list for the predictions
        fordb = []
        # reorder columns that in the same shape as the model
        # very important -- otherwise will put the wrong weight on predictors
        df = df[self.forestColumnNames]

        # for the length of the future values, (10 days * 24 hours = 240)
        for i in xrange(len(df)): 
            # fill row with previous pollution values
            df.loc[i, NAMES_OF_PREV] = values
            # make a prediction
            prediction = self.frst.predict(df.ix[i])                      
            # add prediction to front of values
            values = prediction.item()          
            # add to list of predictions

            fordb.append({'p':prediction.item(), 't_obj':vals['t_obj'][i]})        
        
        add_to_db = {'_id': vals['collected_at'], 'predictions':fordb, 'currently':currently}
        # this is what we put into a new row
        self.addToDB(add_to_db)
        return add_to_db

    def categorizeVars(self):
        df = self.extractRows()
        return concat([df, get_dummies(df.wdire)], axis=1)


    def prepForRF(self):
        df = self.categorizeVars()
        df = df.rename(columns={'E':'East', 'W':'West', 'N':'North', 'S':'South'})
        df = self.imputeVals(df)
        df = self.addPredictions(df, self.get_prev_pol())
        return df

    
    
    
    
    