#! /bin/sh

trap "exit" INT TERM ERR
trap "kill 0" EXIT

kubectl port-forward svc/rest-api-headless 8080:8000 --namespace=rest-api &

sleep 1
token=$(curl -X POST http://localhost:8080/auth/login \
   -H 'Content-Type: application/json' \
   -d '{"username":"llxp@jumpcloud.com","password":"WmNNJPf7wTurU9t","scopes":["auth","node_admin","user"]}' | jq -r .access_token.token)

curl -X POST http://localhost:8080/api/v1/namespaces?namespace=test01 \
    -H "Authorization: Bearer $token"

password=$(curl -X POST http://localhost:8080/api/v1/credentials?namespace=test01 \
    -H "Authorization: Bearer $token" | jq -r .)
echo "password: $password"