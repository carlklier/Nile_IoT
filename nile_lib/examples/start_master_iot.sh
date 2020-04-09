#!/bin/sh
locust -f ./examples/iot_example.py --master --expect-slaves=1 --no-web -c 1 -r 1 --run-time 1m --host=http://google.com
