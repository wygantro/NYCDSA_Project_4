#!/bin/bash

while true; do
    python ETL_predict.py
    wait

    python predict.py 
    wait

done