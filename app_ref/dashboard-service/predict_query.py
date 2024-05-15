from initialize import logger
import logging
import time
from sqlalchemy import create_engine, text
from connect_unix import get_connect_url_feature_service, get_connect_url_train_service
import json

import os
import pandas as pd

# check and initialize current price dataframe
if not os.path.exists('dashboard_current_price_df.csv'):
    current_datetime = 0
    dashboard_current_price_df = pd.DataFrame({'current_datetime':[],
                                               'current_price':[]})
    logger.log(logging.INFO, "current price dataframe created")

else:
    dashboard_current_price_df = pd.read_csv('dashboard_current_price_df.csv')
    current_datetime = dashboard_current_price_df.iloc[-1]['current_datetime']
    logger.log(logging.INFO, "current price dataframe already exists")

# check and initialize preict price dataframe
if not os.path.exists('dashboard_predict_price_df.csv'):
    predict_current_datetime = 0
    dashboard_predict_price_df = pd.DataFrame({'predict_datetime':[],
                                               'actual_price':[],
                                               'predict_price':[]})
    logger.log(logging.INFO, "predict price dataframe created")
else:
    dashboard_predict_price_df = pd.read_csv('dashboard_predict_price_df.csv')
    logger.log(logging.INFO, "predict price dataframe already exists")

s = time.perf_counter()
time.sleep(5)

engine = create_engine(get_connect_url_feature_service())
with engine.connect() as connection:
    logger.log(logging.INFO, "feature-service-db connection successful")
    try:
        # current price update from feature-service      
        logger.log(logging.INFO, "query started from feature-service-db")
        price_data_query = """
                        SELECT * FROM public.price_data
                        ORDER BY datetime DESC
                        LIMIT 1;
                        """
        price_data_query_result = connection.execute(text(price_data_query)).fetchall()
        price_data_query_datetime = price_data_query_result[0][0]
    
        logger.log(logging.INFO, "query complete from feature-service-db")

        # update current price data
        if price_data_query_datetime != current_datetime:
            logger.log(logging.INFO, "updating dashboard_current_price_df")
            current_datetime = price_data_query_datetime
            current_price = price_data_query_result[0][1]
            current_price_data_lst = list((current_datetime, current_price))

            dashboard_current_price_df.loc[len(dashboard_current_price_df)] = current_price_data_lst
            dashboard_current_price_df.tail(600).to_csv('dashboard_current_price_df.csv', index=False)
            logger.log(logging.INFO, "update complete and saving dashboard_current_price_df")

    except:
        connection.close()
        logger.log(logging.INFO, "connection closed")

# predict price update from predict-service
engine = create_engine(get_connect_url_train_service())
with engine.connect() as connection:
    logger.log(logging.INFO, "query started from predict-service-db")
    try:
        predict_data_query = """
                        SELECT * FROM public.predict_results
                        ORDER BY datetime DESC
                        LIMIT 30;
                        """
        predict_data_query_result = connection.execute(text(predict_data_query)).fetchall()
        predict_data_query_count = [predict_data_query_result[i][3] for i in list(range(len(predict_data_query_result)-1))].count(None)
        predict_data_query_datetime = predict_data_query_result[predict_data_query_count][0]
        predict_data_df_count = dashboard_predict_price_df['actual_price'].shape[0] - dashboard_predict_price_df['actual_price'].dropna().shape[0]

        if predict_data_query_count != predict_data_df_count:
            logger.log(logging.INFO, "updating dashboard_predict_price_df data")
            predict_current_datetime = predict_data_query_datetime
            dashboard_predict_price_df = pd.DataFrame({'predict_datetime':[],
                                                        'actual_price':[],
                                                        'predict_price':[]})

            for row in predict_data_query_result:
                dashboard_predict_price_lst = list((row.datetime, row.actual_price, row.predict_price))
                dashboard_predict_price_df.loc[len(dashboard_predict_price_df)] = dashboard_predict_price_lst
        
        dashboard_predict_price_df = dashboard_predict_price_df.sort_values(by='predict_datetime').reset_index(drop=True)
        dashboard_predict_price_df.to_csv('dashboard_predict_price_df.csv', index=False)
        logger.log(logging.INFO, "update complete and saving dashboard_predict_price_df")

        elapsed = time.perf_counter() - s
        logger.log(logging.INFO, f"query loop time: {elapsed}")

    except:
        connection.close()
        logger.log(logging.INFO, "connection closed")

current_datetime = dashboard_current_price_df['current_datetime'].iloc[-1]

# date
date_str = current_datetime.strftime('%Y-%m-%d')

# current time
current_time_est = current_datetime.tz_localize('UTC').tz_convert('US/Eastern').time()
h, m, s = current_time_est.hour, current_time_est.minute, current_time_est.second
current_time_est_str = f"{h:02d}:{m:02d}:{s:02d} EST"

# current price
current_price = dashboard_current_price_df['current_price'].iloc[-1]
current_price_str = "${:,.2f}".format(current_price)

# prediction start time
predict_datetime_start_str = dashboard_predict_price_df.iloc[0]['predict_datetime']
predict_datetime_start = pd.to_datetime(predict_datetime_start_str, format="%Y-%m-%d %H:%M:%S")
predict_datetime_start_est = predict_datetime_start.tz_localize('UTC').tz_convert('US/Eastern').time()
h, m, s = predict_datetime_start_est.hour, predict_datetime_start_est.minute, predict_datetime_start_est.second
predict_datetime_start_est_str = f"{h:02d}:{m:02d}:{s:02d} EST"

# prediction end time
predict_datetime_end_str = dashboard_predict_price_df['predict_datetime'].iloc[-1]
predict_datetime_end = pd.to_datetime(predict_datetime_end_str, format="%Y-%m-%d %H:%M:%S")
predict_datetime_end_est = predict_datetime_end.tz_localize('UTC').tz_convert('US/Eastern').time()
h, m, s = predict_datetime_end_est.hour, predict_datetime_end_est.minute, predict_datetime_end_est.second
predict_datetime_end_est_str = f"{h:02d}:{m:02d}:{s:02d} EST"

# next prediction in    
next_pred = predict_datetime_end.minute - current_time_est.minute
next_pred_str = f"{next_pred} minutes"

live_update_lst = [date_str, current_time_est_str, current_price_str, predict_datetime_start_est_str, predict_datetime_end_est_str, next_pred_str]

# save JSON formatted string to file
with open("live_update_lst.json", "w") as f:
    json.dump(live_update_lst, f)

elapsed = time.perf_counter() - s
logger.log(logging.INFO, f"query loop time: {elapsed}")