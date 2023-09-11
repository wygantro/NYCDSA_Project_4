from sqlalchemy import create_engine, text
import pandas as pd
import logging
from initialize import logger
from connect_unix import get_connect_url_feature_service

logger.log(logging.INFO, "ETL_predict.py starting")

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
    df_ETL_predict = pd.DataFrame(result.fetchall(), columns=result.keys())
    logger.log(logging.INFO, "df_ETL_predict created")
    connection.close()
    logger.log(logging.INFO, "database connection closed")
except:
    logger.log(logging.INFO, "database does not exist or connection invalid")

### TRANSFORM ###
logger.log(logging.INFO, "df_ETL_predict: " + str(list(df_ETL_predict.isnull().sum())) + " missing values found")
df_ETL_predict = df_ETL_predict.fillna(method='ffill')  # forward fill missing values
df_ETL_predict = df_ETL_predict.sort_values(by='datetime').reset_index(drop=True)
n = 6  # down sample to 6*10 seconds = 1 minute frequency
df_ETL_predict = df_ETL_predict.iloc[::n]
logger.log(logging.INFO, "df_ETL_predict: missing values filled and downsampling complete")

df_ETL_predict['price_running_average'] = df_ETL_predict['price'].rolling(window=12).mean() # running average
df_ETL_predict = df_ETL_predict.dropna() # drop initial reference rows
minutes = 60*4*2 # Slice to 8 hours
df_ETL_predict = df_ETL_predict[-int(minutes):]
logger.log(logging.INFO, "df_ETL_predict: smoothing to running average and resizing complete")

### LOAD ###
df_ETL_predict['price'] = df_ETL_predict['price_running_average'].astype(float)
df_ETL_predict = df_ETL_predict[['datetime', 'price_running_average']].reset_index(drop=True)
new_column_names = {'datetime': 'datetime', 'price_running_average': 'price'}
df_ETL_predict.rename(columns=new_column_names, inplace=True)
logger.log(logging.INFO, "df_ETL_predict: update datatype and column names")

df_ETL_predict.to_csv('df_ETL_predict.csv', index=False)
logger.log(logging.INFO, "df_ETL_predict: save and load CSV file")
logger.log(logging.INFO, "ETL_predict.py complete")