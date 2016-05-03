#!/bin/sh

set -x

# Switch off SE-Linux
setenforce 0

# Get the latest stable version of kubernetes
export K8S_VERSION=$(curl -sS https://storage.googleapis.com/kubernetes-release/release/stable.txt)
echo "K8S_VERSION : ${K8S_VERSION}"

echo "Starting docker service"
sudo systemctl enable docker.service
sudo systemctl start docker.service --ignore-dependencies
echo "Checking docker service"
sudo docker ps

# Run the docker containers for kubernetes
echo "Starting Kubernetes containers"
sudo docker run \
    --volume=/:/rootfs:ro \
    --volume=/sys:/sys:ro \
    --volume=/var/lib/docker/:/var/lib/docker:rw \
    --volume=/var/lib/kubelet/:/var/lib/kubelet:rw \
    --volume=/var/run:/var/run:rw \
    --net=host \
    --pid=host \
    --privileged=true \
    --name=kubelet \
    -d \
    gcr.io/google_containers/hyperkube-amd64:${K8S_VERSION} \
    /hyperkube kubelet \
        --containerized \
        --hostname-override="127.0.0.1" \
        --address="0.0.0.0" \
        --api-servers=http://localhost:8080 \
        --config=/etc/kubernetes/manifests \
        --allow-privileged=true --v=2


echo "Download Kubernetes CLI"
wget -O kubectl "http://storage.googleapis.com/kubernetes-release/release/${K8S_VERSION}/bin/linux/amd64/kubectl"
chmod 755 kubectl
./kubectl get nodes

echo "Waiting for master components to start..."
while true; do
    running_count=$(./kubectl -s=http://127.0.0.1:8080 get pods --no-headers 2>/dev/null | grep "Running" | wc -l)
    # We expect to have 3 running pods - etcd, master and kube-proxy.
    if [ "$running_count" -ge 3 ]; then
      break
    fi
    echo -n "."
    sleep 1
done
echo "SUCCESS"
echo "Cluster created!"
echo ""
