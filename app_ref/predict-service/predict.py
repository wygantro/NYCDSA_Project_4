import pandas as pd
import logging
from initialize import session, logger
from models import Model_train_directory
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
import time
from datetime import datetime, timedelta
from connect_unix import get_connect_url_feature_service
from sqlalchemy import create_engine, text
from models import Predict_model_summary, Predict_results

logger.log(logging.INFO, "predict.py starting")

try:
    logger.log(logging.INFO, 'query best parameters from model_train_directory and convert to list of integers')
    query = session.query(Model_train_directory).order_by(Model_train_directory.train_datetime.desc()).all()
    best_params_query = query[0].best_params_mse
    best_params = (int(best_params_query[1]), int(best_params_query[4]), int(best_params_query[7]))
    best_params_model_id = query[0].model_id
    logger.log(logging.INFO, f"best parameters: {best_params} for model {best_params_model_id}")
    session.close()
    logger.log(logging.INFO, "connection closed")

except:
    logger.log(logging.WARNING, "database does not exist or connection invalid")
    session.rollback()

# load dataframe to fit model
logger.log(logging.INFO, "loading df_ETL_predict.csv")
df = pd.read_csv('df_ETL_predict.csv')
df_start_time = df['datetime'].tolist()[0]
df_lst = df['price'].tolist() #list of fit data
logger.log(logging.INFO, f"df start time: {df_start_time}")

# fit the ARIMA model with the best parameters
logger.log(logging.INFO, "refitting ARIMA model and loading best parameters")
model = ARIMA(df_lst, order=best_params)
trained_model = model.fit()

logger.log(logging.INFO, "forecasting price list")
predict_start_time = datetime.now()
prediction_id = f"ARIMA_model_v1_{best_params[0]}_{best_params[0]}_{best_params[0]}_{predict_start_time}" # predict model id
prediction_period = 30 # forecast 30 minutes in future
prediction_price_lst = trained_model.forecast(prediction_period)

# connect to feature-service database
db_url = get_connect_url_feature_service()

# batch commit prediction date and price pair
try:
    engine = create_engine(db_url)
    connection = engine.connect()
    logger.log(logging.INFO, "feature-service-db connection successful")

    # query latest datetime value from database
    query = """
        SELECT * FROM public.price_data
        ORDER BY datetime DESC
        LIMIT 1;
        """
    connection = engine.connect()
    result = connection.execute(text(query)).fetchall()
    start_datetime = result[0][0]
    timestep_lst = list(range(1, prediction_period+1, 1))

    # create datetime prediction list for batch insert
    datetime_predict_lst = [start_datetime + timedelta(minutes=value) for value in timestep_lst]

    # add and commit prediction date and price pair
    for i in list(range(0, prediction_period)):
        prediction_insert_values = Predict_results(datetime=datetime_predict_lst[i],
                                                   model_id_ref=best_params_model_id,
                                                   predict_id_ref=prediction_id,
                                                   predict_price=prediction_price_lst[i])
        session.add(prediction_insert_values)
        session.commit()

except:
    logger.log(logging.WARNING, "database does not exist or connection invalid")
    session.rollback()
    logger.log(logging.INFO, "rollback session")

finally:
    session.close()
    logger.log(logging.INFO, "database connection closed")

# commit update for actual price loop every 60 seconds
try:
    engine = create_engine(db_url)
    connection = engine.connect()
    logger.log(logging.INFO, "feature-service-db connection successful")

    actual_price_lst = []
    for i in list(range(0, prediction_period)):
        start_time = time.time()
        time.sleep(60)
        # get datetime and current price from feature-service db
        logger.log(logging.INFO, "query current price")
        query = """
            SELECT * FROM public.price_data
            ORDER BY datetime DESC
            LIMIT 1;
            """
        connection = engine.connect()
        result = connection.execute(text(query)).fetchall()
        datetime = result[0][0]
        actual_price = result[0][1]

        datetime_latency = datetime - datetime_predict_lst[i]
        logger.log(logging.INFO, f"datetime latency : {datetime_latency}")

        # MSE calculation
        actual_price_lst.append(float(actual_price))    
        predict_mse = mean_squared_error(actual_price_lst, prediction_price_lst[:i+1])

        # match predict datetime index value with database object and update actual pricea and current prediction mse
        predict_row_update = session.get(Predict_results, datetime_predict_lst[i])
        logger.log(logging.INFO, "update database object with actual price and commit")
        predict_row_update.actual_price = actual_price
        predict_row_update.predict_moving_mse = predict_mse
        session.commit()

except:
    logger.log(logging.WARNING, "database does not exist or connection invalid")
    session.rollback()
    logger.log(logging.INFO, "rollback session")

finally:
    session.close()
    logger.log(logging.INFO, "database connection closed")

# update and commit prediction summary values after prediction_period
try:
    engine = create_engine(db_url)
    connection = engine.connect()
    logger.log(logging.INFO, "feature-service-db connection successful")
    
    logger.log(logging.INFO, "adding prediction_summary_insert_values")
    prediction_summary_insert_values = Predict_model_summary(predict_id=prediction_id,
                                                             model_id_ref=best_params_model_id,
                                                             predict_start_time=predict_start_time,
                                                             predict_end_time=datetime.now(),
                                                             predict_mse_score=predict_mse)
    session.add(prediction_summary_insert_values)
    session.commit()
    logger.log(logging.INFO, "prediction_summary_insert_values committed")

except:
    logger.log(logging.WARNING, "database does not exist or connection invalid")
    session.rollback()
    logger.log(logging.INFO, "rollback session")

finally:
    session.close()
    logger.log(logging.INFO, "database connection closed")