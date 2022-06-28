# Authentication-API

## Steps to do

1. clone repository https://github.com/llxp/authentication-api-go.git
2. build project using go build
3. run binary to generate server secret in config file
4. copy server secret from config file to configmap
5. generate certificates using internal pki and place in this directory and name them cert.pem and cert-key.pem and ca.pem
6. adjust ldap config/ad config for target active directory/ldap server in configmap
7. generate a new server secret using openssl rand -hex 16
8. kubectl apply -f namespace.yml
9. kubectl apply -f configmap.yml
10. kubectl apply -f deployment.yml