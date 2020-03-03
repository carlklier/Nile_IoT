#!/bin/sh
python3.7 -m locust -f ./locust_file.py --slave --master-host=localhost
