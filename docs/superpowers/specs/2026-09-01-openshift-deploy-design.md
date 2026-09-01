# OpenShift Deployment Design — cat-gif-generator

**Date:** 2026-09-01  
**Repo:** github.com/hammer-redhat/cat-gif-generator  
**Status:** Approved

## Goal

Deploy the cat-gif-generator Flask app to an OpenShift cluster using a private ghcr.io image, expose it externally via an edge-TLS Route, and store all manifests in the repo under `deploy/`.

## Prerequisites (one-time, out-of-band)

These commands must be run once against the cluster before applying manifests. They are **never committed to git** — the pull secret holds a GitHub PAT.

```bash
# Create the project
oc new-project cat-gif-generator

# Create image pull secret for private ghcr.io package
oc create secret docker-registry ghcr-pull-secret \
  --docker-server=ghcr.io \
  --docker-username=<github-username> \
  --docker-password=<github-pat> \
  --namespace=cat-gif-generator

# Allow the default service account to use the pull secret
oc secrets link default ghcr-pull-secret --for=pull -n cat-gif-generator
```

## Manifests

All manifests live in `deploy/` and are applied with `oc apply -f deploy/`.

### Deployment (`deploy/deployment.yaml`)

- **Namespace:** `cat-gif-generator`
- **Replicas:** 1
- **Image:** `ghcr.io/hammer-redhat/cat-gif-generator:latest`
- **Container port:** 5001
- **imagePullSecrets:** `ghcr-pull-secret`
- **Resources:**
  - requests: 128Mi memory, 100m CPU
  - limits: 256Mi memory, 250m CPU

### Service (`deploy/service.yaml`)

- **Namespace:** `cat-gif-generator`
- **Type:** ClusterIP
- **Port:** 80 → targetPort 5001
- **Selector:** matches the Deployment's pod labels

### Route (`deploy/route.yaml`)

- **Namespace:** `cat-gif-generator`
- **TLS termination:** edge (HTTPS at the router; HTTP inside the cluster)
- **insecureEdgeTerminationPolicy:** Redirect (HTTP → HTTPS)
- **Hostname:** unset — OpenShift assigns `cat-gif-generator-cat-gif-generator.<cluster-domain>` automatically
- **targetPort:** 80 (the Service port)

## Files Created

| File | Action |
|------|--------|
| `deploy/deployment.yaml` | Create |
| `deploy/service.yaml` | Create |
| `deploy/route.yaml` | Create |

## Apply Order

```bash
oc apply -f deploy/
```

OpenShift processes the three manifests in any order; dependencies (Service ← Route) resolve automatically.

## Success Criteria

- `oc get pods -n cat-gif-generator` shows 1 running pod
- `oc get route -n cat-gif-generator` shows an assigned hostname
- Visiting `https://<assigned-hostname>` returns the Cat GIF Viewer UI
- HTTP redirects to HTTPS (insecureEdgeTerminationPolicy: Redirect)
