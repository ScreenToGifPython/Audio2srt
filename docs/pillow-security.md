# Pillow 13 security update

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

## Official dependency support

[Gradio 6.32.0](https://pypi.org/project/gradio/6.32.0/) officially requires
`pillow>=8.0,<14.0`, accepting the pinned Pillow 13.0.0. Gradio 5.5.0 required
Pillow `<12`; 6.31.0 still required `<13`. This update removes the previous
metadata-rewriting builder and local wheel entirely. All packages are installed
from their published distributions with normal dependency resolution.

Gradio's upgrade also requires its matching client, Hugging Face Hub,
SafeHTTPX, newer Starlette/FastAPI and multipart dependencies. These pins are
updated together. Typer is raised to satisfy Hugging Face Hub. The existing
certifi security update is retained.

## Install and validate

Use a fresh Python 3.11 or 3.12 virtual environment:

```sh
python -m venv .venv
# Activate .venv using your platform's normal command.
python -m pip install -r requirements.txt pytest==8.3.4
python -m pip check
GRADIO_ANALYTICS_ENABLED=False python -m pytest tests -q
```

The regression tests verify the installed versions and Gradio's original
Pillow constraint, process benign PNG/JPEG/TIFF/GIF/WebP/BMP images through
real Gradio and Pillow, check grayscale/alpha/CMYK conversion, iterate and
resave multiframe PNG/GIF/TIFF/WebP, and check a grayscale-to-RGB TIFF frame
transition. ImageIO/MoviePy image loading and saving, plus a short FFmpeg MP4
encode/decode round trip, are also covered.

All four web entrypoints (`start_gradio.py`, `main_audio_2_video.py`,
`main_video_add_str.py`, `main_video_downloader.py`) are constructed with real
Gradio components and event wiring. Each starts a real loopback HTTP server;
tests check its home page, configuration, file upload and download. The text
upload/preview callback also runs through Gradio's preprocessing, session state
and output serialization. Only model/inference, translation and download
backends are stubbed; no real model, external API,
video download or exploit is used. Tests block Gradio's import-time HTTP
clients, then permit only loopback/test-client requests during UI tests. The
separate certifi tests check the actual trust bundle.

The CI workflow performs a clean full requirements installation, `pip check`
and regressions on Python 3.11 and 3.12. Inspect its result for the final commit;
an amended dependency constraint or a previous CI run is not compatibility
proof for a new revision.

These are focused compatibility checks, not full transcription, desktop GUI,
browser interaction or production deployment verification. Other dependencies
are outside this remediation's security audit scope. Existing installations
must be rebuilt/reinstalled and restarted to load the patched dependencies.
