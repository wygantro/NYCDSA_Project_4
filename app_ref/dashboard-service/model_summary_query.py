from initialize import logger
import logging
import time
from sqlalchemy import create_engine, text
from connect_unix import get_connect_url_train_service
import json

import pandas as pd

logger.log(logging.INFO, 'start and initialize model_summary_query loop')
engine = create_engine(get_connect_url_train_service())

s = time.perf_counter()
time.sleep(5)

with engine.connect() as connection:
    logger.log(logging.INFO, "train-service-db connection successful")
    
    try:
        # MSE score from prediction update
        logger.log(logging.INFO, "query started from predict-service-db")
        predict_data_query = """
                        SELECT * FROM public.predict_results
                        ORDER BY datetime DESC
                        LIMIT 30;
                        """
        predict_data_query_result = connection.execute(text(predict_data_query)).fetchall()
        running_mse_lst = [predict_data_query_result[i][5] for i in list(range(len(predict_data_query_result)))][::-1]

        with open("running_mse_lst.json", "w") as f:
            json.dump(running_mse_lst, f)
    
        # prediction model ranking
        model_ranking_query = """
                            SELECT * FROM public.predict_model_summary
                            ORDER BY predict_mse_score ASC;
                            """
        model_ranking_df = pd.read_sql(model_ranking_query, engine)

        model_ranking_df = model_ranking_df.drop(['model_id_ref', 'predict_start_time', 'predict_end_time'], axis=1)
        model_ranking_df = model_ranking_df.round(2)

        model_ranking_df.to_csv('model_ranking_df.csv', index=False)

        # current model info
        current_model_id = predict_data_query_result[0][1]

        # query model_train_directory
        current_model_info_query = f"""
                            SELECT * FROM public.model_train_directory
                            WHERE model_id = '{current_model_id}';
                            """
        current_model_info_result = connection.execute(text(current_model_info_query)).fetchall()

        current_model_train_datetime = current_model_info_result[0][1].strftime('%A %Y-%m-%d %H:%M')
        current_model_train_score = str(round(current_model_info_result[0][-2], 2))
        current_model_params = current_model_info_result[0][-1]

        # get average MSE from last N predictions
        predict_avg_mse_query = f"""SELECT AVG(predict_moving_mse) 
                                    FROM public.predict_results;
                                """
        predict_avg_mse_result = connection.execute(text(predict_avg_mse_query)).fetchall()
        predict_avg_mse = predict_avg_mse_result[0][0]
        current_model_info_lst = [current_model_id, current_model_train_datetime, current_model_train_score, current_model_params, predict_avg_mse]

        with open("current_model_info_lst.json", "w") as f:
            json.dump(current_model_info_lst, f)

    except:
        connection.close()
        logger.log(logging.INFO, "connection closed")
