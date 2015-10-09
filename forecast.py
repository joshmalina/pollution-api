from requests import get
from pandas import DataFrame, get_dummies, concat
from numpy import zeros

class forecast(object):    
    
    def __init__(self, colnames, randomforest):
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
        return dict(year=date['year'], month=date['mon'], day=date['mday'], wday=self.day_to_int(date['weekday_name']), hour=date['hour'], pressurei=one['mslp']['english'], icon=one['icon'], dewpti=one['dewpoint']['english'], hum=one['humidity'], temp=one['temp']['metric'], wdird=one['wdir']['degrees'], wdire=one['wdir']['dir'], wspdm=one['wspd']['metric'])
         
    def extractRows(self):
        return DataFrame([self.extractRow(x) for x in self.raw])
    
    # make into binary values categorical vars
    def categorizeVars(self):
        df = self.extractRows()
        return concat([df, get_dummies(df.wdire), get_dummies(df.icon)], axis=1)
    
    def prepForRF(self):
        df = self.categorizeVars()
        # rename certain vars, E to East, W to West, Month to mon, because of inconsistencies in the wunderground API
        df = df.rename(columns={'E':'East', 'W':'West', 'N':'North', 'S':'South', 'month': 'mon', 'temp' : 'tempm'})
        df.columns
        # drop icon, wdire
        # later rebuild the model with day and year
        df = df.drop(['icon', 'wdire', 'wdird', 'day', 'year'], axis=1)
        df = self.imputeVals(df)
        df = self.addPredictions(df)
        return df
    
    def imputeVals(self, df):
        # any missing values in the test frame need to be imputed with all zeroes
        cols_to_add = self.forestColumnNames - df.columns
        for (idx, val) in enumerate(cols_to_add):
            df[val] = zeros(df.shape[0])        
        return df
    
    def addPredictions(self, df):
        df['predictions'] = self.frst.predict(df)
        return df
    