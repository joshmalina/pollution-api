from requests import get
from pandas import DataFrame, get_dummies, concat
from numpy import zeros
import twitter
import datetime

class forecast(object):    
    
    # when users navigate here, we load the forest
    # for performance, we probably should build the tree awhen navigating to the index
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

    def get_prev_pol(self):

        # we actually need to grab the last two; since it's possible that the last one is the 24 hour average
        # in this case, we need to use the next one, or our program will a) fail and our model will b) be using
        # a bad value

        #NUM_PREVIOUS = 5
        NUM_PREVIOUS = 1
        # get tweets from embassy
        tweets_raw = self.api.GetUserTimeline(screen_name='@BeijingAir')
        # collect the five most recent, extract integer value
        pollution_recent = [int(s.text.split(';')[-2]) for idx, s in enumerate(tweets_raw) if (NUM_PREVIOUS + 1) > idx > 0]
        # identify the time of the most recent tweet, t=0 (all prediction will be at times t=1, t=2 ...)
        last_time = str(tweets_raw[0].text.split(';')[0])
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
        # return a dictionary of the five most recent pollution values + 240 times for the future
        return {'p':pollution_recent, 't':times_formatted}

    def imputeVals(self, df):
        # any missing values in the test frame need to be imputed with all zeroes
        cols_to_add = self.forestColumnNames - df.columns
        for (idx, val) in enumerate(cols_to_add):
            df[val] = zeros(df.shape[0])        
        return df

    def addPredictions(self, df, vals):
        #NAMES_OF_PREV = ['nminus1Val', 'nminus2Val', 'nminus3Val', 'nminus4Val', 'nminus5Val']
        NAMES_OF_PREV = ['nminus5Val']
        # extract the five most recent pollution vals from the dictionary
        #values = vals['p']
        values = vals['p'][0]
        # instantiate an empty list for the predictions
        preds = []

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
            #values.insert(0, prediction.item()) 
            values = prediction.item()          
            # drop last value
            #values.pop()            
            # add to list of predictions
            preds.append({'p':prediction.item(), 't':vals['t'][i]})
        
        # add to data frame
        # might be useful elsewhere
        #df['predictions'] = preds
        return {'predictions':preds}

    def categorizeVars(self):
        df = self.extractRows()
        return concat([df, get_dummies(df.wdire)], axis=1)


    def prepForRF(self):
        df = self.categorizeVars()
        df = df.rename(columns={'E':'East', 'W':'West', 'N':'North', 'S':'South'})
        df = self.imputeVals(df)
        df = self.addPredictions(df, self.get_prev_pol())
        return df
    
    
    
    
    