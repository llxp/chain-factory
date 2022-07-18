SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo "SCRIPT_DIR: $SCRIPT_DIR"

REMOTE_HOST=$1
USER=$2

if [ ! -f "$SCRIPT_DIR/k3s_token" ]; then
  k3s_token=$(openssl rand -hex 16)
  echo $k3s_token > $SCRIPT_DIR/k3s_token
fi

ssh $USER@REMOTE_HOST << EOF
touch /tmp/k3s_token
chmod 600 /tmp/k3s_token
EOF

cat <<EOF > $SCRIPT_DIR/echo.sh
#!/bin/sh
echo "k3s_token: $k3s_token"
cd /tmp/chain-factory
/tmp/chain-factory/setup_k3s.sh
EOF

scp $SCRIPT_DIR/k3s_token $USER@REMOTE_HOST:/tmp/k3s_token
scp $SCRIPT_DIR/echo.sh $USER@REMOTE_HOST:/tmp/echo.sh
scp ./ $USER@REMOTE_HOST:/tmp/chain-factory

ssh -t $USER@REMOTE_HOST chmod +x /tmp/echo.sh
ssh -t $USER@REMOTE_HOST "sudo /tmp/echo.sh"