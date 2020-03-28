#!/bin/sh
locust -f ./locust_file.py --master --no-web -c 1 -r 1 --run-time 1m --host http://google.com
