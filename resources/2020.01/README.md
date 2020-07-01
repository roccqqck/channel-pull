# Episode 21 - Using MetalLB with Rancher

There were two comments on my [earlier episode about MetalLB](https://youtu.be/Ytc24Y0YrXE) that asked about using it with Rancher.

First was this one, on October 25, 2019:

> Thank you for these videos.  How do I change Service type to LoadBalancer in the default nginx-ingress/rancher? I prefer not to use traefik Thanks in advance!
>
> - Paul Rabinowitz

And this one, on December 17, 2019:

> 		Hi Adrian, I'm trying for days now to setup this "client --> metallb --> ingress-controller --> target service" flow, but with Nginx. Can't get it to work. Also had a couple of Slack convos already. Do I need Traefik? Do I need to edit the Rancher default Nginx controller and/or backend? Any pointers are greatly appreciated.
>
> 	- iohenkies

Using it with Rancher and the Nginx Ingress Controller isn't hard, but it requires a few extra steps. 

1. Deploy the cluster _without_ the ingress controller
2. Deploy MetalLB
3. Deploy the ingress controller
4. Deploy a workload

This video shows you how it's done.

Thanks for watching! If you liked the video, please give it a thumbs up and subscribe to the channel. 

Have a great 2020!


# ChangeLog

## 2020-03-04

### Changed

- Replicated [https://github.com/kubernetes/ingress-nginx/tree/nginx-0.29.0/deploy/cloud-generic](cloud-generic) configuration in response to [this issue](https://gitlab.com/monachus/channel/issues/1). 

## 2020-07-01

### Changed

- Added `namespace.yaml` in response to [this issue][https://gitlab.com/monachus/channel/-/issues/2]
- Modified `kustomization.yaml` for metallb, updated version to 0.9.3
- Added secret generator for metallb to work with new Memberlist algorithm

