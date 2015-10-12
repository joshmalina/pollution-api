from requests import get
from pandas import DataFrame
from numpy import zeros
import twitter

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
        return dict(mday=date['mday'], wday=self.day_to_int(date['weekday_name']), pressurei=one['mslp']['english'], dewpti=one['dewpoint']['english'], hum=one['humidity'], tempm=one['temp']['metric'], wdird=one['wdir']['degrees'], wspdm=one['wspd']['metric'])
         
    def extractRows(self):
        return DataFrame([self.extractRow(x) for x in self.raw])    

    def get_prev_pol(self):
        tweets = [s.text for s in self.api.GetUserTimeline(screen_name='@BeijingAir')]
        # we can probably just stop at five, rather than indexing them back out
        return [int(x.split(';')[-2]) for x in tweets][0:5]

    def imputeVals(self, df):
        # any missing values in the test frame need to be imputed with all zeroes
        cols_to_add = self.forestColumnNames - df.columns
        for (idx, val) in enumerate(cols_to_add):
            df[val] = zeros(df.shape[0])        
        return df

    def addPredictions(self, df, values):
        predictions = zeros(len(df))                
        preds = []        
        # reorder so that in the same shape as the model
        # very important -- otherwise will put the wrong weight on predictors
        df = df[self.forestColumnNames]

        for i in xrange(len(df)):          
            # fill row
            df.loc[i, ['nminus1Val', 'nminus2Val', 'nminus3Val', 'nminus4Val', 'nminus5Val']] = values
            # make a prediction
            prediction = self.frst.predict(df.ix[i])                      
            # add prediction to front
            values.insert(0, prediction.item())           
            # drop last value
            values.pop()            
            # add to list of predictions
            preds.append(prediction.item())
        
        # add to data frame
        #df['predictions'] = preds
        # return predictions
        return preds


    def prepForRF(self):
        df = self.extractRows()
        df = self.imputeVals(df)
        df = self.addPredictions(df, self.get_prev_pol())
        return df
    
    
    
    
    