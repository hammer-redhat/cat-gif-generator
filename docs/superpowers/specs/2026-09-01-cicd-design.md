# CI/CD Design — cat-gif-generator

**Date:** 2026-09-01  
**Repo:** github.com/hammer-redhat/cat-gif-generator  
**Status:** Approved

## Goal

Build a CI/CD pipeline that packages the cat-gif-generator Flask app as a container image and publishes it to GitHub Container Registry (ghcr.io) on every merge to `main`. Pull requests trigger a build-only validation (no push).

## Container Image

### Base image

`registry.access.redhat.com/ubi9/python-313`

Chosen to be consistent with the Red Hat Lightwell package index already used by the app. Pre-built wheels from Lightwell install cleanly on UBI9 with no compiler toolchain needed.

### Build strategy

Single-stage build. The app is pure Python with pre-built wheels; a multi-stage build offers no meaningful size reduction here.

Layer order (optimised for cache hits):
1. Set working directory `/app`
2. Copy `requirements.txt`
3. Install dependencies via pip with `--extra-index-url` pointing at the Lightwell index
4. Copy application source

Exposed port: `5001` (matches `app.py` default).  
Entrypoint: `python3 app.py`

### `.dockerignore`

Excludes from the build context:
- `.secret.key`, `.session.token` — runtime-generated secrets must never be baked into an image
- `__pycache__/`, `*.pyc`
- `.git/`, `.remember/`
- `docs/`

## GitHub Actions Workflow

**File:** `.github/workflows/ci.yml`

### Triggers

| Event | Branch | Effect |
|-------|--------|--------|
| `push` | `main` | Build + push image |
| `pull_request` | targeting `main` | Build only (no push) |

### Steps

1. **Checkout** — `actions/checkout@v4`
2. **Set up Docker Buildx** — `docker/setup-buildx-action@v3`
3. **Log in to ghcr.io** — `docker/login-action@v3` using `GITHUB_TOKEN` (built-in; no manual secret configuration required). Skipped on PR runs via `if: github.event_name == 'push'`.
4. **Build and push** — `docker/build-push-action@v6`
   - `push: ${{ github.event_name == 'push' }}` — pushes on `main`, builds-only on PR
   - Tags (applied on push): `latest` + 7-character commit SHA

### Image tags

```
ghcr.io/hammer-redhat/cat-gif-generator:latest
ghcr.io/hammer-redhat/cat-gif-generator:<7-char-sha>
```

SHA tag preserves a pinnable reference for every build. `latest` tracks `main` HEAD.

### Permissions

The workflow requests `packages: write` so `GITHUB_TOKEN` can push to ghcr.io. No additional repository secrets are required.

## Files Created / Modified

| File | Action |
|------|--------|
| `Dockerfile` | Create |
| `.dockerignore` | Create |
| `.github/workflows/ci.yml` | Create |
| `.gitignore` | Create (add `.secret.key`, `.session.token`, `__pycache__/`) |

## Success Criteria

- `docker build` completes locally against the UBI9 base with packages sourced from the Lightwell index
- GitHub Actions runs on every PR and every push to `main`
- On push to `main`, the image is visible at `ghcr.io/hammer-redhat/cat-gif-generator`
- `.secret.key` and `.session.token` are absent from the built image
