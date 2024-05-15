from initialize import session, logger
from models import Price_data
import logging
import json
import time
from datetime import datetime

def predict():
    n = 0
    logger.log(logging.INFO, 'run.py loop initialized')
    
    while True:
        s = time.perf_counter()
        time.sleep(10)
        try:
            with open('high_freq.json', 'r') as f:
                high_freq_data = json.load(f)
        except:
            logger.log(logging.WARNING, 'could not open high_freq.json')
            pass
        current_price = high_freq_data[-1]['p']
        current_datetime = datetime.today()
        
        try:
            logger.log(logging.INFO, 'adding price updated to feature-service-db')
            price_update = Price_data(datetime=current_datetime,
                                      price=current_price)
        
            session.add(price_update)
            session.commit()
            logger.log(logging.INFO, 'price update committed to feature-service-db')
        
        except:
            session.rollback()
            logger.log(logging.INFO, "database does not exist or connection invalid")

        elapsed = time.perf_counter() - s
        logger.log(logging.INFO, 'predict.py loop compute time: ' + str(elapsed) + ' seconds')

predict()