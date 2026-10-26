"""Build the explicitly maintained Gradio 5.5.0 / Pillow 13 compatibility wheel.

No dependency checks are disabled. Only the upstream wheel's Pillow constraint
and local version are changed; all Python code and frontend assets are retained.
"""

import argparse
import base64
import csv
import hashlib
import io
from pathlib import Path
import urllib.request
import zipfile


UPSTREAM_URL = (
    "https://files.pythonhosted.org/packages/18/a1/"
    "1bdb57a072903b222b1a745aa634cb845ff5f52a88ddd5ed1640ecf30beb/"
    "gradio-5.5.0-py3-none-any.whl"
)
UPSTREAM_SHA256 = "48ea11ae1376d9506eb295dbeb4d3ff962830a6e2d8aa9085e025cce3c04e544"
VERSION = "5.5.0+audio2srt.pillow13"
WHEEL_NAME = f"gradio-{VERSION}-py3-none-any.whl"
OLD_INFO = "gradio-5.5.0.dist-info"
NEW_INFO = f"gradio-{VERSION}.dist-info"


def build_wheel(source: bytes, output: Path) -> Path:
    if hashlib.sha256(source).hexdigest() != UPSTREAM_SHA256:
        raise ValueError("Upstream Gradio wheel SHA-256 mismatch; refusing to patch")
    entries = {}
    with zipfile.ZipFile(io.BytesIO(source)) as upstream:
        for name in upstream.namelist():
            if name == f"{OLD_INFO}/RECORD":
                continue
            content = upstream.read(name)
            if name == f"{OLD_INFO}/METADATA":
                for old, new in (
                    (b"Version: 5.5.0\n", f"Version: {VERSION}\n".encode()),
                    (b"Requires-Dist: pillow<12.0,>=8.0\n",
                     b"Requires-Dist: pillow==13.0.0\n"),
                ):
                    if content.count(old) != 1:
                        raise ValueError("Unexpected upstream metadata; refusing to patch")
                    content = content.replace(old, new)
            entries[name.replace(OLD_INFO + "/", NEW_INFO + "/", 1)] = content
    record = io.StringIO(newline="")
    writer = csv.writer(record, lineterminator="\n")
    for name, content in sorted(entries.items()):
        digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode()
        writer.writerow((name, f"sha256={digest}", len(content)))
    writer.writerow((f"{NEW_INFO}/RECORD", "", ""))
    entries[f"{NEW_INFO}/RECORD"] = record.getvalue().encode()
    output.mkdir(parents=True, exist_ok=True)
    destination = output / WHEEL_NAME
    temporary = destination.with_suffix(".tmp")
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as wheel:
        for name, content in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=(2024, 11, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            wheel.writestr(info, content)
    temporary.replace(destination)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="Previously downloaded official wheel (hash checked)")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / ".wheels")
    args = parser.parse_args()
    if args.source:
        source = args.source.read_bytes()
    else:
        with urllib.request.urlopen(UPSTREAM_URL, timeout=120) as response:
            source = response.read()
    result = build_wheel(source, args.output)
    print(f"Built {result}")
    print(f"SHA-256: {hashlib.sha256(result.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
