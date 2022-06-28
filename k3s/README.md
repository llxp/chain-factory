# Chain-Factory Kubernetes Cluster Resources

## This is a collection of resources that are used to create chain-factory on Kubernetes.

## Steps to do

1. setup vagrant development box
   ```Dockerfile
   vagrant up
   ```
2. upload code for the worker
3. create Dockerfile:
   ```shell
   FROM python:3.10-alpine

   RUN apk add --update --no-cache --virtual .tmp-build-deps libffi-dev gcc libc-dev linux-headers git

   RUN mkdir -p /app

   WORKDIR /app

   COPY ./requirements.txt /app/
   RUN pip install --no-cache-dir -r /app/requirements.txt

   COPY ./framework/ /app/framework
   COPY ./api /app/api
   COPY ./main_worker.py /app/
   COPY ./worker /app/worker

   CMD [ "python", "./main_worker.py" ]
   ```
4. build worker container image
   ```shell
   docker build -t chain-factory-worker .
   ```
5. create a namespace using the script: `./scripts/create-namespace.sh`
6. create directory for the worker yaml files: k3s/worker
7. reference the image in the kubernetes yaml file: k3s/worker/deployment.yml
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
   name: dws-worker-deployment
   namespace: worker
   labels:
      app: dws-worker
   spec:
   replicas: 1
   selector:
      matchLabels:
         app: dws-worker
   template:
      metadata:
         labels:
         app: dws-worker
      spec:
         containers:
         - name: dws-worker
         image: chain-factory-worker:latest
         env:
         - name: IDP_USERNAME
            valueFrom:
               secretKeyRef:
               name: dws-worker-secret
               key: idp-username
               optional: false
         - name: IDP_PASSWORD
            valueFrom:
               secretKeyRef:
               name: dws-worker-secret
               key: idp-password
               optional: false
         - name: VAULT_URL
            valueFrom:
               secretKeyRef:
               name: dws-worker-secret
               key: vault-url
               optional: false
         - name: VAULT_TOKEN
            valueFrom:
               secretKeyRef:
               name: dws-worker-secret
               key: vault-token
               optional: false
         - name: VAULT_ROLE
            valueFrom:
               secretKeyRef:
               name: dws-worker-secret
               key: vault-role
               optional: false
         - name: VAULT_USER
            valueFrom:
               secretKeyRef:
               name: dws-worker-secret
               key: vault-user
               optional: false
         - name: VAULT_PASS
            valueFrom:
               secretKeyRef:
               name: dws-worker-secret
               key: vault-pass
               optional: false
         - name: API_ENDPOINT
            valueFrom:
               secretKeyRef:
               name: dws-worker-secret
               key: api-endpoint
               optional: false
         - name: NAMESPACE
            valueFrom:
               secretKeyRef:
               name: dws-worker-secret
               key: namespace
               optional: false
         - name: NAMESPACE_KEY
            valueFrom:
               secretKeyRef:
               name: dws-worker-secret
               key: namespace-key
               optional: false
         - name: NODE_NAME
            value: "dws-worker"
         - name: WORKER_COUNT
            value: "10"
         - name: LOG_LEVEL
            value: "INFO"
         resources:
            requests:
               cpu: 100m
               memory: 100Mi
            limits:
               cpu: 100m
               memory: 100Mi
   ```
8. create the secrets file
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
   name: dws-worker-secret
   namespace: worker
   stringData:
   # chain-factory credentials
   idp-username: "llxp@jumpcloud.com"
   idp-password: "WmNNJPf7wTurU9t"
   api-endpoint: "http://rest-api-headless.rest-api.svc.cluster.local:8000"
   namespace: "test01"
   # has to be changed after the namespace secret has been created using the rest-api
   # needs to be recreated after every desaster or after the namespace has been changed
   namespace-key: "YnONnFq1bCd7h-O9DrOqM13cIykCUTNyL1o-EY1NrCY="
   type: Generic
   ```