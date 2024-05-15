from initialize import Base
from sqlalchemy import Column, DateTime, Numeric

class Price_data(Base):
    __tablename__ = 'price_data'
    
    datetime = Column(DateTime(), primary_key=True)
    price = Column(Numeric(15,6))