# HA Kubernetes with RKE2, kube-vip, and Rancher

- [Video](https://youtu.be/QqSgiezqMAA)

## RKE2 Installation (Part One)

```text
➤ cat config.a.yaml
tls-san:
- demo-a
- demo-a.home.monach.us
- demo-cluster.home.monach.us
- 10.68.0.81
disable: rke2-ingress-nginx
cni:
- cilium

$ scp config.a.yaml demo-a:.

$ ssh demo-a

sudo -s

# Set up environment
export VIP=10.68.0.81
export TAG=v0.3.8
export INTERFACE=ens18
export CONTAINER_RUNTIME_ENDPOINT=unix:///run/k3s/containerd/containerd.sock
export CONTAINERD_ADDRESS=/run/k3s/containerd/containerd.sock
export PATH=/var/lib/rancher/rke2/bin:$PATH
export KUBECONFIG=/etc/rancher/rke2/rke2.yaml
alias k=kubectl

# Install RKE2
mkdir -p /etc/rancher/rke2
cp config.a.yaml /etc/rancher/rke2/config.yaml
curl -sfL https://get.rke2.io | sh -
systemctl enable rke2-server
systemctl start rke2-server
# wait for rke2 to be ready
kubectl get nodes

```

## Kube-VIP Installation

```bash

# Pull kube-vip RBAC manifest
curl -s https://kube-vip.io/manifests/rbac.yaml > /var/lib/rancher/rke2/server/manifests/kube-vip-rbac.yaml

# pull image
crictl pull docker.io/plndr/kube-vip:$TAG

# create alias
# on k3s `ctr` is a link to `k3s` which has the namespace set by default but on rke2 we
# have to specify the namespace

alias kube-vip="ctr --namespace k8s.io run --rm --net-host docker.io/plndr/kube-vip:$TAG vip /kube-vip"

# generate manifest
kube-vip manifest daemonset \
    --arp \
    --interface $INTERFACE \
    --address $VIP \
    --controlplane \
    --leaderElection \
    --taint \
    --services \
    --inCluster | tee /var/lib/rancher/rke2/server/manifests/kube-vip.yaml

# check logs
root@demo-a:~# k get po -n kube-system | grep kube-vip
kube-vip-ds-8595m                           1/1     Running     0          48s

root@demo-a:~# k logs kube-vip-ds-8595m -n kube-system --tail 1
time="2021-03-12T12:29:38Z" level=info msg="Broadcasting ARP update for 10.68.0.80 (02:84:08:4a:dd:1c) via ens18"

# ping VIP
root@demo-a:~# ping $VIP
PING 10.68.0.81 (10.68.0.81) 56(84) bytes of data.
64 bytes from 10.68.0.81: icmp_seq=1 ttl=64 time=0.051 ms
64 bytes from 10.68.0.81: icmp_seq=2 ttl=64 time=0.043 ms

# get the token from demo-a
root@demo-a:~# cat /var/lib/rancher/rke2/server/token

# add it to config.b and config.c

➤ cat config.b.yaml
token: K10400a2a885bd2afd9bbf90b3b7e3117f7b9b78393d240bc509699c04e111949d2::server:9b27c71333958cefa9c31ca3c4c3a674
server: https://demo-cluster.home.monach.us:9345
tls-san:
- demo-b
- demo-b.home.monach.us
- demo-cluster.home.monach.us
- 10.68.0.81
disable:
- rke2-ingress-nginx
cni:
- cilium

➤ cat config.c.yaml
token: K10400a2a885bd2afd9bbf90b3b7e3117f7b9b78393d240bc509699c04e111949d2::server:9b27c71333958cefa9c31ca3c4c3a674
server: https://demo-cluster.home.monach.us:9345
tls-san:
- demo-c
- demo-c.home.monach.us
- demo-cluster.home.monach.us
- 10.68.0.81
disable:
- rke2-ingress-nginx
cni:
- cilium

# copy other configs over
➤ for x in b c; scp config.$x.yaml demo-$x:config.yaml; end
config.b.yaml                                                               100%  230   385.3KB/s   00:00
config.c.yaml                                                               100%  230   263.6KB/s   00:00

# bring up other two master nodes

# demo-b
sudo -s
mkdir -p /etc/rancher/rke2
cp config.b.yaml /etc/rancher/rke2/config.yaml
curl -sfL https://get.rke2.io | sh -
systemctl enable rke2-server
systemctl start rke2-server

# demo-c
sudo -s
mkdir -p /etc/rancher/rke2
cp config.c.yaml /etc/rancher/rke2/config.yaml
curl -sfL https://get.rke2.io | sh -
systemctl enable rke2-server
systemctl start rke2-server

# demo-a
kubectl get nodes -w

# if it doesn't come up and if `crictl ps -a` shows an Exited etcd container, restart the service



```

## Kube-VIP Cloud Provider Install

```bash
# demo-a
curl -sfL https://raw.githubusercontent.com/kube-vip/kube-vip-cloud-provider/main/manifest/kube-vip-cloud-controller.yaml > /var/lib/rancher/rke2/server/manifests/kube-vip-cloud-controller.yaml

# copy configmap into place
cat > kube-vip-config.yaml
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: kubevip
  namespace: kube-system
data:
  range-global: 10.68.1.120-10.68.1.130

cp kube-vip-config.yaml /var/lib/rancher/rke2/server/manifests

# test
kubectl create deploy nginx --image=nginx:stable-alpine
kubectl expose deploy nginx --port=80 --type=LoadBalancer

kubectl get services
```
