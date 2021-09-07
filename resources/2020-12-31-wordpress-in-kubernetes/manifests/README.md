# Manifests for 2020.06

## Kustomize templates

I updated these after recording the video so that variables are changed between the normal and polyscripted deployments. The ConfigMap and Secret are now generated by kustomize, but due to [inconsistencies between `kustomize` and `kubectl apply -k`](https://github.com/kubernetes-sigs/kustomize/issues/2205), please use `kustomize build . | kubectl apply -f -` to deploy and update the content.

## VirtualService path redirect

Something I didn't point out in the video is that all Wordpress URLs for the backend (everything except your actual site URL) change to `/wordpress` - so instead of `/wp-admin` you'll go to `/wordpress/wp-admin`. This is reflected in the VirtualService with a `pathRewrite` statement. If you use an Ingress, you'll have to make this adjustment as well. If you don't, then you'll end up in a redirect loop when logging in, where you'll appear to always end up back on the login page. If that happens, simply add `/wordpress` before `/wp-admin` and the login redirect will work.
