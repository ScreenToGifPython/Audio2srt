# Pillow 13 security compatibility patch

## Why this patch exists

The application pinned Pillow 11.0.0. The reviewed advisories below list Pillow
13.0.0 as patched. They include specific JPEG, TIFF, GIF, PDF and morphology
paths; an affected dependency does not establish exploitation or that every
application entrypoint reaches those paths.

- [JPEG decoder](https://github.com/advisories/GHSA-8g5g-8vmr-9782)
- [TIFF decoder](https://github.com/advisories/GHSA-c6hw-5grf-ff96)
- [GIF decoder](https://github.com/advisories/GHSA-65qm-jvmh-6pqg)
- [PDF append parser](https://github.com/advisories/GHSA-p4wg-p73j-c528)
- [TIFF JPEG strips](https://github.com/advisories/GHSA-q45j-58j2-45rg)
- [Morphology](https://github.com/advisories/GHSA-58r4-6rv3-gfh8)
- [TIFF encoder](https://github.com/advisories/GHSA-pchr-8j38-3x4p)

Gradio 5.5.0 requires Pillow `<12`. Even Gradio 6.30.0 requires Pillow `<13`.
Simply changing the Pillow pin produces `ResolutionImpossible`. Replacing the
UI framework would be a much larger change.

## Reproducible, project-maintained wheel

Run from the repository root using Python 3.11 or 3.12:

```sh
python -m venv .venv
# Activate .venv using your platform's normal command.
python scripts/build_gradio_compat.py
python -m pip install -r requirements.txt
python -m pip check
```

The builder downloads **only the official Gradio 5.5.0 wheel**, with a fixed URL
and SHA-256 `48ea11ae1376d9506eb295dbeb4d3ff962830a6e2d8aa9085e025cce3c04e544`.
It fails on a different hash or unexpected metadata. An already downloaded
official wheel can be supplied with `--source`; it receives the same hash check.

The local package version is `5.5.0+audio2srt.pillow13`. The only upstream
metadata changes are the version and the Pillow requirement, now exactly
`13.0.0`. The dist-info directory and RECORD hashes are regenerated. All Gradio
Python code, frontend assets and license files are retained byte-for-byte.
Output ordering and archive timestamps are fixed for reproducible builds.

The wheel is generated into `.wheels/`, not committed as a 57 MB binary.
`requirements.txt` references that exact local wheel. No `--no-deps` installation
or resolver override is used; pip validates the amended package's dependencies.
The builder is required before installation in a fresh checkout.

This is **our compatibility patch, not an official Gradio release or upstream
endorsement**. Maintain it until an official compatible release has been tested.
Do not remove the local version label or silently broaden the Pillow pin.
On future Gradio updates, re-check its dependency constraints and image APIs,
repeat the tests, then remove this builder/local-wheel requirement if no longer
needed. Future Pillow changes also require explicit compatibility validation.

## Validation

```sh
python -m pip install pytest==8.3.4
GRADIO_ANALYTICS_ENABLED=False python -m pytest tests/test_pillow_compat.py -q
python -m pip check
```

The tests exercise benign PNG/JPEG/TIFF/GIF/WebP processing through real Gradio
and Pillow, ImageIO/MoviePy image loading and saving, and all four web entrypoints:
`start_gradio.py`, `main_audio_2_video.py`, `main_video_add_str.py` and
`main_video_downloader.py`. Real Gradio component/event construction and ASGI
home/config routes are checked. Only inference, translation and download
backends/model listings are stubbed; tests never load a model, call an external
API, download a video, or run an exploit. Import-time Gradio HTTP clients are
blocked in tests so host proxy settings cannot cause network traffic.

The builder tests verify rejection of an invalid source hash, deterministic
output, unchanged code/assets/license bytes, dependency metadata and RECORD
integrity. The CI workflow installs the full pinned requirements and runs these checks.
Its result must be inspected for the specific commit; configuration alone is
not proof that the CI run passed.

These are focused compatibility checks, not full transcription, FFmpeg,
desktop GUI, browser interaction, or production deployment verification.
Existing unrelated dependencies are not comprehensively security-audited by
this change. Installing this branch does not update already deployed copies.
