#!/bin/sh
locust -f ./examples/locust_file.py --no-web -c 1 -r 1 --run-time 1m --host http://google.com
