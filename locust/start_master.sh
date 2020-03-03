#!/bin/sh
python3.7 -m locust -f ./locust_file.py --master --expect-slaves=1 --no-web -c 10 -r 1 --run-time 1m --host http://google.com
