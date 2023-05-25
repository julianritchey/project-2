# Project Plan

## Goal
Develop a real-time portfolio tracker that performs the following functions:
- Displays historic and existing investments from multiple exchanges.
- Stores historic and existing investments in a local database.
- Provides forecasting models for various investment assets.
- Displays data in tabular and graphical formats.

## Road map
1. Open trial investment accounts at various exchanges.
2. Initialize primary documents in their respective paths.
3. Prepare API functions, design and develop database, develop main application menu.
4. Pull, customize and organize initial data, develop database queries, develop displays for current and historic investments.
5. Pull, customize and organize remaining data, populate database with all data, develop display for portfolio forecasting.
6. Test application.

## Tasks
### Preparation
1. Open trial accounts at various exchanges.

### Forecasting
1. Initialize forecasting.ipynb file in [Resources](https://github.com/julianritchey/project-1/tree/main/Resources "Application resources") folder.
2. Prepare API calls for portforlio forecasting.
3. Pull historic data for portfoolio forecasting of one asset.
4. Customize portfolio forecasting for first asset type.
5. Pull historic data for remaining assets.
6. Customize portfolio forecasting for remaining assets.

### Investment data
1. Initialize investments.ipynb file in [Resources](https://github.com/julianritchey/project-1/tree/main/Resources "Application resources") folder.
2. Prepare API calls for investment data collection.
3. Pull investment data from first exchange.
4. Organize investment data.
5. Pull investment data from remaining exchanges.
6. Organize investment data from remaining exchanges.

### Database
1. Initialize queries.ipynb file in [Resources](https://github.com/julianritchey/project-1/tree/main/Resources "Application resources") folder.  
2. Design database for storing investment data and portfolio forecasting data.
3. Develop database for storing investment data and portfolio forecasting data.
4. Develop database CRUD queries for application.
5. Populate database using application queries.

### Application
1. Initialize index.ipynb file in main repository.
2. Develop user input for main menu.
3. Develop display for current investments.
4. Develop display for historic investments.
5. Develop display for portfolio forecasting.

### Libraries and packages used
- uWSGI
- Flask
- Dash
- Pandas
- SQLAlchemy*
- Flask-SQLAlchemy*