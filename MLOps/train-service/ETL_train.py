from sqlalchemy import create_engine, text
import pandas as pd
import logging
from initialize import logger
from connect_unix import get_connect_url_feature_service

logger.log(logging.INFO, "ETL_train.py starting")

### EXTRACT ###
db_url = get_connect_url_feature_service()
try:
    engine = create_engine(db_url)
    connection = engine.connect()
    logger.log(logging.INFO, "database connection successful")
    result = connection.execute(text("SELECT version()"))
    logger.log(logging.INFO, result.fetchone()[0])
    
    # Create dataframe
    query = "SELECT * FROM price_data"
    connection = engine.connect()
    result = connection.execute(text(query))
    df_ETL_train = pd.DataFrame(result.fetchall(), columns=result.keys())
    logger.log(logging.INFO, "df_ETL_train created")
    connection.close()
    logger.log(logging.INFO, "database connection closed")
except:
    logger.log(logging.INFO, "database does not exist or connection invalid")

### TRANSFORM ###
logger.log(logging.INFO, "df_ETL_train: " + str(list(df_ETL_train.isnull().sum())) + " missing values found")
df_ETL_train = df_ETL_train.fillna(method='ffill')  # forward fill missing values
df_ETL_train = df_ETL_train.sort_values(by='datetime').reset_index(drop=True)
n = 6  # down sample to 6*10 seconds = 1 minute frequency
df_ETL_train = df_ETL_train.iloc[::n]
logger.log(logging.INFO, "df_ETL_train: missing values filled and downsampling complete")

df_ETL_train['price_running_average'] = df_ETL_train['price'].rolling(window=12).mean() # running average
df_ETL_train = df_ETL_train.dropna() # drop initial reference rows
minutes = 60*4*2 # Slice to 8 hours
df_ETL_train = df_ETL_train[-int(minutes):]
logger.log(logging.INFO, "df_ETL_train: smoothing to running average and resizing complete")

### LOAD ###
df_ETL_train['price'] = df_ETL_train['price_running_average'].astype(float)
df_ETL_train = df_ETL_train[['datetime', 'price_running_average']].reset_index(drop=True)
new_column_names = {'datetime': 'datetime', 'price_running_average': 'price'}
df_ETL_train.rename(columns=new_column_names, inplace=True)
logger.log(logging.INFO, "df_ETL_train: update datatype and column names")

df_ETL_train.to_csv('df_ETL_train.csv', index=False)
logger.log(logging.INFO, "df_ETL_train: save and load CSV file")
logger.log(logging.INFO, "ETL_train.py complete")