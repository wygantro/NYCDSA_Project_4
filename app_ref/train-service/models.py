from initialize import Base
from sqlalchemy import Column, DateTime, Float, LargeBinary, String, Integer

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