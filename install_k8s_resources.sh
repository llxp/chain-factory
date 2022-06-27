# 1. mongodb operator
kubectl apply -f ./k3s/mongodb/namespace.yml
kubectl config set-context --current --namespace=mongodb-operator
helm repo add mongodb https://mongodb.github.io/helm-charts
helm repo update
helm install community-operator mongodb/community-operator --namespace=mongodb-operator
# 2. mongodb deployment
kubectl apply -f ./k3s/mongodb/mongodb.com_v1_mongodbcommunity_cr.yaml
# 3. mongo-express helm install
helm repo add cowboysysop https://cowboysysop.github.io/charts/
helm repo update
helm install mongo-express cowboysysop/mongo-express --namespace=mongodb-operator -f ./k3s/mongodb/values_express.yaml
# 4. redis deployment
kubectl apply -f ./k3s/redis/namespace.yml
kubectl config set-context --current --namespace=redis
kubectl apply -f ./k3s/redis/configmap.yml
kubectl apply -f ./k3s/redis/headless-service.yml
kubectl apply -f ./k3s/redis/secrets.yml
kubectl apply -f ./k3s/redis/statefulset.yml
# 5. rabbitmq deployment
kubectl apply -f ./k3s/rabbitmq/namespace.yml
kubectl config set-context --current --namespace=rabbitmq
kubectl apply -f ./k3s/rabbitmq/rbac.yml
kubectl apply -f ./k3s/rabbitmq/headless-service.yml
kubectl apply -f ./k3s/rabbitmq/configmap.yml
kubectl apply -f ./k3s/rabbitmq/cookie.yml
kubectl apply -f ./k3s/rabbitmq/admin-account.yml
kubectl apply -f ./k3s/rabbitmq/statefulset.yml
# 6. loki helm install
kubectl apply -f ./k3s/elk/namespace.yml
kubectl config set-context --current --namespace=loki
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm install loki grafana/loki-stack --namespace=loki -f ./k3s/elk/values_loki_default.yaml
# 7. vault helm install
kubectl apply -f ./k3s/vault/namespace.yml
kubectl config set-context --current --namespace=vault
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update
## create certificates for vault server
### generate root-ca key
openssl genrsa -out "./k3s/vault/cert/root-ca.key" 4096
### generate root-ca certificate signing request
openssl req -new -key "./k3s/vault/cert/root-ca.key" -out "./k3s/vault/cert/root-ca.csr" -sha256 -subj '/CN=Local Test Root CA'
### generate root-ca certificate
openssl x509 -req -days 3650 -in "./k3s/vault/cert/root-ca.csr" -signkey "./k3s/vault/cert/root-ca.key" -sha256 -out "./k3s/vault/cert/root-ca.crt" -extfile "./k3s/vault/cert/root-ca.cnf" -extensions root_ca
### generate server key
openssl genrsa -out "./k3s/vault/cert/server.key" 4096
### generate server certificate signing request
openssl req -new -key "./k3s/vault/cert/server.key" -out "./k3s/vault/cert/server.csr" -sha256 -subj '/CN=vault.svc.cluster.local'
### generate server certificate
openssl x509 -req -days 750 -in "./k3s/vault/cert/server.csr" -sha256 -CA "./k3s/vault/cert/root-ca.crt" -CAkey "./k3s/vault/cert/root-ca.key" -CAcreateserial -out "./k3s/vault/cert/server.crt" -extfile "./k3s/vault/cert/server.cnf" -extensions v3_req
### create root-ca secret
kubectl create secret generic tls-ca --from-file=./k3s/vault/cert/root-ca.crt --from-file=./k3s/vault/cert/root-ca.key
### create server secret
kubectl create secret generic tls-server --from-file=./k3s/vault/cert/server.crt --from-file=./k3s/vault/cert/server.key
### install helm chart
helm install vault hashicorp/vault --namespace=vault -f ./k3s/vault/override-values.yml
# 8. rest-api deployment
kubectl apply -f ./k3s/rest-api/namespace.yml
kubectl config set-context --current --namespace=rest-api
kubectl apply -f ./k3s/rest-api/secrets.yml
kubectl apply -f ./k3s/rest-api/headless-service.yml
kubectl apply -f ./k3s/rest-api/deployment.yml
# 9. worker deployment
kubectl apply -f ./k3s/worker/namespace.yml
kubectl config set-context --current --namespace=worker
kubectl apply -f ./k3s/worker/secrets.yml
kubectl apply -f ./k3s/worker/deployment.yml
# 10. authentication-api deployment
# 11. webui deployment