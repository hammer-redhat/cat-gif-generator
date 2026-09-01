# CI/CD Container Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Dockerfile and GitHub Actions workflow so the cat-gif-generator app is built as a Red Hat UBI9 container image and published to ghcr.io on every push to `main`.

**Architecture:** Single-stage Dockerfile using `ubi9/python-313` as the base; packages installed from the Red Hat Lightwell index (with PyPI as fallback for transitive deps). GitHub Actions runs on both PRs (build-only) and pushes to `main` (build + push), using the built-in `GITHUB_TOKEN` for ghcr.io authentication.

**Tech Stack:** Docker, GitHub Actions, Red Hat UBI9, ghcr.io

**Spec:** `docs/superpowers/specs/2026-09-01-cicd-design.md`

## Global Constraints

- Base image: `registry.access.redhat.com/ubi9/python-313`
- Package index: `--extra-index-url https://packages.redhat.com/lightwell/public-lightwell-demo/python/validated/`
- Registry: `ghcr.io/hammer-redhat/cat-gif-generator`
- App port: `5001`
- Python binary inside UBI9 image: `python3`
- `.secret.key` and `.session.token` must never appear in the built image

---

### Task 1: Add `.gitignore`

**Files:**
- Create: `.gitignore`

**Interfaces:**
- Produces: nothing consumed by other tasks — standalone hygiene step

- [ ] **Step 1: Create `.gitignore`**

```
.secret.key
.session.token
__pycache__/
*.pyc
*.pyo
.DS_Store
```

- [ ] **Step 2: Verify the secrets are now ignored**

Run:
```bash
git status
```
Expected: `.secret.key` and `.session.token` no longer listed as untracked files.

- [ ] **Step 3: Commit**

```bash
git add .gitignore
git commit -m "chore: add .gitignore to exclude secrets and cache"
```

---

### Task 2: Create `.dockerignore`

**Files:**
- Create: `.dockerignore`

**Interfaces:**
- Produces: build context exclusion rules consumed implicitly by `docker build` in Task 3

- [ ] **Step 1: Create `.dockerignore`**

```
.secret.key
.session.token
__pycache__/
*.pyc
*.pyo
.git/
.remember/
docs/
.DS_Store
```

- [ ] **Step 2: Verify the file exists**

Run:
```bash
cat .dockerignore
```
Expected: file prints the exclusion list above.

- [ ] **Step 3: Commit**

```bash
git add .dockerignore
git commit -m "chore: add .dockerignore to exclude secrets and dev artifacts"
```

---

### Task 3: Create `Dockerfile`

**Files:**
- Create: `Dockerfile`

**Interfaces:**
- Consumes: `.dockerignore` (Task 2) — keeps build context clean
- Consumes: `requirements.txt` — package list
- Produces: buildable image tagged locally as `cat-gif-generator:local` for smoke test

- [ ] **Step 1: Create `Dockerfile`**

```dockerfile
FROM registry.access.redhat.com/ubi9/python-313

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir \
    --extra-index-url https://packages.redhat.com/lightwell/public-lightwell-demo/python/validated/ \
    -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python3", "app.py"]
```

- [ ] **Step 2: Build the image locally**

Run:
```bash
docker build -t cat-gif-generator:local .
```
Expected: build completes with no errors; final line shows `Successfully built` or `naming to docker.io/library/cat-gif-generator:local`.

- [ ] **Step 3: Verify secrets are absent from the image**

Run:
```bash
docker run --rm cat-gif-generator:local ls -la /app | grep -E "secret|session"
```
Expected: no output (`.secret.key` and `.session.token` excluded by `.dockerignore`).

- [ ] **Step 4: Smoke test — app starts**

Run:
```bash
docker run --rm -p 5001:5001 cat-gif-generator:local &
sleep 4
curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/
```
Expected: `200`. Kill the container after.

- [ ] **Step 5: Commit**

```bash
git add Dockerfile
git commit -m "feat: add Dockerfile using Red Hat UBI9 python-313 base"
```

---

### Task 4: Create GitHub Actions Workflow

**Files:**
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: `Dockerfile` (Task 3) — built by the workflow
- Produces: published image at `ghcr.io/hammer-redhat/cat-gif-generator:latest` and `ghcr.io/hammer-redhat/cat-gif-generator:<sha>` on push to `main`

- [ ] **Step 1: Create the workflow directory**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Create `.github/workflows/ci.yml`**

```yaml
name: Build and push container image

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read
  packages: write

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to ghcr.io
        if: github.event_name == 'push'
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: ${{ github.event_name == 'push' }}
          tags: |
            ghcr.io/hammer-redhat/cat-gif-generator:latest
            ghcr.io/hammer-redhat/cat-gif-generator:${{ github.sha && substr(github.sha, 0, 7) || 'local' }}
```

- [ ] **Step 3: Fix the SHA tag expression**

The `substr` function is not valid in GitHub Actions expressions. Use the `github.sha` context with a shell step instead:

```yaml
name: Build and push container image

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read
  packages: write

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to ghcr.io
        if: github.event_name == 'push'
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: ${{ github.event_name == 'push' }}
          tags: |
            ghcr.io/hammer-redhat/cat-gif-generator:latest
            ghcr.io/hammer-redhat/cat-gif-generator:${{ github.sha }}
```

Note: `github.sha` is the full 40-char SHA. ghcr.io accepts long tags; this is fine for a demo. If a 7-char short SHA is preferred, add a prior step:

```yaml
      - name: Compute short SHA
        id: sha
        run: echo "short=${GITHUB_SHA::7}" >> $GITHUB_OUTPUT

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: ${{ github.event_name == 'push' }}
          tags: |
            ghcr.io/hammer-redhat/cat-gif-generator:latest
            ghcr.io/hammer-redhat/cat-gif-generator:${{ steps.sha.outputs.short }}
```

Use the short-SHA variant (cleaner). Final `ci.yml` is shown in Step 4.

- [ ] **Step 4: Write the final `ci.yml`**

```yaml
name: Build and push container image

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read
  packages: write

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to ghcr.io
        if: github.event_name == 'push'
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Compute short SHA
        id: sha
        run: echo "short=${GITHUB_SHA::7}" >> $GITHUB_OUTPUT

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: ${{ github.event_name == 'push' }}
          tags: |
            ghcr.io/hammer-redhat/cat-gif-generator:latest
            ghcr.io/hammer-redhat/cat-gif-generator:${{ steps.sha.outputs.short }}
```

- [ ] **Step 5: Verify the YAML is valid**

Run:
```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))" && echo "YAML valid"
```
Expected: `YAML valid`

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "feat: add GitHub Actions workflow to build and push container image"
```

---

### Task 5: Push to remote and verify

**Files:** none — push only

- [ ] **Step 1: Push all commits to `main`**

```bash
git push origin main
```

- [ ] **Step 2: Confirm the workflow triggered**

Run:
```bash
gh run list --limit 3
```
Expected: a run named `Build and push container image` appears with status `in_progress` or `completed`.

- [ ] **Step 3: Watch the run complete**

```bash
gh run watch
```
Expected: all steps green. The image should be visible at `https://github.com/hammer-redhat/cat-gif-generator/pkgs/container/cat-gif-generator`.
