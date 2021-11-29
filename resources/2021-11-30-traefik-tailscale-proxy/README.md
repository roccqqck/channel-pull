# Traefik Multi-Cluster Proxy

This README is in support of the videos located [here](https://youtu.be/Wh_HpPwSswo) (Part One) and [here](https://youtu.be/OIwxIdyZg7A) (Part Two).

In it I show you how I cut my cloud costs from $300/month to $15/month by moving all of my production Kubernetes workloads in-house and tunneling through a dynamic IP using [Traefik Proxy](https://traefik.io/traefik/) and [Tailscale](https://tailscale.io).

The videos are structured as a rapid tutorial, with all of the commands captured in this README.

## Prerequisites

There are some fundamental things that you'll need to follow along.

- A cloud instance somewhere (the "edge" cluster)
- One or more local nodes somewhere else (the "local" cluster)
- CLI utilities
  - kubectl
  - kubie (optional)
  - k3sup
- A [tailscale](https://tailscale.com) account

Replace all instances of `138.197.212.50` with the external IP of your edge node.

Replace all instances of `10.68.0.70` with the internal host IP of one of the local nodes.

Replace all instances of `10.73.x.x` with the ClusterIP Service address for the corresponding Service in that section of the README.

## Local Cluster

The local cluster consists of [K3s](https://k3s.io), Traefik Proxy, and a Tailscale [subnet router](https://tailscale.com/kb/1019/subnets/).

### Install K3s (Local Cluster)

```bash
k3sup install --host=demo-a --user=root --local-path=local/config.yaml \
  --context=local --k3s-extra-args="--cluster-cidr=10.72.0.0/16 \
  --service-cidr=10.73.0.0/16" --k3s-channel=stable

kubie ctx -f local/config.yaml
```

### Install Tailscale

In the Tailscale admin interface, under Settings/Auth Keys

- create a reusable authentication key

```bash
kubectl create ns tailscale
kubie ns tailscale

cd tailscale

# get authkey from tailscale admin interface
# create secret from authkey
kubectl create secret generic tailscale-auth --from-literal=AUTH_KEY=YOUR-AUTH-KEY-HERE --dry-run=client -o yaml > authkey.yaml

kubectl apply -f authkey.yaml -n tailscale

# rbac
kubectl apply -f local/rbac.yaml -n tailscale

# edit subnet.yaml and add local service and/or pod CIDRs
kubectl apply -f local/subnet.yaml -n tailscale
```

In tailscale admin interface, check that host appears, and then disable key expiration and activate the routes.

The local cluster build is now complete.

## Edge Cluster

The edge cluster consists of K3s, [Kyverno](https://kyverno.io), Traefik Proxy, and a Tailscale sidecar attached to the Traefik Proxy Pod.

### Install K3s (Edge Cluster)

```bash
k3sup install --host=138.197.212.50 --user=root --local-path=edge/config.yaml \
  --context=edge --k3s-extra-args="--cluster-cidr=10.74.0.0/16 \
  --service-cidr=10.75.0.0/16 \
  --disable traefik" --k3s-channel=stable

kubie ctx -f edge/config.yaml
```

### Tailscale

```bash
kubectl create ns traefik-system

cd tailscale

# apply the same authkey as the local cluster
kubectl apply -f authkey.yaml -n traefik-system

# install the modified rbac config that allows the
# traefik serviceaccount to control the tailscale
# secret
kubectl apply -f edge/rbac.yaml -n traefik-system
```

### Install Kyverno

Kyverno is used to mutate the Traefik Deployment manifest and attach our Tailscale sidecar to it.

```bash
cd ..
helm repo add kyverno https://kyverno.github.io/kyverno/
helm repo update
helm install kyverno kyverno/kyverno --namespace kyverno --create-namespace
kubectl apply -f kyverno/policy.yaml -n traefik-system
```

### Install Traefik via Helm

Add some additional flags to the Helm deployment, enabling Traefik to use ExternalName Services for the Ingress and CRD providers.

```bash
helm repo add traefik https://helm.traefik.io/traefik
helm repo update
helm install traefik traefik/traefik -n traefik-system \
  --set providers.kubernetesCRD.allowExternalNameServices=true \
  --set providers.kubernetesIngress.publishedService.enabled=true \
  --set providers.kubernetesIngress.publishedService.pathOverride="traefik-system/traefik" \
  --set "additionalArguments={--providers.kubernetesIngress.allowExternalNameServices=true}" \
  --set ports.websecure.tls.enabled=true
```

In tailscale admin interface, check that the host appears, and then disable key expiration.

The edge cluster build is now complete.

## Testing

### Local Cluster Setup

Install the `monachus/traefik-demo` application into the local cluster. This launches three replicas and demonstrates load balancing across them.

```bash
kubectl create ns traefik-demo
kubectl create deploy traefik-demo --image=monachus/traefik-demo --port=8080 --replicas=3 -n traefik-demo
kubectl expose deploy traefik-demo --port=80 --target-port=8080 -n traefik-demo

# get the IP from the Service
kubectl get service -n traefik-demo

# edit ingressroute.yaml and set the Host values for external and internal
kubectl apply -f local/ingressroute.yaml -n traefik-demo

# look for a 200 response code, or optionally visit
# the URL below in a browser. (change the IP)
curl -I traefik-demo.local.10.68.0.70.sslip.io
```

### Edge Cluster Setup

Create an ExternalName Service and an IngressRoute on the edge cluster. This enables it to communicate with and send traffic to the local cluster.

```bash
# edit ext-service.yaml and set the ClusterIP of the Traefik service
kubectl apply -f edge/ext-service-demo-http.yaml -n traefik-system

# edit ingressroute.yaml and set the Host to the external Host value from Local
# set the service name to local-demo-http
kubectl apply -f edge/ingressroute.yaml -n traefik-system

# look for a 200 response code, or optionally visit
# the URL below in a browser. (change the IP)
curl -I traefik-demo.edge.138.197.212.50.sslip.io
```

## What About TLS?

Because we're using the Tailscale network to communicate between nodes, the traffic that traverses the Internet is already encrypted. We can terminate TLS on either the edge cluster or the local cluster. We'll use [cert-manager](https://cert-manager.io) to generate and manage certificates from Let's Encrypt.

### Edge Cluster Termination

#### Install cert-manager (Edge Cluster)

```bash
kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.6.0/cert-manager.yaml
```

#### Create ClusterIssuer (Edge Cluster)

This ClusterIssuer will handle HTTP-01 challenges. You can use DNS-01 instead if you have a domain configured for it.

```bash
cd letsencrypt
kubectl apply -f clusterissuer.yaml
```

#### Option A

This uses the Ingress resource to have cert-manager create a certificate automatically.

```bash
kubectl delete ingressroute/traefik-demo -n traefik-system
kubectl apply -f 01-edge/ingress.yaml -n traefik-system
```

#### Option B

This has cert-manager create the certificate manually and store it in a Secret. We'll continue to use the IngressRoute and point it to the Secret. Our environment is configured with the Ingress provider, so cert-manager will create Ingress resources to serve the HTTP-01 challenge.

```bash
# clean up previous examples
kubectl delete ingress traefik-demo
kubectl delete secret traefik-demo-edge-crt

# create middleware for redirects
kubectl apply -f middleware-redirect-scheme.yaml -n traefik-system

# create certificate
kubectl apply -f 01-edge/certificate.yaml -n traefik-system

# create ingressroute
kubectl apply -f 01-edge/ingressroute.yaml -n traefik-system

# test redirect (or visit in browser)
curl -IL traefik-demo.edge.138.197.212.50.sslip.io
```

### Local Cluster Termination

If we want to access local services via the same FQDN with TLS on both the edge and local clusters, then certificate generation has to happen on the local cluster.

Terminating TLS on the local cluster requires that we also connect TCP ports from the edge cluster to the local cluster. Doing so means that we can no longer see into the request for non-encrypted communication, so we can't perform Layer 7 routing of the request at the edge. This example assumes that we're sending all traffic from the edge to the local cluster.

#### Edge Cluster Configuration

```bash
## edge cluster
# cleanup
kubectl delete ingressroute traefik-demo-http -n traefik-system
kubectl delete ingressroute traefik-demo-https -n traefik-system
kubectl delete certificate traefik-demo-edge -n traefik-system
kubectl delete secret traefik-demo-edge-crt -n traefik-system
kubectl delete service local-demo-http -n traefik-system

# edit ext-service-traefik.yaml and set the IP
# of the local Traefik service

# install ExternalName Service and IngressRouteTCP
kubectl apply -f 02-local/edge/ext-service-traefik.yaml -n traefik-system
kubectl apply -f 02-local/edge/ingressroute.yaml -n traefik-system
```

#### Local Cluster Configuration

```bash
## local cluster
# cleanup
kubectl delete ingressroute traefik-demo-external-http

# install cert-manager and clusterissuer
cd letsencrypt

kubectl apply -f middleware-redirect-scheme.yaml
kubectl apply -f 02-local/local/certificate.yaml -n traefik-demo
kubectl apply -f 02-local/local/ingressroute.yaml -n traefik-demo

# test redirect (or visit in browser)
curl -IL traefik-demo.edge.138.197.212.50.sslip.io
```

## Conclusion

This is a small-scale demonstration of how to tunnel traffic from a public cloud provider to a private cluster. It can scale to any size and any application, and as cloud providers continue to build walled gardens to keep their customers locked-in and captive, a solution like this just might be the [rock hammer](https://www.youtube.com/watch?v=cZHJuM1tqgo) you need to escape.
