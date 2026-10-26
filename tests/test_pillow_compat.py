"""Benign image and real Gradio UI smoke tests; no model/API calls or exploits."""

import importlib
from importlib.metadata import version
import os
from pathlib import Path
import sys
import types
from unittest.mock import Mock, patch

os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import httpx


def deny_network(request):
    raise AssertionError(f"External network is disabled in UI smoke tests: {request.url}")


def offline_client(original):
    def initialize(self, *args, **kwargs):
        # Gradio creates clients during import. Keep tests fully offline and
        # independent of host proxy settings (old httpx rejects socks5h URLs).
        kwargs["trust_env"] = False
        kwargs["transport"] = httpx.MockTransport(deny_network)
        original(self, *args, **kwargs)
    return initialize


with patch.object(httpx.Client, "__init__", offline_client(httpx.Client.__init__)), patch.object(httpx.AsyncClient, "__init__", offline_client(httpx.AsyncClient.__init__)):
    import gradio as gr
from gradio.components.image import ImageData
from fastapi.testclient import TestClient
import numpy as np
from PIL import Image
import pytest


def test_patched_versions():
    assert version("Pillow") == "13.0.0"
    assert version("gradio") == "5.5.0+audio2srt.pillow13"


@pytest.mark.parametrize("format", ["PNG", "JPEG", "TIFF", "GIF", "WEBP"])
def test_gradio_image_round_trip(tmp_path, format):
    path = tmp_path / ("input." + format.lower())
    Image.new("RGB", (64, 48), "blue").save(path, format=format)
    component = gr.Image(type="pil", image_mode="RGB", format="png")
    decoded = component.preprocess(ImageData(path=str(path)))
    assert decoded.size == (64, 48)
    decoded.thumbnail((16, 16))
    output = component.postprocess(decoded)
    with Image.open(output.path) as result:
        assert result.size == (16, 12)


def test_imageio_and_moviepy_pillow_paths(tmp_path):
    import imageio.v2 as imageio
    from moviepy.video.VideoClip import ImageClip
    path = tmp_path / "frame.png"
    pixels = np.zeros((24, 32, 3), dtype=np.uint8)
    imageio.imwrite(path, pixels)
    assert imageio.imread(path).shape == pixels.shape
    clip = ImageClip(str(path))
    try:
        assert clip.get_frame(0).shape == pixels.shape
        clip.save_frame(str(tmp_path / "saved.png"))
    finally:
        clip.close()


def stub(name, *attributes):
    module = types.ModuleType(name)
    for attribute in attributes:
        setattr(module, attribute, Mock(side_effect=AssertionError("Backend must not run in UI smoke test")))
    return module


@pytest.mark.parametrize("module_name,entrypoint", [
    ("start_gradio", "start_gradio"),
    ("main_audio_2_video", "main_gradio"),
    ("main_video_add_str", "start_gradio"),
    ("main_video_downloader", "start_gradio"),
])
def test_four_ui_entrypoints(module_name, entrypoint):
    # Isolate only external inference/download/translation backends. Gradio,
    # component construction, event wiring and HTTP routes remain real.
    backends = {
        "whisper": stub("whisper", "load_model"),
        "aeneas.executetask": stub("aeneas.executetask", "ExecuteTask"),
        "aeneas.task": stub("aeneas.task", "Task"),
        "C02_audio_2_video": stub("C02_audio_2_video", "generate_video", "transcribe_and_generate_srt", "srt_to_ass", "wrap_main"),
        "A01_get_audio_from_video": stub("A01_get_audio_from_video", "extract_audio_from_video"),
        "A02_whisper_to_srt": stub("A02_whisper_to_srt", "transcribe_and_generate_srt"),
        "A03_srt_add_cn": stub("A03_srt_add_cn", "translate_srt"),
        "A06_srt_2_ass": stub("A06_srt_2_ass", "convert_srt_to_ass_with_line_split"),
        "A07_ass_in_video": stub("A07_ass_in_video", "embed_ass_subtitles"),
        "yt_dlp": stub("yt_dlp", "YoutubeDL"),
    }
    actual_listdir = os.listdir

    def model_files(path):
        if Path(path) == ROOT / "whisper_models":
            return ["large-v3.pt"]
        return actual_listdir(path)

    launched = []

    def capture_launch(self, **kwargs):
        launched.append(self)

    sys.modules.pop(module_name, None)
    with patch.dict(sys.modules, backends), patch("os.listdir", side_effect=model_files), patch.object(gr.Blocks, "launch", capture_launch):
        module = importlib.import_module(module_name)
        getattr(module, entrypoint)()
        assert len(launched) == 1
        demo = launched[0]
        try:
            with TestClient(gr.routes.App.create_app(demo)) as client:
                assert client.get("/").status_code == 200
                config_response = client.get("/config")
                assert config_response.status_code == 200
                config = config_response.json()
                assert config["components"]
                assert config["dependencies"]
        finally:
            demo.close()
            sys.modules.pop(module_name, None)


def test_builder_rejects_unverified_source(tmp_path):
    from scripts.build_gradio_compat import build_wheel
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        build_wheel(b"not the verified upstream wheel", tmp_path)


def test_builder_changes_only_metadata_and_record(tmp_path, monkeypatch):
    import base64
    import csv
    import hashlib
    import io
    import zipfile
    from scripts import build_gradio_compat as builder

    source = io.BytesIO()
    original_files = {
        "gradio/example.py": b"# unchanged code\n",
        "gradio/templates/index.html": b"unchanged frontend",
        f"{builder.OLD_INFO}/LICENSE": b"unchanged license",
        f"{builder.OLD_INFO}/WHEEL": b"Wheel-Version: 1.0\n",
        f"{builder.OLD_INFO}/METADATA": b"Name: gradio\nVersion: 5.5.0\nRequires-Dist: pillow<12.0,>=8.0\nRequires-Dist: numpy>=1.0\n",
        f"{builder.OLD_INFO}/RECORD": b"old record",
    }
    with zipfile.ZipFile(source, "w") as archive:
        for name, content in original_files.items():
            archive.writestr(name, content)
    source_bytes = source.getvalue()
    # Synthetic fixture only. Production always verifies the pinned PyPI hash.
    monkeypatch.setattr(builder, "UPSTREAM_SHA256", hashlib.sha256(source_bytes).hexdigest())
    first = builder.build_wheel(source_bytes, tmp_path / "first").read_bytes()
    second = builder.build_wheel(source_bytes, tmp_path / "second").read_bytes()
    assert first == second
    with zipfile.ZipFile(io.BytesIO(first)) as archive:
        for name, content in original_files.items():
            if name.endswith(("/METADATA", "/RECORD")):
                continue
            assert archive.read(name.replace(builder.OLD_INFO, builder.NEW_INFO)) == content
        metadata = archive.read(f"{builder.NEW_INFO}/METADATA").decode()
        assert f"Version: {builder.VERSION}\n" in metadata
        assert "Requires-Dist: pillow==13.0.0\n" in metadata
        assert "Requires-Dist: numpy>=1.0\n" in metadata
        rows = list(csv.reader(io.StringIO(archive.read(f"{builder.NEW_INFO}/RECORD").decode())))
        assert len(rows) == len(archive.namelist())
        for name, digest, size in rows:
            if name.endswith("/RECORD"):
                assert digest == size == ""
            else:
                content = archive.read(name)
                assert int(size) == len(content)
                assert digest == "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode()
