import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from imblearn.over_sampling import RandomOverSampler

# Function to split the data into training and testing sets
def split_data(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
    return X_train, X_test, y_train, y_test

# Function to train and evaluate the Random Forest Classifier
def train_rf_classifier(X_train, X_test, y_train, y_test):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    return model, accuracy, cm

# Function to train and evaluate the Gradient Boosting Classifier
def train_gradient_balanced(X_train, X_test, y_train, y_test):
    model = GradientBoostingClassifier(random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    return model, accuracy, cm

# Function to train and evaluate the Decision Tree Classifier
def train_dtree_balanced(X_train, X_test, y_train, y_test):
    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    return model, accuracy, cm

# Load the dataset
risk_tol_model = pd.read_csv('risk_tol_model.csv')

# Prepare the data
X = risk_tol_model[['AGE', 'KIDS', 'NET WORTH', 'INCOME', 'MARRIAGE']]
y = risk_tol_model['RISK TOLERANCE SCORE']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = split_data(X, y)

# Oversample the data using RandomOverSampler
oversampler = RandomOverSampler(random_state=42)
X_train_resampled, y_train_resampled = oversampler.fit_resample(X_train, y_train)

# Model selection widget
model_selection = st.sidebar.selectbox('Select Model', ('Random Forest Classifier', 'Gradient Boosting Classifier', 'Decision Tree Classifier', 'Random Balanced'))

# Model 1: Random Forest Classifier
if model_selection == 'Random Forest Classifier':
    st.subheader('Random Forest Classifier')
    rf_model, rf_accuracy, rf_cm = train_rf_classifier(X_train, X_test, y_train, y_test)

    # Display accuracy
    st.write("Accuracy:", rf_accuracy)

    # Display value counts for y_train
    st.write("y_train value counts:")
    st.write(y_train.value_counts())

    # Display classification report
    st.write("Classification Report:")
    y_pred_rf = rf_model.predict(X_test)
    st.write(classification_report(y_test, y_pred_rf))

    # Display confusion matrix
    cm_rf_df = pd.DataFrame(rf_cm, columns=rf_model.classes_, index=rf_model.classes_)
    st.write("Confusion Matrix:")
    st.write(cm_rf_df)

# Model 2: Gradient Boosting Classifier
elif model_selection == 'Gradient Boosting Classifier':
    st.subheader('Gradient Boosting Classifier')
    gradient_balanced_model, gradient_balanced_accuracy, gradient_balanced_cm = train_gradient_balanced(X_train, X_test, y_train, y_test)

    # Display accuracy
    st.write("Accuracy:", gradient_balanced_accuracy)

    # Display value counts for y_train
    st.write("y_train value counts:")
    st.write(y_train.value_counts())

    # Display classification report
    st.write("Classification Report:")
    y_pred_gb = gradient_balanced_model.predict(X_test)
    st.write(classification_report(y_test, y_pred_gb))

    # Display confusion matrix
    cm_gb_df = pd.DataFrame(gradient_balanced_cm, columns=gradient_balanced_model.classes_, index=gradient_balanced_model.classes_)
    st.write("Confusion Matrix:")
    st.write(cm_gb_df)

# Model 3: Decision Tree Classifier
elif model_selection == 'Decision Tree Classifier':
    st.subheader('Decision Tree Classifier')
    dtree_balanced_model, dtree_balanced_accuracy, dtree_balanced_cm = train_dtree_balanced(X_train, X_test, y_train, y_test)

    # Display accuracy
    st.write("Accuracy:", dtree_balanced_accuracy)

    # Display value counts for y_train
    st.write("y_train value counts:")
    st.write(y_train.value_counts())

    # Display classification report
    st.write("Classification Report:")
    y_pred_dt = dtree_balanced_model.predict(X_test)
    st.write(classification_report(y_test, y_pred_dt))

    # Display confusion matrix
    cm_dt_df = pd.DataFrame(dtree_balanced_cm, columns=dtree_balanced_model.classes_, index=dtree_balanced_model.classes_)
    st.write("Confusion Matrix:")
    st.write(cm_dt_df)

# Model 4: Random Balanced
elif model_selection == 'Random Balanced':
    st.subheader('Random Balanced')
    random_balanced_model, random_balanced_accuracy, random_balanced_cm = train_rf_classifier(X_train_resampled, X_test, y_train_resampled, y_test)

    # Display accuracy
    st.write("Accuracy:", random_balanced_accuracy)

    # Display value counts for y_train
    st.write("y_train value counts:")
    st.write(pd.Series(y_train_resampled).value_counts())

    # Display classification report
    st.write("Classification Report:")
    y_pred_random_balanced = random_balanced_model.predict(X_test)
    st.write(classification_report(y_test, y_pred_random_balanced))

    # Display confusion matrix
    cm_random_balanced_df = pd.DataFrame(random_balanced_cm, columns=random_balanced_model.classes_, index=random_balanced_model.classes_)
    st.write("Confusion Matrix:")
    st.write(cm_random_balanced_df)
