# CNCN/Trilio Resources

This document captures the commands and links for the video at <https://youtu.be/79IXKH_NPys>.

## Resources

- [Trilio Documentation](https://llb.io/2t2vm)
- [Trilio Examples](https://llb.io/zcro5)
- [Trilio Community](https://llb.io/60amq)

## Walkthrough

### Install the Hostpath CSI Driver (optional)

This will not be needed for most installations. As long as your cluster has a CSI driver that supports [VolumeSnapshots](https://kubernetes.io/docs/concepts/storage/volume-snapshots/), your cluster meets the requirements. We used the Hostpath driver for demonstration only.

#### Procedure

1. Follow [the instructions](https://docs.trilio.io/kubernetes/appendix/csi-drivers/hostpath-for-tvk).

### Install the One-Click Plugin

This plugin enables the installation and configuration of Trilio with a Kubernetes cluster by following a series of executions with different flags.

#### Procedure

1. Install [all prerequisite software](https://docs.trilio.io/kubernetes/tvk-one-click-deploy-and-configure#pre-requisites).

2. Clone the repository

   ```
   git clone https://github.com/trilio-nikita/one-click-TVK-installation/
   ```

3. Install the plugin

   ```
   kubectl krew install --manifest=manifest.yaml --archive=tvk-oneclick.tar.gz
   ```

3. Follow [the instructions](https://docs.trilio.io/kubernetes/tvk-one-click-deploy-and-configure).

The instructions give an overview of how the plugin works, but to summarize, there are four options you can provide to configure TVK in your cluster, and one of them is optional:

- `tvk_oneclick -i` - installs TVK into your cluster
- `tvk_oneclick -c` - creates the management console
- `tvk_oneclick -t` - creates the target to which backups are saved
- `tvk_onclick -s` - deploys a sample application for testing

We chose to use the first two and to deploy the target from within the management console. 

We also chose to manually install an example application by following [the instructions](https://docs.trilio.io/kubernetes/overview/getting-started#create-a-sample-application) in the documentation.

Everything in the video from this point forward uses the TVK UI.

