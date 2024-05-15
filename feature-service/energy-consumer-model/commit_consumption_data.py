# commit_consumption_data.py

from datetime import datetime
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.connect_db import connect_url
from app.models import Base, Energy_consumption_timeseries


# create connection engine and table
db_url = connect_url('energy-consumption-model')
engine = create_engine(db_url)
Base.metadata.create_all(engine)

# create Session object
Session = sessionmaker(bind=engine)
session = Session()

# load timeseries energy cosumption csv file
file_path = './data/USA_IL_Chicago_consumption_energy_timeseries.csv'
df = pd.read_csv(file_path)
df = df

# load timeseries energy cosumption csv file
# temperature lookup
file_path = './data/USA_IL_Chicago-OHare_temp_lookup.csv'
df_weather = pd.read_csv(file_path)

# dewpoint lookup
file_path = './data/USA_IL_Chicago-OHare_dewpoint_lookup.csv'
df_dewpoint = pd.read_csv(file_path)

# humidity lookup
file_path = './data/USA_IL_Chicago-OHare_humidity_lookup.csv'
df_humidity = pd.read_csv(file_path)

# Iterate over each row in the DataFrame and print it
for index, row in df.iterrows():
    # datetime string formatting
    datetime_str = row['Date'] + " " + row['Time']

    # convert the string to a datetime object
    datetime_format = "%m/%d/%Y %H:%M"
    datetime_object = datetime.strptime(datetime_str, datetime_format).replace(year=1)
    month = int(datetime_object.month),
    day = int(datetime_object.day),
    hour = int(datetime_object.hour),
    minute = int(datetime_object.minute),
    energy_consumption = float(row["Current Demand"])

    # lookup weather data
    temp_value = float(df_weather.iloc[hour[0], month[0]])
    dewpoint_value = float(df_dewpoint.iloc[hour[0], month[0]])
    humidity_value = float(df_humidity.iloc[hour[0], month[0]])

    # add noise to lookup weather data
    # temp value noise
    temp_value_max = float(df_weather.iloc[-2, month[0]])
    temp_value_min = float(df_weather.iloc[-1, month[0]])
    temp_value_range = temp_value_max - temp_value_min
    noise_level = 0.03  # 3% of the range
    temp_noise = np.random.uniform(-noise_level * temp_value_range, noise_level * temp_value_range)
    temp_value = temp_value + temp_noise

    # dewpoint value noise
    dewpoint_value_max = float(df_dewpoint.iloc[-2, month[0]])
    dewpoint_value_min = float(df_dewpoint.iloc[-1, month[0]])
    dewpoint_value_range = dewpoint_value_max - dewpoint_value_min
    noise_level = 0.03  # 3% of the range
    dewpoint_noise = np.random.uniform(-noise_level * dewpoint_value_range, noise_level * dewpoint_value_range)
    dewpoint_value = dewpoint_value + dewpoint_noise

    # humidity value noise
    humidity_value_max = float(df_humidity.iloc[-2, month[0]])
    humidity_value_min = float(df_humidity.iloc[-1, month[0]])
    humidity_value_range = humidity_value_max - humidity_value_min
    noise_level = 0.03  # 3% of the range
    humidity_noise = np.random.uniform(-noise_level * humidity_value_range, noise_level * humidity_value_range)
    humidity_value = humidity_value + humidity_noise


    # commit records to database
    try:
        new_record = Energy_consumption_timeseries(
            datetime_id=datetime_object,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            electric_demand=energy_consumption,
            temp_value=round(temp_value, 2),
            dewpoint_value=round(dewpoint_value, 2),
            humidity_value=round(humidity_value, 2),
            location_id = "USA_IL_Chicago"
            )
        session.add(new_record)
        session.commit()
        print(f"Record added successfully for {datetime_object}")

    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")

    finally:
        session.close()
