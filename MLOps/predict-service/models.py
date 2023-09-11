from initialize import Base
from sqlalchemy import Column, DateTime, Float, LargeBinary, String, Integer, Numeric

class Model_train_directory(Base):
    __tablename__ = 'model_train_directory'

    model_id = Column(String, primary_key=True)  
    train_datetime = Column(DateTime())
    model_info = Column(String)
    df_start_time = Column(String)
    df_end_time = Column(String)
    train_test_df = Column(LargeBinary)
    test_size_minutes = Column(Integer)
    best_score_mse = Column(Float)
    best_params_mse = Column(String)

class Predict_model_summary(Base):
    __tablename__ = 'predict_model_summary'

    predict_id = Column(String, primary_key=True)
    model_id_ref = Column(String) 
    predict_start_time = Column(DateTime())
    predict_end_time = Column(DateTime())
    predict_mse_score = Column(Float)

class Predict_results(Base):
    __tablename__ = 'predict_results'

    datetime = Column(DateTime(), primary_key=True)
    model_id_ref = Column(String)
    predict_id_ref = Column(String)
    actual_price = Column(Numeric(15,6))
    predict_price = Column(Numeric(15,6))
    predict_moving_mse = Column(Float)