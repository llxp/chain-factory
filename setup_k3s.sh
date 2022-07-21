#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo "SCRIPT_DIR: $SCRIPT_DIR"
BASE_DOMAIN_ENV=${BASE_DOMAIN:-localhost}
METALLB_IP_RANGE=${IP_RANGE:-10.0.2.15-10.0.2.20}
PROVISION_MASTER=${PROVISION_MASTER:-true}
API_ENDPOINT=${API_ENDPOINT:-https://localhost:6443}

pregenerated_k3s_token=$(openssl rand -hex 16)
k3s_token_env=${K3S_TOKEN:-$(cat /tmp/k3s_token)}
k3s_token=${k3s_token_env:-$pregenerated_k3s_token}
# k3s_token=$(openssl rand -hex 16)
# echo $k3s_token > ./k3s/k3s_token
echo $k3s_token
# curl -sfL https://get.k3s.io | K3S_TOKEN=$k3s_token sh -s - server --cluster-init

cat <<EOF > /etc/sysctl.d/90-kubelet.conf
vm.panic_on_oom=0
vm.overcommit_memory=1
kernel.panic=10
kernel.panic_on_oops=1
kernel.keys.root_maxbytes=25000000
EOF
sysctl --system

if [ $PROVISION_MASTER == "true" ]; then
  K3S_EXEC="--cluster-init"
else
  K3S_EXEC="--server https://$API_ENDPOINT:8443"
fi

export INSTALL_K3S_EXEC="server ${K3S_EXEC}\
  --protect-kernel-defaults=true \
	--kube-apiserver-arg=audit-log-path=/var/lib/rancher/k3s/server/logs/audit.log \
	--kube-apiserver-arg=audit-policy-file=/var/lib/rancher/k3s/server/audit.yaml \
  --kube-apiserver-arg=audit-log-maxage=30 \
  --kube-apiserver-arg=audit-log-maxbackup=10 \
  --kube-apiserver-arg=audit-log-maxsize=100 \
  --kube-apiserver-arg=request-timeout=300s \
  --kube-apiserver-arg=service-account-lookup=true \
  --kube-apiserver-arg=enable-admission-plugins=NodeRestriction,PodSecurityPolicy,NamespaceLifecycle,ServiceAccount \
  --kube-controller-manager-arg=terminated-pod-gc-threshold=10 \
  --kube-controller-manager-arg=use-service-account-credentials=true \
  --kubelet-arg=streaming-connection-idle-timeout=5m \
  --kubelet-arg=make-iptables-util-chains=true \
  --disable traefik \
  --disable servicelb"
export K3S_KUBECONFIG_MODE="600"
export INSTALL_K3S_SKIP_START="true"
export K3S_TOKEN=$k3s_token
curl -sfL https://get.k3s.io | sh -s - server --cluster-init
mkdir -p -m 700 /var/lib/rancher/k3s/server/logs
cat <<EOF > /var/lib/rancher/k3s/server/audit.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
EOF
systemctl enable k3s.service
systemctl start k3s.service
while [ ! -d /var/lib/rancher/k3s/server/manifests/ ]; do sleep 1; done
cp $SCRIPT_DIR/scripts/hardening/pod-security-policies.yml /var/lib/rancher/k3s/server/manifests/policy.yaml
mkdir -p ~/.kube
chmod 710 ~/.kube
ln -s /etc/rancher/k3s/k3s.yaml ~/.kube/config
# kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.12.1/manifests/namespace.yaml
# kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.12.1/manifests/metallb.yaml
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.3/config/manifests/metallb-native.yaml
cat <<EOF > /tmp/metallb-configmap.yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  namespace: metallb-system
  name: first-pool
spec:
  addresses:
    - $METALLB_IP_RANGE
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: example
  namespace: metallb-system
spec:
  ipAddressPools:
  - first-pool
  nodeSelectors:
  - matchLabels:
      kubernetes.io/hostname: ubuntu-jammy
EOF
sleep 30
kubectl apply -f /tmp/metallb-configmap.yaml
# kubectl apply -f $SCRIPT_DIR/scripts/traefik-deployment.yaml
# sleep 10
# kubectl apply -f $SCRIPT_DIR/scripts/traefik-crd.yaml

apt install -y nfs-kernel-server nfs-common
mkdir -p /storage_mount/k3s
chown nobody:nogroup /storage_mount/k3s
cat << EOF >> /etc/exports
/storage_mount 127.0.0.1/8(rw,sync,no_subtree_check,crossmnt,fsid=0)
/storage_mount/k3s 127.0.0.1/8(rw,sync,no_subtree_check)
EOF
exportfs -ar

# cat <<EOF > /var/lib/rancher/k3s/server/manifests/nfs.yaml
# apiVersion: helm.cattle.io/v1
# kind: HelmChart
# metadata:
#   name: nfs
#   namespace: default
# spec:
#   chart: nfs-subdir-external-provisioner
#   repo: https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner
#   targetNamespace: default
#   set:
#     nfs.server: 127.0.0.1
#     nfs.path: /k3s
#     storageClass.name: standard
#     storageClass.onDelete: retain
#     storageClass.reclaimPolicy: Retain
# EOF

cat <<EOF > /tmp/nfs.yaml
nfs:
  server: 127.0.0.1
  path: /k3s
storageClass:
  name: standard
  onDelete: retain
  reclaimPolicy: Retain
podSecurityPolicy:
  enabled: true
EOF

curl -fsSL -o /tmp/get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 /tmp/get_helm.sh
/tmp/get_helm.sh
helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/
helm repo update
helm install nfs-subdir-external-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner --namespace default -f /tmp/nfs.yaml
kubectl patch storageclass local-path -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'
kubectl patch storageclass standard -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
helm repo add traefik https://helm.traefik.io/traefik
helm repo update
kubectl create namespace traefik-v2
helm install traefik traefik/traefik --namespace traefik-v2
cat $SCRIPT_DIR/scripts/traefik-dashboard.yaml | sed "s/localhost/$BASE_DOMAIN_ENV/g" | kubectl apply -f -