SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo "SCRIPT_DIR: $SCRIPT_DIR"

REMOTE_HOST=$1
USER=$2
SSH_REMOTE="$USER@$REMOTE_HOST"
API_ENDPOINT=$3
PROVISION_MASTER=$4

echo "REMOTE_HOST: $REMOTE_HOST"
echo "USER: $USER"

if [ ! -f "$SCRIPT_DIR/env/k3s_token" ]; then
  mkdir $SCRIPT_DIR/env
  k3s_token=$(openssl rand -hex 16)
  echo $k3s_token > $SCRIPT_DIR/env/k3s_token
  echo $API_ENDPOINT > $SCRIPT_DIR/env/k3s_api_endpoint
fi

echo $PROVISION_MASTER > $SCRIPT_DIR/env/provision_master

ssh $SSH_REMOTE << EOF
touch /tmp/k3s_token
chmod 600 /tmp/k3s_token
mkdir /tmp/chain-factory
chmod 700 /tmp/chain-factory
EOF

cat <<EOF > $SCRIPT_DIR/env/install.sh
export K3S_TOKEN=\$(cat /tmp/k3s_token)
export API_ENDPOINT=\$(cat /tmp/k3s_api_endpoint)
export PROVISION_MASTER=\$(cat /tmp/provision_master)
cat /tmp/k3s_token
echo "k3s_token: \$k3s_token"
cd /tmp/chain-factory
# source /tmp/chain-factory/setup_k3s.sh
source /tmp/chain-factory/install_k8s_resources.sh
EOF

# environment variables
scp $SCRIPT_DIR/env/k3s_token $SSH_REMOTE:/tmp/k3s_token
scp $SCRIPT_DIR/env/k3s_api_endpoint $SSH_REMOTE:/tmp/k3s_api_endpoint
scp $SCRIPT_DIR/env/provision_master $SSH_REMOTE:/tmp/provision_master

# chain-factory k8s resources
scp $SCRIPT_DIR/env/install.sh $SSH_REMOTE:/tmp/install.sh
scp -r $SCRIPT_DIR/k3s/ $SSH_REMOTE:/tmp/chain-factory/k3s
scp $SCRIPT_DIR/setup_k3s.sh $SSH_REMOTE:/tmp/chain-factory/setup_k3s.sh
scp -r $SCRIPT_DIR/scripts $SSH_REMOTE:/tmp/chain-factory/scripts
scp -r $SCRIPT_DIR/mongodb $SSH_REMOTE:/tmp/chain-factory/mongodb
scp $SCRIPT_DIR/install_k8s_resources.sh $SSH_REMOTE:/tmp/chain-factory/install_k8s_resources.sh

ssh $SSH_REMOTE chmod +x /tmp/install.sh
ssh -t $SSH_REMOTE "sudo bash /tmp/install.sh"