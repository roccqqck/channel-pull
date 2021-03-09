# 2021.02

## K3s VIP installation

```
k3sup install \
	--host=demo-a \
	--user=root \
	--k3s-version=v1.19.4+k3s1 \
	--local-path=config.demo.yaml \
	--context demo \
	--cluster \
	--tls-san 10.68.0.240 \
	--k3s-extra-args="--disable servicelb --node-taint node-role.kubernetes.io/master=true:NoSchedule"

kcc -f config.demo.yaml

ssh root@demo-a

curl -s https://kube-vip.io/manifests/rbac.yaml > /var/lib/rancher/k3s/server/manifests/kube-vip-rbac.yaml

# edit kube-vip-rbac.yaml
  - apiGroups: ["coordination.k8s.io"]
    resources: ["leases"]
    verbs: ["list", "get", "watch", "update", "create"]

ifconfig ens18
export VIP=10.68.0.240
export INTERFACE=ens18

# fetch container 
crictl pull docker.io/plndr/kube-vip:0.3.2

# create alias
alias kube-vip="ctr run --rm --net-host docker.io/plndr/kube-vip:0.3.2 vip /kube-vip"

# generate manifest
kube-vip manifest daemonset \
    --arp \
    --interface $INTERFACE \
    --address $VIP \
    --controlplane \
    --leaderElection \
    --taint \
    --inCluster | tee /var/lib/rancher/k3s/server/manifests/kube-vip.yaml
    
# edit kube-vip.yaml
      tolerations:
      - effect: NoSchedule
        key: node-role.kubernetes.io/master
        operator: Exists
        
ping 10.68.0.240

# edit config.demo.yaml and replace server with 10.68.0.240

# add remaining server nodes

k3sup join --host=demo-b --server-user=root --server-host=10.68.0.240 --user=root --k3s-version=v1.19.4+k3s1 --server --k3s-extra-args="--disable servicelb --node-taint node-role.kubernetes.io/master=true:NoSchedule"

k3sup join --host=demo-c --server-user=root --server-host=10.68.0.240 --user=root --k3s-version=v1.19.4+k3s1 --server --k3s-extra-args="--disable servicelb --node-taint node-role.kubernetes.io/master=true:NoSchedule"

k get po -n kube-system

# add worker node
k3sup join --host=demo-d --server-user=root --server-host=10.68.0.240 --user=root --k3s-version=v1.19.4+k3s1

k get po -n kube-system
k get service -n kube-system
```

## K3s Service LoadBalancer Installation

```
# install metallb
curl -s https://raw.githubusercontent.com/metallb/metallb/v0.9.5/manifests/namespace.yaml > /var/tmp/metallb.yaml; \
echo '---' >> /var/tmp/metallb.yaml; \
curl -s https://raw.githubusercontent.com/metallb/metallb/v0.9.5/manifests/metallb.yaml >> /var/tmp/metallb.yaml; \
mv /var/tmp/metallb.yaml /var/lib/rancher/k3s/server/manifests

# create secret
kubectl create secret generic -n metallb-system memberlist --from-literal=secretkey="$(openssl rand -base64 128)"

# create configmap
apiVersion: v1
kind: ConfigMap
metadata:
  namespace: metallb-system
  name: config
data:
  config: |
    address-pools:
    - name: default
      protocol: layer2
      addresses:
      - 10.68.0.230-10.68.0.239
```

## Demonstration

```
ns default
k create deploy demo --image monachus/rancher-demo --port 8080 --replicas=3
k expose deploy demo --type=LoadBalancer --port=80 --target-port=8080

```

