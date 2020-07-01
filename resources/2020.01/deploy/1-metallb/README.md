Update: 2020-07-01

MetalLB now uses Memberlist from Hashicorp for fast detection of failed nodes. 
This requires a secret to be installed in the cluster.

Run `generate-secret.sh` to create that secret, prior to installing MetalLB 
with Kustomize.

If you get errors about `--dry-run=client`, make sure you're running a version
of `kubectl` >=1.18.4.

