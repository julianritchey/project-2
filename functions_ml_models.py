import pandas as pd
import pickle
import os
import numpy as np


def build_df(age, kids, net_worth, income, marriage):  
    if marriage.lower() == 'yes':
        marriage = 1
    elif marriage.lower() == 'no':
        marriage = 2
    user = {'AGE':age, 'KIDS':kids, 'NET WORTH':net_worth, 'INCOME':income, 'MARRIAGE':marriage}
    df = pd.DataFrame(user, index = [0])
    return df

def load_model(model_name):
    with open('models/' + model_name + '.pkl', 'rb') as file:
        model = pickle.load(file)
    return model

def predict_risk_score(model, df):
    risk_level = model.predict(df)
    return risk_level[0]

def list_saved_models():
    saved_models = []
    directory = 'models'
    for filename in os.listdir(directory):
        if filename.endswith('.pkl'):
            model_name = filename[:-4]  # Remove the file extension (.pkl)
            saved_models.append(model_name)
    return saved_models


def get_feature_importances(model, X):
    feature_importances = model.feature_importances_
    importances_dict = dict(zip(X.columns, feature_importances))
    return importances_dict

def evaluate_model(model, X, y):
    y_pred = model.predict(X)
    accuracy = accuracy_score(y, y_pred)
    return accuracy

def preprocess_input(df):
    # Perform any necessary preprocessing steps here
    # For example, you can scale numerical features or encode categorical variables
    # Make sure to handle missing values as well
    return df

def predict_risk_tolerance(model, df):
    preprocessed_df = preprocess_input(df)
    risk_tolerance = model.predict(preprocessed_df)
    return risk_tolerance[0]

def validate_input(age, kids, net_worth, income, marriage):
    # Implement your validation logic here
    # Check for missing or invalid values in the user input
    # Return appropriate error messages or indicators if validation fails
    return True  # or False, depending on the validation result

def display_result(risk_tolerance):
    # Format and display the predicted risk tolerance in a user-friendly manner
    print('Predicted Risk Tolerance: {}'.format(risk_tolerance))
