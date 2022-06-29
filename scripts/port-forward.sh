#! /bin/sh

kubectl port-forward svc/example-mongodb-svc 27017:27017 --namespace=mongodb-operator &
kubectl port-forward svc/rest-api-headless 8080:8000 --namespace=rest-api &
kubectl port-forward svc/mongo-express 8081:8081 --namespace=mongodb-operator &
kubectl port-forward svc/redis-commander 8082:8081 --namespace=redis &
kubectl port-forward svc/rabbitmq-headless 8083:15672 --namespace=rabbitmq &
kubectl port-forward svc/vault 8084:8200 --namespace=vault &

kubectl port-forward svc/loki-grafana 9090:80 --namespace=loki &
