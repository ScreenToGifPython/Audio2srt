# -*- encoding: utf-8 -*-
"""
@File: main_audio_2_video.py
@Modify Time: 2024/11/19 16:06       
@Author: Kevin-Chen
@Descriptions: 将播客音频转为视频 (纯文字的视频)
"""

import os
import gradio as gr
from C02_audio_2_video import generate_video
from C02_audio_2_video import transcribe_and_generate_srt, srt_to_ass, wrap_main

# 语言映射
language_map = {
    "英语": {"whisper": "en", "aeneas": "eng"},
    "中文": {"whisper": "zh", "aeneas": "cmn"},
    "日语": {"whisper": "ja", "aeneas": "jpn"},
    # 可以根据需要添加更多语言
}

# 当前文件夹路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 从whisper_models文件夹中寻找是否存在 .pt 文件
whisper_model_folder = os.path.join(current_dir, "whisper_models")
whisper_model_list = list()
for file_name in os.listdir(whisper_model_folder):
    if file_name.endswith(".pt"):
        whisper_model_list.append(file_name)

# 检查是否找到模型文件, 如果没有则报错
if not whisper_model_list:
    raise FileNotFoundError(
        "未找到任何 whisper 模型文件，请确保当前目录下存在 small.pt 或 base.pt 或 large-v3.pt 文件")

# 字幕文件输出路径
the_srt_output_file = "zzz_output.srt"
the_ass_file = "zzz_output.ass"
wrapped_ass_file = "zzz_output_wrapped.ass"
video_path = "zzz_output_video.mp4"


def generate_video_main(audio_file):
    generate_video(audio_file, video_path, wrapped_ass_file)
    return video_path


# 语音识别为ASS字幕文件
def generate_text(audio_file, language_choice, model_choice):
    model_choice = os.path.join(whisper_model_folder, model_choice)
    language_choice = language_map[language_choice]["whisper"]

    # 生成字幕
    transcribe_and_generate_srt(audio_file, the_srt_output_file, language=language_choice,
                                whisper_model=model_choice)

    # 将 SRT 字幕转换为 ASS 字幕
    srt_to_ass(the_srt_output_file, the_ass_file)

    # 将 ASS 字幕智能换行
    txt = wrap_main(input_file=the_ass_file, output_file=wrapped_ass_file, max_len=12)
    return txt, wrapped_ass_file


def main_gradio():
    # 创建一个Gradio Blocks对象，用于构建自定义的UI布局
    with gr.Blocks() as demo:
        # 显示项目介绍和使用说明的Markdown文本
        gr.Markdown("# 将播客音频转为视频")

        # 上传音频文件
        gr.Markdown("## Step.1 上传音频文件")
        with gr.Row():
            audio_input = gr.Audio(label="上传音频文件", type="filepath")

        # 选择对话的语言
        gr.Markdown("## Step.2 语音识别")
        with gr.Column():
            with gr.Row():
                # 下拉框: 选择语言
                language_choice = gr.Dropdown(choices=list(language_map.keys()), label="选择语言", value="中文")
                # 下拉框: 选择语音识别模型
                model_choice = gr.Dropdown(whisper_model_list, label="选择Whisper模型", value="large-v3.pt")
            # 按钮: 语音识别
            generate_text_button = gr.Button("开始识别")

        # 选择对话的语言
        gr.Markdown("## Step.3 字幕预览")
        with gr.Column():
            # 预览文本
            text_preview = gr.Textbox(label="文本预览", lines=3, interactive=False)
            # 下载文本文件按钮
            text_download = gr.File(label="下载文本文件")

        # 开始生成视频
        gr.Markdown("## Step.4 生成视频")
        with gr.Column():
            with gr.Row():
                # # 勾选框: 是否删除临时的字幕文件
                # delete_ass = gr.Checkbox(label="是否删除临时的字幕文件")
                # 按钮: 生成视频
                generate_video_button = gr.Button("开始视频生成")

            show_video = gr.Video(label="视频预览")

        # 功能: 语音识别
        generate_text_button.click(
            generate_text,
            inputs=[audio_input, language_choice, model_choice],
            outputs=[text_preview, text_download]
        )

        # 功能: 生成视频
        generate_video_button.click(
            generate_video_main,
            inputs=[audio_input],
            outputs=show_video
        )

    demo.launch(inbrowser=True)


if __name__ == '__main__':
    main_gradio()
