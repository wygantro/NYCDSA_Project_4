# ./energy_consumption_api.py

from flask import Flask, jsonify
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

app = Flask(__name__)

# Query Energy Consumption Data
@app.route('/api/v1/energy-consumption', methods=['GET'])
def get_energy_consumption_data():

    from app.connect_db import connect_url
    from app.get_data import interpolate_value, round_down_dt, round_up_dt
    from app.models import Energy_consumption_timeseries

    # current time, upper, and lower 15 min estimates
    current_time = datetime.now().replace(microsecond=0).replace(year=1)
    current_time_lower = round_down_dt(datetime.now()).replace(year=1)
    current_time_uppper = round_up_dt(datetime.now()).replace(year=1)

    try:
        # connect to db and create session
        db_url = connect_url('energy-consumption-model')
        engine = create_engine(db_url)
        session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=True)
        Session = scoped_session(session_factory)
        session = Session()

        # energy consumption data query
        values_lower = session.query(Energy_consumption_timeseries).filter(Energy_consumption_timeseries.datetime_id == current_time_lower).all()[0]
        values_upper = session.query(Energy_consumption_timeseries).filter(Energy_consumption_timeseries.datetime_id == current_time_uppper).all()[0]
        
        # interpolate queried values
        electric_demand = interpolate_value(current_time, current_time_lower, current_time_uppper,
                                            values_lower.electric_demand, values_upper.electric_demand)
        temp_value = interpolate_value(current_time, current_time_lower, current_time_uppper,
                                       values_lower.temp_value, values_upper.temp_value)
        dewpoint_value = interpolate_value(current_time, current_time_lower, current_time_uppper,
                                           values_lower.dewpoint_value, values_upper.dewpoint_value)
        humidity_value = interpolate_value(current_time, current_time_lower, current_time_uppper,
                                           values_lower.humidity_value, values_upper.humidity_value)
        location_id = values_lower.location_id

        # reformat to json
        data = {
            "time_stamp": datetime.now(),
            "electric_demand": electric_demand,
            "temp_value": temp_value,
            "dewpoint_value": dewpoint_value,
            "humidity_value": humidity_value,
            "location_id": location_id
            }
        session.close()
        return jsonify(data)    

    except Exception as e:
        session.rollback()
        return jsonify({'error': f'{e}'}), 500
    finally:
        Session.remove()


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')