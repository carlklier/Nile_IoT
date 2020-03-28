#!/bin/sh
python3.7 -m locust -f ./data_flow_locust.py --slave --master-host=localhost
