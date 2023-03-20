#!/bin/bash

kubectl port-forward svc/mongodb 27017:27017 &
kubectl port-forward svc/redis-master 6379:6379 &
kubectl port-forward svc/rabbitmq 5672:5672 &

# wait for the background jobs to finish
wait