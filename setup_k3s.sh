# k3s_token=$(openssl rand -hex 16)
# echo $k3s_token > ./k3s/k3s_token
# curl -sfL https://get.k3s.io | K3S_TOKEN=$k3s_token sh -s - server --cluster-init
sudo -i -u vagrant curl -sfL https://get.k3s.io | K3S_KUBECONFIG_MODE="644" sh -

apt install -y nfs-kernel-server nfs-common
mkdir -p /exports/k3s
chown nobody:nogroup /exports/k3s
cat << EOF >> /etc/exports
/exports 127.0.0.1/8(rw,sync,no_subtree_check,crossmnt,fsid=0)
/exports/k3s 127.0.0.1/8(rw,sync,no_subtree_check)
EOF

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
