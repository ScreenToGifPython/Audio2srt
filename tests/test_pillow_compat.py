"""Benign image and real Gradio UI smoke tests; no model/API calls or exploits."""

import importlib
from functools import partial
from importlib.metadata import requires, version
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


def loopback_client(original):
    def check(request):
        if request.url.host not in {"127.0.0.1", "localhost", "testserver"}:
            deny_network(request)

    async def async_check(request):
        check(request)

    def initialize(self, *args, **kwargs):
        kwargs["trust_env"] = False
        hooks = kwargs.setdefault("event_hooks", {})
        hooks.setdefault("request", []).append(
            async_check if isinstance(self, httpx.AsyncClient) else check,
        )
        original(self, *args, **kwargs)
    return initialize


with (
    patch.object(httpx.Client, "__init__", offline_client(httpx.Client.__init__)),
    patch.object(httpx.AsyncClient, "__init__", offline_client(httpx.AsyncClient.__init__)),
):
    import gradio as gr
from gradio.components.image import ImageData
from fastapi.testclient import TestClient
from gradio.state_holder import SessionState
import numpy as np
from PIL import Image
from packaging.requirements import Requirement
import pytest


def test_patched_versions():
    assert version("Pillow") == "13.0.0"
    assert version("gradio") == "6.32.0"
    pillow_requirement, = [
        Requirement(item) for item in requires("gradio")
        if Requirement(item).name.lower() == "pillow"
    ]
    assert version("Pillow") in pillow_requirement.specifier


@pytest.mark.parametrize("format", ["PNG", "JPEG", "TIFF", "GIF", "WEBP", "BMP"])
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


@pytest.mark.parametrize("format", ["PNG", "GIF", "TIFF", "WEBP"])
def test_multiframe_load_and_resave(tmp_path, format):
    path = tmp_path / ("animation." + format.lower())
    frames = [Image.new("RGB", (24, 16), color) for color in ("red", "blue")]
    frames[0].save(path, format=format, save_all=True, append_images=frames[1:],
                   duration=100, loop=0)
    with Image.open(path) as image:
        assert image.n_frames == 2
        for index, expected in enumerate(((255, 0, 0), (0, 0, 255))):
            image.seek(index)
            image.load()
            rgb = image.convert("RGB")
            assert rgb.size == (24, 16)
            assert np.max(np.abs(np.array(rgb.getpixel((12, 8))) - expected)) <= 3
            rgb.save(tmp_path / f"frame-{index}.png")


def test_tiff_frame_mode_transition(tmp_path):
    path = tmp_path / "mode-change.tiff"
    Image.new("L", (24, 16), 80).save(
        path, save_all=True, append_images=[Image.new("RGB", (24, 16), "blue")],
    )
    with Image.open(path) as image:
        image.load()
        assert image.mode == "L"
        assert image.getpixel((12, 8)) == 80
        image.seek(1)
        image.load()
        assert image.mode == "RGB"
        assert image.getpixel((12, 8)) == (0, 0, 255)


@pytest.mark.parametrize("mode", ["L", "RGBA", "CMYK"])
def test_gradio_converts_image_modes(tmp_path, mode):
    path = tmp_path / ("input.tiff" if mode == "CMYK" else "input.png")
    Image.new("RGB", (24, 16), "blue").convert(mode).save(path)
    component = gr.Image(type="pil", image_mode="RGB", format="png")
    decoded = component.preprocess(ImageData(path=str(path)))
    assert decoded.mode == "RGB"
    assert decoded.size == (24, 16)
    with Image.open(component.postprocess(decoded).path) as output:
        np.testing.assert_array_equal(np.asarray(output), np.asarray(decoded))


def test_imageio_and_moviepy_pillow_paths(tmp_path):
    import imageio.v2 as imageio
    from moviepy.video.VideoClip import ImageClip
    from moviepy.video.io.VideoFileClip import VideoFileClip
    path = tmp_path / "frame.png"
    pixels = np.zeros((24, 32, 3), dtype=np.uint8)
    imageio.imwrite(path, pixels)
    assert imageio.imread(path).shape == pixels.shape
    clip = ImageClip(str(path)).set_duration(0.4)
    try:
        assert clip.get_frame(0).shape == pixels.shape
        clip.save_frame(str(tmp_path / "saved.png"))
        output = tmp_path / "clip.mp4"
        clip.write_videofile(str(output), fps=5, codec="libx264", audio=False,
                             logger=None)
        with VideoFileClip(str(output)) as video:
            frame = video.get_frame(0)
            assert frame.shape == pixels.shape
            assert np.max(frame) <= 3
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
    original_launch = gr.Blocks.launch

    def capture_launch(self, **kwargs):
        launched.append(self)
        return original_launch(self, **{
            **kwargs, "inbrowser": False, "share": False,
            "prevent_thread_lock": True, "server_name": "127.0.0.1", "quiet": True,
        })

    sys.modules.pop(module_name, None)
    with (
        patch.dict(sys.modules, backends),
        patch("os.listdir", side_effect=model_files),
        patch.object(gr.Blocks, "launch", capture_launch),
        patch.object(httpx.Client, "__init__", loopback_client(httpx.Client.__init__)),
        patch.object(httpx.AsyncClient, "__init__", loopback_client(httpx.AsyncClient.__init__)),
    ):
        try:
            module = importlib.import_module(module_name)
            getattr(module, entrypoint)()
            assert len(launched) == 1
            demo = launched[0]
            with httpx.Client(trust_env=False) as live_client:
                assert live_client.get(demo.local_url).status_code == 200
            with TestClient(demo.app) as client:
                assert client.get("/").status_code == 200
                config_response = client.get("/config")
                assert config_response.status_code == 200
                config = config_response.json()
                assert config["components"]
                assert config["dependencies"]
                upload = client.post("/gradio_api/upload", files={
                    "files": ("sample.txt", "你好，字幕。".encode(), "text/plain"),
                })
                assert upload.status_code == 200
                uploaded_path, = upload.json()
                assert Path(uploaded_path).read_text() == "你好，字幕。"
                downloaded = client.get(f"/gradio_api/file={uploaded_path}")
                assert downloaded.status_code == 200
                assert downloaded.content == "你好，字幕。".encode()
                if module_name == "start_gradio":
                    state = SessionState(demo)
                    index, fn = next(
                        (index, fn) for index, fn in demo.fns.items()
                        if getattr(fn.fn, "__name__", None) == "load_text_file"
                    )
                    result = client.portal.call(partial(
                        demo.process_api, index,
                        [{"path": uploaded_path, "meta": {"_type": "gradio.FileData"}}],
                        state=state,
                    ))
                    assert state[fn.outputs[0]._id] == "你好，字幕。"
                    assert result["data"][1]["value"] == "你好，字幕。"
                    download_value = result["data"][3]["value"]
                    assert Path(download_value["path"]).read_text() == "你好，字幕。"
        finally:
            for demo in launched:
                demo.close()
            sys.modules.pop(module_name, None)
