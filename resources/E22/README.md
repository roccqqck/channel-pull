# E22 - K8OS ENGINEERING

**Released: 2020-01-28**

[This episode](https://youtu.be/bxT-eJCkqP8) is about using [KubeInvaders](https://github.com/oskapt.kubeinvaders) for chaos engineering in your Kubernetes clusters.

When I sat down to make this video, I started out looking at the Kubernetes manifests. The instructions for installing from the manifests seemed more complicated than they needed to be, so I set out to find a better way for you to install it.

Obviously we can install with Helm, but not everyone runs Helm. Even those instructions seemed too complex, and as you'll see in the video, there are post-install configuration changes that we need to make to get even the Helm deployment to run.

In this video we'll first install into K3s using Helm 3, which has been supported in K3s since v1.17.0.

After that, we'll go back and use the Kustomize templates that I've added in this fork of the [main repo](https://github.com/lucky-sideburn/KubeInvaders/) to set some variables and launch the whole thing with `kubectl`.

## Getting Started

The upstream repos are contained as submodules, so pull them in.

```bash
git submodule update
```

If you need an application to destroy, use the `rancher-demo` app in `resources/common/rancher-demo`.  That's a local submodule of [this repository](https://github.com/oskapt/rancher-demo), and the [install instructions](https://github.com/oskapt/rancher-demo/README.md) will walk you through setting the variables and installing it with Kustomize.

I don't recommend that you install with Helm, but if you want to, you'll find a Helm chart in `kubeinvaders/helm-charts/kubeinvaders` and a README that will talk you through it. K3s supports Helm 3 by default, so that's your best bet for getting an environment up and running.

The Kustomize install method is my preferred method.

Head into `kubeinvaders/kubernetes` and take a look at [the README](kubeinvaders/kubernetes/README.md). That will walk you through setting the variables and installing it with `kubectl apply -k base`.

Enjoy the video! Thank you for your support!
