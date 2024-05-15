#!/bin/bash

while true; do
    python ETL_train.py
    wait
    python train.py
    wait

    sleep 3600
done