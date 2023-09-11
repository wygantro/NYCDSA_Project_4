import pandas as pd
import numpy as np
import logging
from initialize import session, logger
from models import Model_train_directory
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from itertools import product
import warnings
import time
from datetime import datetime
import json
from io import BytesIO

logger.log(logging.INFO, "train.py starting")

logger.log(logging.INFO, "loading df_ETL_train.csv")
df = pd.read_csv('df_ETL_train.csv')
df_start_time = df['datetime'].tolist()[0]
logger.log(logging.INFO, "df start time: " + df_start_time)

df_end_time = df['datetime'].tolist()[-1]
logger.log(logging.INFO, "df end time: " + df_end_time)

logger.log(logging.INFO, "split into train and test data")
minutes = 30 # 30 minute test split
price_data_lst = df['price'].tolist()
train_size = int(len(price_data_lst) - minutes)

train_data = price_data_lst[:train_size]
logger.log(logging.INFO, "train data range " + str(len(train_data)) + " minutes")

test_data = price_data_lst[train_size:]
logger.log(logging.INFO, "test data range " + str(len(test_data)) + " minutes")

logger.log(logging.INFO, "grid search starting")
# grid search for p,d,q ARIMA parameters
p_range = range(0, 3)
d_range = range(0, 3)
q_range = range(0, 3)
parameter_combinations = list(product(p_range, d_range, q_range))

# start the timer for grid search
start_time = time.time()

# ignore all UserWarnings temporarily
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=UserWarning)
    
    best_score = float('inf')
    best_params = None
    for p, d, q in parameter_combinations:
        try:
            # fit ARIMA model with the current parameter combination
            model = ARIMA(train_data, order=(p, d, q))
            results = model.fit()
            
            # calculate a performance metrics for model evaluation
            aic = results.aic
            test_predictions = results.forecast(len(test_data))
            mse = mean_squared_error(test_data, test_predictions)
            rmse = np.sqrt(mse)
            current_score = mse
            
            # update best parameters if the current model is better
            if current_score < best_score:
                best_score = current_score
                best_params = (p, d, q)
        
        except:
            continue

# calculate the elapsed time
end_time = time.time()
elapsed_time = end_time - start_time

logger.log(logging.INFO, "grid search complete")
logger.log(logging.INFO, f"grid search elasped time {elapsed_time:.4f} seconds")
logger.log(logging.INFO, "best score mean squared error from grid search " + str(best_score))
logger.log(logging.INFO, "best parameters from grid search " + str(best_params))

# aggregate results and commit to database
train_datetime = datetime.today()
model_info = repr(model)
df_start_time = df_start_time
df_end_time = df_end_time
test_size_minutes = int(minutes)
best_score_mse = best_score
best_params_mse = json.dumps(best_params)
model_id = f'{str(train_datetime).replace(" ", "_")}_{model_info[1:32]}'

# convert training DataFrame to Binary
binary_data = BytesIO()
df.to_pickle(binary_data)
df_binary = binary_data.getvalue()
logger.log(logging.INFO, "training dataframe converted to binary")

try:
    logger.log(logging.INFO, "adding values to train-service-db")
    model_train_update = Model_train_directory(model_id=model_id,
                                               train_datetime=train_datetime,
                                               model_info=model_info,
                                               df_start_time=df_start_time,
                                               df_end_time=df_end_time,
                                               train_test_df=df_binary,
                                               test_size_minutes=test_size_minutes,
                                               best_score_mse=best_score_mse,
                                               best_params_mse=best_params_mse)
    
    session.add(model_train_update)
    session.commit()
    session.close()
    logger.log(logging.INFO, "updated values committed to train-service-db")

except:
    session.rollback()
    logger.log(logging.INFO, "database does not exist or connection invalid")

logger.log(logging.INFO, "train.py complete")