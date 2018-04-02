#!/bin/bash
set -x
for ip in "1.1.1.1" "8.8.8.8" "9.9.9.9" "208.67.222.222"; do 
echo "nameserver $ip" | sudo tee /etc/resolv.conf
python adns-benchmark.py alexa-top1k.txt
python adns-benchmark.py alexa-random1k.txt
done
