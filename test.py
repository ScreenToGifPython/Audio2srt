from setuptools import setup

APP = ['start_gradio.py']  # 你的主 Python 文件
DATA_FILES = []  # 如果你有额外的文件，可以在这里添加
OPTIONS = {
    'argv_emulation': True,  # 允许应用自动捕获终端参数
    'includes': ['gradio', 'numba', 'numpy', 'tiktoken', 'torch'],  # 指定需要包含的模块
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

# aiofiles==23.2.1
# altgraph==0.17.4
# annotated-types==0.7.0
# anyio==4.6.2.post1
# certifi==2024.8.30
# charset-normalizer==3.4.0
# click==8.1.7
# fastapi==0.115.2
# ffmpy==0.4.0
# filelock==3.16.1
# fsspec==2024.9.0
# gradio==5.1.0
# gradio_client==1.4.0
# h11==0.14.0
# httpcore==1.0.6
# httpx==0.27.2
# huggingface-hub==0.26.0
# idna==3.10
# Jinja2==3.1.4
# llvmlite==0.43.0
# macholib==1.16.3
# markdown-it-py==3.0.0
# MarkupSafe==2.1.5
# mdurl==0.1.2
# ml_dtypes==0.5.0
# modulegraph==0.19.6
# mpmath==1.3.0
# networkx==3.4.1
# numba==0.60.0
# numpy==2.0.2
# onnx==1.17.0
# onnxscript==0.1.0.dev20241020
# orjson==3.10.9
# packaging==24.1
# pandas==2.2.3
# pillow==10.4.0
# protobuf==5.28.2
# pydantic==2.9.2
# pydantic_core==2.23.4
# pydub==0.25.1
# Pygments==2.18.0
# pyinstaller==6.11.0
# pyinstaller-hooks-contrib==2024.9
# python-dateutil==2.9.0.post0
# python-multipart==0.0.12
# pytz==2024.2
# PyYAML==6.0.2
# regex==2024.9.11
# requests==2.32.3
# rich==13.9.2
# ruff==0.7.0
# semantic-version==2.10.0
# setuptools==75.2.0
# shellingham==1.5.4
# six==1.16.0
# sniffio==1.3.1
# starlette==0.40.0
# sympy==1.13.1
# tiktoken==0.8.0
# tomlkit==0.12.0
# torch==2.5.0
# tqdm==4.66.5
# typer==0.12.5
# typing_extensions==4.12.2
# tzdata==2024.2
# urllib3==2.2.3
# uvicorn==0.32.0
# websockets==12.0
