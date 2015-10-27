import rforest
import forecast

forest = rforest.forest(train=False)
frcast = forecast.forecast(forest.X_train.columns, forest.rf)