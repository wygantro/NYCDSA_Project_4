from sqlalchemy import create_engine, inspect, text
import logging
import sys
from connect_unix import get_connect_url_feature_service

# initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s] %(levelname)s:dashboard:%(lineno)d:%(message)s")
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
file_handler = logging.FileHandler("runtime_logs.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# db url connection and create engine
db_url = get_connect_url_feature_service()

try:
    # connect and create engine
    engine = create_engine(db_url)
    connection = engine.connect()
    result = connection.execute(text("SELECT version()"))
    logger.log(logging.INFO, 'database exists: ' + str(result.fetchone()[0]))
    connection.close()
    logger.log(logging.INFO, "database connection closed")
    
    # initial database inspection (tables and columns)
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    if len(table_names) < 1:
        logger.log(logging.INFO, "tables do not exist")
        
    else:
        logger.log(logging.INFO, "Tables exist")
        for table_name in table_names:
            logger.log(logging.INFO, f"Table: {table_name}")
    
except:
    logger.log(logging.INFO, "database does not exist or connection invalid")
    connection.close()
    logger.log(logging.INFO, "database connection closed")