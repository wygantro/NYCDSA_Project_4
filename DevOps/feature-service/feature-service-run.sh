#!/bin/bash

# run the initial Python script
python initialize.py
sleep 10

# stream websocket data and run.py in parallel
python websocket_conn.py &
python run.py &

wait