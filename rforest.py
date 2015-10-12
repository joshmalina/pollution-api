from pandas import read_csv, DataFrame
from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_validation import train_test_split

# should be a streamlined function since serving content to the web
class forest():
    
    def __init__(self):
        data = read_csv('data_pruned_.csv')
        self.X_train, self.X_test, self.y_train, self.y_test = self.prepData(data)
        self.rf = self.buildForest(self.X_train, self.y_train)
        
    def prepData(self, df):
        self.df = df
        return self.splitSet(df)       
        
    def splitSet(self, df):
        # create training (80%) and test (20%) sets
        X_train, X_test, y_train, y_test = train_test_split(df[df.columns.difference(['Value'])], df.Value, test_size=0.2, random_state=42)
        return X_train, X_test, y_train, y_test
    
    def buildForest(self, X_train, y_train):
        NUM_TREES = 10
        NUM_JOBS = 1
        rf = RandomForestRegressor(n_estimators=NUM_TREES, verbose=1, n_jobs=NUM_JOBS)
        rf.fit_transform(X_train, y_train)
        return rf    
    
        