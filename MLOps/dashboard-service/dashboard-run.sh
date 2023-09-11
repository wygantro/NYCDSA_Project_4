#!/bin/bash

# initialize
python predict_query.py
python model_summary_query.py
python update_monitoring_api.py
wait

python dashboard.py &

while true; do
    python predict_query.py &
    python model_summary_query.py &
    python update_monitoring_api.py
done