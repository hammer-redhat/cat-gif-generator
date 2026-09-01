# OpenShift Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three OpenShift manifests (Deployment, Service, Route) to `deploy/` so the cat-gif-generator app can be applied to an OpenShift cluster with `oc apply -f deploy/`.

**Architecture:** ClusterIP Service on port 80 fronting the Flask container on port 5001; edge-TLS Route terminating HTTPS at the OpenShift router; private ghcr.io image pulled via a `ghcr-pull-secret` image pull secret (created out-of-band, never committed).

**Tech Stack:** OpenShift (Route, Deployment, Service), ghcr.io private registry

**Spec:** `docs/superpowers/specs/2026-09-01-openshift-deploy-design.md`

## Global Constraints

- Namespace: `cat-gif-generator`
- Image: `ghcr.io/hammer-redhat/cat-gif-generator:latest`
- Container port: `5001`
- Service port: `80` → targetPort `5001`
- Pull secret name: `ghcr-pull-secret`
- TLS termination: `edge`
- insecureEdgeTerminationPolicy: `Redirect`
- Resource requests: `128Mi` memory, `100m` CPU
- Resource limits: `256Mi` memory, `250m` CPU

---

### Task 1: Create `deploy/deployment.yaml`

**Files:**
- Create: `deploy/deployment.yaml`

**Interfaces:**
- Produces: a Deployment named `cat-gif-generator` with label `app: cat-gif-generator` consumed by the Service selector in Task 2

- [ ] **Step 1: Create the deploy directory and write the manifest**

```bash
mkdir -p deploy
```

```yaml
# deploy/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cat-gif-generator
  namespace: cat-gif-generator
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cat-gif-generator
  template:
    metadata:
      labels:
        app: cat-gif-generator
    spec:
      imagePullSecrets:
        - name: ghcr-pull-secret
      containers:
        - name: cat-gif-generator
          image: ghcr.io/hammer-redhat/cat-gif-generator:latest
          ports:
            - containerPort: 5001
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "250m"
```

- [ ] **Step 2: Validate the YAML is parseable**

```bash
python3 -c "import yaml; yaml.safe_load(open('deploy/deployment.yaml'))" && echo "YAML valid"
```
Expected: `YAML valid`

- [ ] **Step 3: Commit**

```bash
git add deploy/deployment.yaml
git commit -m "feat: add OpenShift Deployment manifest"
```

---

### Task 2: Create `deploy/service.yaml`

**Files:**
- Create: `deploy/service.yaml`

**Interfaces:**
- Consumes: label `app: cat-gif-generator` from Task 1's Deployment pod template
- Produces: Service named `cat-gif-generator` on port `80`, consumed by the Route in Task 3

- [ ] **Step 1: Write the manifest**

```yaml
# deploy/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: cat-gif-generator
  namespace: cat-gif-generator
spec:
  selector:
    app: cat-gif-generator
  ports:
    - port: 80
      targetPort: 5001
```

- [ ] **Step 2: Validate the YAML**

```bash
python3 -c "import yaml; yaml.safe_load(open('deploy/service.yaml'))" && echo "YAML valid"
```
Expected: `YAML valid`

- [ ] **Step 3: Commit**

```bash
git add deploy/service.yaml
git commit -m "feat: add OpenShift Service manifest"
```

---

### Task 3: Create `deploy/route.yaml`

**Files:**
- Create: `deploy/route.yaml`

**Interfaces:**
- Consumes: Service named `cat-gif-generator` on port `80` from Task 2
- Produces: externally accessible HTTPS URL assigned by OpenShift

- [ ] **Step 1: Write the manifest**

```yaml
# deploy/route.yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: cat-gif-generator
  namespace: cat-gif-generator
spec:
  to:
    kind: Service
    name: cat-gif-generator
  port:
    targetPort: 80
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
```

- [ ] **Step 2: Validate the YAML**

```bash
python3 -c "import yaml; yaml.safe_load(open('deploy/route.yaml'))" && echo "YAML valid"
```
Expected: `YAML valid`

- [ ] **Step 3: Commit and push**

```bash
git add deploy/route.yaml
git commit -m "feat: add OpenShift Route manifest with edge TLS"
git push origin main
```

---

### Task 4: Apply to cluster and verify

This task is run by the user against their OpenShift cluster. Prerequisites must be completed first.

- [ ] **Step 1: Run one-time prerequisites (if not already done)**

```bash
oc new-project cat-gif-generator

oc create secret docker-registry ghcr-pull-secret \
  --docker-server=ghcr.io \
  --docker-username=<github-username> \
  --docker-password=<github-pat> \
  --namespace=cat-gif-generator

oc secrets link default ghcr-pull-secret --for=pull -n cat-gif-generator
```

- [ ] **Step 2: Dry-run to validate manifests against the cluster API**

```bash
oc apply --dry-run=client -f deploy/
```
Expected: three lines of `... configured (dry run)` with no errors.

- [ ] **Step 3: Apply manifests**

```bash
oc apply -f deploy/
```
Expected:
```
deployment.apps/cat-gif-generator created
service/cat-gif-generator created
route.route.openshift.io/cat-gif-generator created
```

- [ ] **Step 4: Verify pod is running**

```bash
oc get pods -n cat-gif-generator -w
```
Expected: pod reaches `Running` status (1/1 Ready). If it stays in `ImagePullBackOff`, the pull secret is not linked — re-run Step 1.

- [ ] **Step 5: Get the Route hostname and verify HTTPS**

```bash
oc get route cat-gif-generator -n cat-gif-generator -o jsonpath='{.spec.host}'
```
Then open `https://<hostname>` in a browser.
Expected: Cat GIF Viewer UI loads over HTTPS. HTTP should redirect to HTTPS automatically.
