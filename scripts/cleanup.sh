#!/bin/sh

login_response = $(curl -s -k -d '{"username":"'$IDP_USERNAME'","password":"'$IDP_PASSWORD'","scopes":["auth","user"]}' -H "Content-Type: application/json" -X POST https://$API_ENDPOINT/auth/login)
access_token = $(echo $login_response | jq -r '.access_token')
echo "Access token: $access_token"