# Chain-Factory Kubernetes Cluster Resources

## This is a collection of resources that are used to create chain-factory on Kubernetes.

## Steps to do

1. clone repository https://gitlab.devops.telekom.de/dws/portal-and-automation/chain-factory-kubernetes.git
2. setup the backend resources: rabbitmq, redis, mongodb
3. rabbitmq
   1. cd rabbitmq
   2. kubectl apply -f namespace.yml
   3. kubectl apply -f configmap.yml
   4. kubectl apply -f headless-service.yml
   5. kubectl apply -f cookie.yml
   6. kubectl apply -f admin-account.yml
   7. kubectl apply -f rbac.yml
   8. kubectl apply -f statefulset.yml
4. redis
   1. cd redis
   2. kubectl apply -f namespace.yml
   3. kubectl apply -f configmap.yml
   4. kubectl apply -f headless-service.yml
   5. kubectl apply -f statefulset.yml
5. mongodb
   1. cd mongodb
   2. helm install --name mongodb01 --namespace mongodb -f values.yml bitnami/mongodb
6. setup the rest-api
   1. cd rest-api
   2. kubectl apply -f namespace.yml
   3. kubectl apply -f secrets.yml
   4. kubectl apply -f headless-service.yml
   5. kubectl apply -f deployment.yml
7. setup the worker-node
   1. cd worker-node
   2. kubectl apply -f namespace.yml
   3. kubectl apply -f secrets.yml
   4. kubectl apply -f deployment.yml
8. setup the webui
   1. cd webui
   2. kubectl apply -f namespace.yml
   3. kubectl apply -f secrets.yml
   4. kubectl apply -f deployment.yml