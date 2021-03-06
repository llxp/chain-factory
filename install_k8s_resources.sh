trap "kill 0" EXIT
BASE_DOMAIN_ENV=${BASE_DOMAIN:-localhost}
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
cat ./k3s/mongodb/ingress.yml | sed "s/localhost/$BASE_DOMAIN_ENV/g" | kubectl apply -f -
while [[ $(kubectl get pods --all-namespaces -l app=example-mongodb-svc -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}' | grep "False") ]]; do echo "waiting for pod" && sleep 1; done
while [[ $(kubectl get pods --all-namespaces -l app.kubernetes.io/name=mongo-express -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for pod" && sleep 1; done
./scripts/provision_mongodb.sh
# 4. mongodb backup cronjob
kubectl apply -f ./k3s/backup/mongodb-secret.yml
kubectl apply -f ./k3s/backup/job.yml
# 5. redis deployment
kubectl apply -f ./k3s/redis/namespace.yml
kubectl config set-context --current --namespace=redis
kubectl apply -f ./k3s/redis/configmap.yml
kubectl apply -f ./k3s/redis/headless-service.yml
kubectl apply -f ./k3s/redis/secrets.yml
kubectl apply -f ./k3s/redis/statefulset.yml
cat ./k3s/redis/ingress.yml | sed "s/localhost/$BASE_DOMAIN_ENV/g" | kubectl apply -f -
while [[ $(kubectl get pods --all-namespaces -l app=redis -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}' | grep "False") ]]; do echo "waiting for pod" && sleep 1; done
# 6. rabbitmq deployment
kubectl apply -f ./k3s/rabbitmq/namespace.yml
kubectl config set-context --current --namespace=rabbitmq
kubectl apply -f ./k3s/rabbitmq/rbac.yml
kubectl apply -f ./k3s/rabbitmq/headless-service.yml
kubectl apply -f ./k3s/rabbitmq/configmap.yml
kubectl apply -f ./k3s/rabbitmq/cookie.yml
kubectl apply -f ./k3s/rabbitmq/admin-account.yml
kubectl apply -f ./k3s/rabbitmq/statefulset.yml
cat ./k3s/rabbitmq/ingress.yml | sed "s/localhost/$BASE_DOMAIN_ENV/g" | kubectl apply -f -
while [[ $(kubectl get pods --all-namespaces -l app=rabbitmq -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}' | grep "False") ]]; do echo "waiting for pod" && sleep 1; done
kubectl exec -it rabbitmq-0 -- rabbitmqctl add_user rest-api Start123
kubectl exec -it rabbitmq-0 -- rabbitmqctl set_user_tags rest-api administrator
kubectl exec -it rabbitmq-0 -- rabbitmqctl set_permissions -p / rest-api ".*" ".*" ".*"
# 7. loki helm install
kubectl apply -f ./k3s/elk/namespace.yml
kubectl config set-context --current --namespace=loki
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm install loki grafana/loki-stack --namespace=loki -f ./k3s/elk/values_loki_default.yaml
cat ./k3s/elk/ingress.yml | sed "s/localhost/$BASE_DOMAIN_ENV/g" | kubectl apply -f -
# 8. vault helm install
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
kubectl create secret generic tls-ca --from-file=tls.crt=./k3s/vault/cert/root-ca.crt --from-file=tls.key=./k3s/vault/cert/root-ca.key
### create server secret
kubectl create secret generic tls-server --from-file=tls.crt=./k3s/vault/cert/server.crt --from-file=tls.key=./k3s/vault/cert/server.key
### install helm chart
helm install vault hashicorp/vault --namespace=vault -f ./k3s/vault/override-values.yml
cat ./k3s/vault/ingress.yml | sed "s/localhost/$BASE_DOMAIN_ENV/g" | kubectl apply -f -
# 9. rest-api deployment
kubectl apply -f ./k3s/rest-api/namespace.yml
kubectl config set-context --current --namespace=rest-api
kubectl apply -f ./k3s/rest-api/secrets.yml
kubectl apply -f ./k3s/rest-api/headless-service.yml
kubectl apply -f ./k3s/rest-api/deployment.yml
cat ./k3s/rest-api/ingress.yml | sed "s/localhost/$BASE_DOMAIN_ENV/g" | kubectl apply -f -
# 10. db cleanup deployment
kubectl apply -f ./k3s/db-cleanup/cleanup-secret.yml
kubectl apply -f ./k3s/db-cleanup/job.yml
# 10. worker deployment
# kubectl apply -f ./k3s/worker/namespace.yml
# kubectl config set-context --current --namespace=worker
# kubectl apply -f ./k3s/worker/secrets.yml
# kubectl apply -f ./k3s/worker/deployment.yml
# 10. ldap deployment
kubectl apply -f ./k3s/ldap/namespace.yml
kubectl config set-context --current --namespace=ldap
kubectl apply -f ./k3s/ldap/secrets.yml
kubectl apply -f ./k3s/ldap/headless-service.yml
kubectl apply -f ./k3s/ldap/deployment.yml
while [[ $(kubectl get pods --all-namespaces -l app=samba-dc -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}' | grep "False") ]]; do echo "waiting for pod" && sleep 1; done
# 11. authentication-api deployment
kubectl apply -f ./k3s/authentication-api/namespace.yml
kubectl config set-context --current --namespace=authentication-api
kubectl create secret generic tls-ca --from-file=./k3s/authentication-api/ca.pem
kubectl create secret generic tls-cert --from-file=./k3s/authentication-api/cert.pem --from-file=./k3s/authentication-api/cert-key.pem
kubectl apply -f ./k3s/authentication-api/headless-service.yml
kubectl apply -f ./k3s/authentication-api/configmap.yml
kubectl apply -f ./k3s/authentication-api/deployment.yml
# 12. webui deployment
kubectl apply -f ./k3s/webui/namespace.yml
kubectl config set-context --current --namespace=webui
kubectl apply -f ./k3s/webui/deployment.yml
kubectl apply -f ./k3s/webui/headless-service.yml
cat ./k3s/webui/ingress.yml | sed "s/localhost/$BASE_DOMAIN_ENV/g" | kubectl apply -f -
# output grafana admin password
echo "grafana admin password:"
kubectl get secret --namespace loki loki-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo

echo "The following urls are available: "
cat ~/.kube/config