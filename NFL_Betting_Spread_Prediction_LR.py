#!/usr/bin/env python
# coding: utf-8

# ### This is a program to predict points per team in NFL games.  The data is from:
#  https://www.pro-football-reference.com/
#  https://sonnymoorepowerratings.com/nfl-foot.htm
#  https://www.nflweather.com/en/
#  https://www.footballoutsiders.com/    

# In[116]:


# importing required libraries
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn import linear_model
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score
from sklearn.ensemble import  RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.compose import ColumnTransformer 
from sklearn.impute import SimpleImputer
from sklearn import preprocessing
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats


# In[117]:


# read the training data
train_data = pd.read_csv('~/NFL_Modeling/alloff.csv')


# In[118]:



# select feature variables to be scaled
features = train_data.iloc[:,16:]

max_abs_scaler = preprocessing.MaxAbsScaler()

#fit and transform and save as X 
X = max_abs_scaler.fit_transform(features)



# In[119]:


def aroptTrainingObject(train_x, test_x, train_y, test_y):
    # create a list of alphas
    alphas = [vala/100 for vala in range(10, 100,5)]
    # create a list of ratios
    ratios = [valb/100 for valb in range(0, 100)]
    accvar = 0


    for alpha in alphas:
        for ratio in ratios:

            # instantiate the classifier
            model_LR = linear_model.ElasticNet(l1_ratio=ratio, alpha=alpha, max_iter=1000000)

            # fit the classifier to the training data
            model_LR.fit(train_x, train_y)

            # predict with the classifier using the .predict() function
            pred_y = model_LR.predict(test_x)

            # view the model accuracy with the accuracy_score() function, Accuracy: 16.0% | penalty = 0.7, C = 0.1
            accuracy = model_LR.score(test_x, test_y)
            accuracy_rd = round(accuracy*100,1)
            if accuracy_rd > accvar:
                accvar = accuracy_rd
                avar = alpha
                rvar = ratio
    return avar, rvar


# In[120]:


def optinTrainingObject(train_x, test_x, train_y, test_y, avar, rvar):
    # optimal penalty and C
    accvar = 0

    options = [True, False]

    for option in options:
        intercept = option
        for option in options:

            # instantiate the classifier
            model_LR = linear_model.ElasticNet(l1_ratio=ratio, alpha=avar, fit_intercept = intercept, normalize = option, 
                                               max_iter=1000000)

            # fit the classifier to the training data
            model_LR.fit(train_x, train_y)

            # predict with the classifier using the .predict() function
            pred_y = model_LR.predict(test_x)

            # view the model accuracy with the accuracy_score() function
            accuracy = model_LR.score(test_x, test_y)
            accuracy_rd = round(accuracy*100,1)
            if accuracy_rd > accvar:
                accvar = accuracy_rd
                ivar = intercept
                ovar = option

    return ivar, ovar


# In[121]:


# set the test size and hyperparameters
def optthTrainingObject(train_x, test_x, train_y, test_y, avar, rvar, ivar, ovar):
    
    accvar = 0

    # create a list of test_sizes
    test_sizes = [val/200 for val in range(30, 150)]

    for test_size in test_sizes:

        # train-test split
        train_x, test_x, train_y, test_y = train_test_split(X, y, test_size=test_size, random_state=42)

        # instantiate the classifier
        model_LR = linear_model.ElasticNet(l1_ratio=rvar, alpha=avar, fit_intercept = ivar, normalize = ovar, 
                                                   max_iter=1000000)

        # fit the classifier to the training data
        model_LR.fit(train_x, train_y)

        # predict with the classifier using the .predict() function
        pred_y = model_LR.predict(test_x)

        # view the model accuracy with the accuracy_score() function
        accuracy = model_LR.score(test_x, test_y)
        accuracy_rd = round(accuracy*100,1)
        if accuracy_rd > accvar:
            accvar = accuracy_rd
            testvar = test_size

    return testvar


# In[122]:


predictweek = pd.read_csv('~/NFL_Modeling/tomodel.csv')

# select just the game stats
new_X = predictweek.loc[:,features.columns]


# standardize using original data's scaling
new_X_sc = max_abs_scaler.fit_transform(new_X)


# In[124]:


# There may be warning message about some of the combinations not converging.  It is ok to disregard these messages and continue.
listys = ["spread", "PtsW", "PtsL", "YdsW", "YdsL", "PtsTotal"]

for listy in listys:
    y = train_data[listy]
    
    # randomly split the data
    train_x, test_x, train_y, test_y = train_test_split(X, y,test_size=0.5, random_state=42)
    
    # create an object of the LinearRegression Model
    model_LR = linear_model.ElasticNet()

    # fit the model with the training data
    model_LR.fit(train_x, train_y)

    # predict the target on train and test data 
    predict_train_LR = model_LR.predict(train_x)
    predict_test_LR  = model_LR.predict(test_x)

    #calculate score:
    score = model_LR.score(test_x, test_y)
    
    if score > 0:
        aropt = aroptTrainingObject(train_x, test_x, train_y, test_y)
        avar = aropt[0]
        rvar = aropt[1]
        optin = optinTrainingObject(train_x, test_x, train_y, test_y, avar, rvar)
        ivar = optin[0]
        ovar = optin[1]
        testvar = optthTrainingObject(train_x, test_x, train_y, test_y, avar, rvar, ivar, ovar)
      
        
        # train-test split
        train_x, test_x, train_y, test_y = train_test_split(X, y, test_size=testvar, random_state=42)

        # instantiate the classifier
        model_LR = linear_model.ElasticNet(l1_ratio=rvar, alpha=avar, fit_intercept = ivar, normalize = ovar, 
                                                   max_iter=1000000)

        # fit the classifier to the training data
        model_LR.fit(train_x, train_y)

        # predict with the classifier using the .predict() function
        pred_y = model_LR.predict(test_x)
        
        new_preds = model_LR.predict(new_X_sc)
        intpred = []

        for pred in new_preds:
            intpred.append(pred)
            
        print(intpred)
        predictweek[listy] = intpred
            
        
    
    


# In[125]:


predictweek.to_csv('C:\\Users\\sarae\\Desktop\\NFL_Modeling\\predictweek.csv')

