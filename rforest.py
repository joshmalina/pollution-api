from pandas import read_csv, DataFrame
from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_validation import train_test_split
import cPickle

# should be a streamlined function since serving content to the web
class forest():
    
    def __init__(self, train):
        #if train:
        CSV_FILE = 'fifth_prev.csv'
        #CSV_FILE = 'data_pruned_.csv'
        data = read_csv(CSV_FILE)
        self.X_train, self.X_test, self.y_train, self.y_test = self.prepData(data)
        #self.rf = self.buildForest(self.X_train, self.y_train)
        randFor = self.buildForest(self.X_train, self.y_train)
        #else:
        self.rf = randFor
        #self.rf = self.loadRF()
        #self.saveRF(randFor)
        #self.loadRF()

    def saveRF(self, rf):
        with open('randomF.cpickle', 'wb') as f:
            cPickle.dump(rf, f, protocol=2)

    def loadRF(self):
        with open('randomF.cpickle', 'rb') as f:
            self.rf = cPickle.load(f)
        #return rf      
        
    def prepData(self, df):
        #self.df = df        
        return self.splitSet(df)       
        
    def splitSet(self, df):
        # create training (80%) and test (20%) sets
        X_train, X_test, y_train, y_test = train_test_split(df[df.columns.difference(['Value'])], df.Value, test_size=0.2, random_state=42)
        return X_train, X_test, y_train, y_test
    
    def buildForest(self, X_train, y_train):
        NUM_TREES = 100
        NUM_JOBS = 1
        FEATURES_IN_EACH_TREE = "sqrt"
        rf = RandomForestRegressor(n_estimators=NUM_TREES, verbose=1, n_jobs=NUM_JOBS, max_features=FEATURES_IN_EACH_TREE, oob_score=True, max_depth=30)
        rf.fit_transform(X_train, y_train)
        return rf