from pandas import read_csv, concat, get_dummies, DataFrame
from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_validation import train_test_split
from sklearn.metrics import r2_score

class forest():
    
    def __init__(self):
        data = read_csv('data.csv')
        self.X_train, self.X_test, self.y_train, self.y_test = self.prepData(data)
        self.rf = self.buildForest(self.X_train, self.y_train)
        #self.measures = self.plotMetrics()
        
    def prepData(self, df):
        df = self.catVars(df)
        df = self.removeUnusedVars(df)
        self.df = df
        return self.splitSet(df)
        
    def catVars(self, df):
        wdire_cat = get_dummies(df.wdire)
        icon_cat = get_dummies(df.icon)
        return concat([df, wdire_cat, icon_cat], axis=1)
    
    def removeUnusedVars(self, df):
        return df.drop(['X', 'conds', 'datetime', 'icon', 'visi', 'wdird', 'wdire', 'Unnamed: 0'], axis=1)
    
    def splitSet(self, df):
        # create training (80%) and test (20%) sets
        X_train, X_test, y_train, y_test = train_test_split(df[df.columns.difference(['Value'])], df.Value, test_size=0.2, random_state=42)
        return X_train, X_test, y_train, y_test
    
    def buildForest(self, X_train, y_train):
        rf = RandomForestRegressor(n_estimators=50, verbose=1, n_jobs=4)
        rf.fit_transform(X_train, y_train)
        return rf
    
    def metrics(self, y_test, X_test, rf):
        self.r2 = r2_score(y_test, rf.predict(X_test))
        self.mse = np.mean((y_test - rf.predict(X_test))**2)
        self.rmse = np.sqrt(mse)
    
    def plotMetrics(self):
        measures = DataFrame({"feature_importances_": self.rf.feature_importances_, "names" : X_train.columns})
        #ggplot(measures, aes(x='names', y='feature_importances_')) + geom_bar(stat='bar') + theme(axis_text_x = element_text(angle = 90, hjust = 1))
        
        