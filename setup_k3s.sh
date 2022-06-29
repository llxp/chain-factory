# k3s_token=$(openssl rand -hex 16)
# echo $k3s_token > ./k3s/k3s_token
# curl -sfL https://get.k3s.io | K3S_TOKEN=$k3s_token sh -s - server --cluster-init

cat <<EOF > /etc/sysctl.d/90-kubelet.conf
vm.panic_on_oom=0
vm.overcommit_memory=1
kernel.panic=10
kernel.panic_on_oops=1
kernel.keys.root_maxbytes=25000000
EOF
sysctl --system

export INSTALL_K3S_EXEC="server \
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
  --kubelet-arg=make-iptables-util-chains=true"
export K3S_KUBECONFIG_MODE="600"
export INSTALL_K3S_SKIP_START="true"
curl -sfL https://get.k3s.io | sh -
mkdir -p -m 700 /var/lib/rancher/k3s/server/logs
cat <<EOF > /var/lib/rancher/k3s/server/audit.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
EOF
systemctl enable k3s.service
systemctl start k3s.service
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo "SCRIPT_DIR: $SCRIPT_DIR"
cp $SCRIPT_DIR/scripts/hardening/pod-security-policies.yml /var/lib/rancher/k3s/server/manifests/policy.yaml
mkdir -p ~/.kube
chmod 710 ~/.kube
ln -s /etc/rancher/k3s/k3s.yaml ~/.kube/config

apt install -y nfs-kernel-server nfs-common
mkdir -p /exports/k3s
chown nobody:nogroup /exports/k3s
cat << EOF >> /etc/exports
/exports 127.0.0.1/8(rw,sync,no_subtree_check,crossmnt,fsid=0)
/exports/k3s 127.0.0.1/8(rw,sync,no_subtree_check)
EOF
exportfs -ar

cat <<EOF > /var/lib/rancher/k3s/server/manifests/nfs.yaml
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: nfs
  namespace: default
spec:
  chart: nfs-subdir-external-provisioner
  repo: https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner
  targetNamespace: default
  set:
    nfs.server: 127.0.0.1
    nfs.path: /k3s
    storageClass.name: standard
    storageClass.onDelete: retain
    storageClass.reclaimPolicy: Retain
EOF

curl -fsSL -o /tmp/get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 /tmp/get_helm.sh
/tmp/get_helm.sh