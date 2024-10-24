# 语音转文字与字幕生成工具

```bash
  ______                   __  __             ______                        __     
 /      \                 |  \|  \           /      \                      |  \    
|  $$$$$$\ __    __   ____| $$ \$$  ______  |  $$$$$$\  _______   ______  _| $$_   
| $$__| $$|  \  |  \ /      $$|  \ /      \  \$$__| $$ /       \ /      \|   $$ \  
| $$    $$| $$  | $$|  $$$$$$$| $$|  $$$$$$\ /      $$|  $$$$$$$|  $$$$$$\\$$$$$$  
| $$$$$$$$| $$  | $$| $$  | $$| $$| $$  | $$|  $$$$$$  \$$    \ | $$   \$$ | $$ __ 
| $$  | $$| $$__/ $$| $$__| $$| $$| $$__/ $$| $$_____  _\$$$$$$\| $$       | $$|  \
| $$  | $$ \$$    $$ \$$    $$| $$ \$$    $$| $$     \|       $$| $$        \$$  $$
 \$$   \$$  \$$$$$$   \$$$$$$$ \$$  \$$$$$$  \$$$$$$$$ \$$$$$$$  \$$         \$$$$ 
```

## 简介

这是一款基于 OpenAI Whisper 模型的语音转文字工具，能够将音频文件转换为文字，并生成对应的 SRT 字幕文件。该工具旨在帮助用户方便地处理各种语音转录任务，特别适用于将会议录音转成文字、生成视频字幕等场景。

为了提升用户体验，我们为工具设计了一个简洁易用的 GUI 界面，基于 PyQt5 开发。用户可以通过该界面轻松启动前端页面并操作工具。此外，也可以通过命令行运行前端，灵活满足不同用户的需求。

## 主要特性

- **基于 OpenAI Whisper 模型**：
  - 领先的语音识别技术，支持多种语言转录与翻译。
  - 优秀的语音处理能力，适应嘈杂环境、口音以及不同语速。

- **字幕生成**：
  - 轻松生成 SRT 格式的字幕文件，便于视频配字幕及文本标注。

- **直观的用户界面**：
  - 使用 PyQt5 开发的 GUI，让用户可以轻松启动和关闭语音转录任务。
  - 提供自定义的终端用于监控程序运行状态。

- **多种运行方式**：
  - 既支持通过 GUI 操作，也支持通过命令行启动，灵活适应不同的用户需求。

## 安装与使用

### 1. 克隆项目

首先克隆本仓库到本地：

```bash
$ git clone <仓库地址>
$ cd <项目目录>
```

### 2. 安装依赖

请确保你使用的是 Python 3.8+，然后安装项目所需依赖：

```bash
$ pip install -r requirements.txt
```

### 3. 下载模型参数文件

由于模型的参数文件较大，未包含在 Git 仓库中。请从以下地址下载参数文件，并将其放置在项目的指定目录中：

[Whisper 模型参数下载地址](<https://pan.baidu.com/s/1pZ-QFuebeBDXs5Yi0SC6LA?pwd=xbi8>)
链接: https://pan.baidu.com/s/1pZ-QFuebeBDXs5Yi0SC6LA?pwd=xbi8 
提取码: xbi8

将下载的 `.pt` 文件放置到项目的主文件夹 `Audio2srt/` 目录下。

### 4. 运行程序

你可以通过以下两种方式运行工具：

#### GUI 界面启动

```bash
$ python main.py
```

GUI 界面允许你启动前端页面，通过点击按钮来控制工具的启动与停止：

- **Start**：启动子进程，并打开网页前端用于进行语音转文字。
- **Close**：关闭网页所在的子进程。

#### 直接启动前端

如果你更喜欢直接在命令行中操作，你可以运行以下命令直接启动前端：

```bash
$ python start_gradio.py
```

## 依赖

- **Python 3.8+**
- **PyQt5**：用于开发图形用户界面。
- **Whisper**：OpenAI 开发的语音识别模型。

## 贡献

欢迎对本项目提出改进建议！如果你发现任何问题或有新的想法，欢迎提交 Issue 或 Pull Request。

## 许可证

本项目基于 MIT 许可证发布，详情请参阅 LICENSE 文件。
