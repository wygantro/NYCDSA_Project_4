# ./app/get_data.py

from datetime import datetime, timedelta

def round_down_dt(dt):
    """
    Round down datetime input to the nearest lower 15 minutes.

    Args:
        dt (datetime.datetime): database service string input

    Returns:
        datetime.datetime: rounded down datetime object   
    """

    minutes = (dt.minute // 15) * 15
    return dt.replace(minute=minutes, second=0, microsecond=0)

def round_up_dt(dt):
    """
    Round up datetime input to the nearest lower 15 minutes.

    Args:
        dt (datetime.datetime): database service string input

    Returns:
        datetime.datetime: rounded down datetime object   
    """

    if dt.minute % 15 == 0 and dt.second == 0 and dt.microsecond == 0:
        return dt
    return round_down_dt(dt) + timedelta(minutes=15)

def interpolate_value(current_time, lower_time, upper_time, lower_value, upper_value):
    """
    Interpolates value based on the current time within a range defined by lower and upper times.

    Args:
        current_time (datetime.datetime): current datetime object
        lower_time (datetime.datetime): lower bound datetime object
        upper_time (datetime.datetime): upper bound datetime object
        lower_value (float): value at the lower bound time
        upper_value (float): value at the upper bound time
    
    Returns:
        float: interpolated value
    """
    # check current_time is between lower_time and upper_time
    if not (lower_time <= current_time <= upper_time):
        raise ValueError("current time must be between lower time and upper time")

    # calculate total time span in seconds
    total_time_span = (upper_time - lower_time).total_seconds()
    
    # calculate elapsed time from lower_time to current_time in seconds
    elapsed_time = (current_time - lower_time).total_seconds()
    
    # calculate the proportion of the elapsed time to the total time span
    proportion = elapsed_time / total_time_span
    
    # interpolate value
    interpolated_value = lower_value + proportion * (upper_value - lower_value)
    interpolated_value = round(interpolated_value, 4)
    
    return interpolated_value