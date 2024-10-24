import time

import gradio as gr
import whisper
from aeneas.executetask import ExecuteTask
from aeneas.task import Task
import tempfile
import re
import os
import sys
import traceback

# 语言映射
language_map = {
    "英语": {"whisper": "en", "aeneas": "eng"},
    "中文": {"whisper": "zh", "aeneas": "cmn"},
    "日语": {"whisper": "ja", "aeneas": "jpn"},
    # 可以根据需要添加更多语言
}

# 检查是否是打包后的可执行文件
if getattr(sys, 'frozen', False):
    # 获取当前文件目录（针对 Nuitka 的打包环境）
    current_dir = os.path.dirname(sys.executable)
else:
    # 开发环境中，使用当前文件路径
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)


def transcribe_audio(audio_file, language_code):
    # 加载模型，确保路径正确
    model_path = os.path.join(current_dir, "small.pt")
    # model_path = os.path.join(current_dir, "small")
    model = whisper.load_model(model_path)

    # 转录音频
    result = model.transcribe(audio_file, language=language_code)
    text = result["text"]
    return text


def split_text_by_punctuation(text, max_length=25):
    # 定义标点符号
    punctuation = '。！？；，,.;!?'
    # 用正则表达式将文本按照标点符号分割
    sentences = re.split(f'([{punctuation}])', text)
    new_sentences = []
    temp_sentence = ''
    for i in range(0, len(sentences) - 1, 2):
        sentence = sentences[i] + sentences[i + 1]
        if len(temp_sentence) + len(sentence) <= max_length:
            temp_sentence += sentence
        else:
            if temp_sentence:
                new_sentences.append(temp_sentence)
            if len(sentence) <= max_length:
                temp_sentence = sentence
            else:
                # 如果单个句子超过最大长度，则需要进一步切分
                temp_sentence = ''
                while len(sentence) > max_length:
                    new_sentences.append(sentence[:max_length])
                    sentence = sentence[max_length:]
                temp_sentence += sentence
    if temp_sentence:
        new_sentences.append(temp_sentence)
    return '\n'.join(new_sentences)


def generate_subtitles(audio_file, text_content, language_code):
    # 在这里处理文本，使每行不超过25个字符，并在标点符号处换行
    processed_text = split_text_by_punctuation(text_content, max_length=25)

    # 创建临时文件
    temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_audio_path = temp_audio.name
    temp_audio.write(open(audio_file, 'rb').read())
    temp_audio.close()

    temp_text = tempfile.NamedTemporaryFile(suffix=".txt", mode='w', delete=False, encoding='utf-8')
    temp_text_path = temp_text.name
    temp_text.write(processed_text)
    temp_text.close()

    temp_srt = tempfile.NamedTemporaryFile(suffix=".srt", delete=False)
    temp_srt_path = temp_srt.name
    temp_srt.close()

    # 创建任务
    config_string = u"task_language=%s|is_text_type=plain|os_task_file_format=srt" % language_code
    task = Task(config_string=config_string)
    task.audio_file_path_absolute = temp_audio_path
    task.text_file_path_absolute = temp_text_path
    task.sync_map_file_path_absolute = temp_srt_path

    # 执行任务
    ExecuteTask(task).execute()
    task.output_sync_map_file()

    # 读取字幕内容
    with open(temp_srt_path, 'r', encoding='utf-8') as f:
        srt_content = f.read()

    # 返回字幕内容和文件路径
    return srt_content, temp_srt_path


def preview_text(text_content):
    # 返回前 100 行
    lines = text_content.splitlines()
    preview = '\n'.join(lines[:100])
    return preview


with gr.Blocks() as demo:
    gr.Markdown("## 音频转文字 & 字幕生成器")

    # 1. 上传音频文件（可试听）
    audio_input = gr.Audio(label="上传音频文件", type="filepath")

    # 语言选择
    language_choice = gr.Dropdown(choices=list(language_map.keys()), label="选择语言", value="中文")

    # 2. 选择文本来源
    text_option = gr.Radio(["上传文本文件", "通过模型识别语音生成文本"], label="文本来源")

    # 占位符，用于存储文本内容
    text_content = gr.State()

    # 上传文本文件选项
    text_file = gr.File(label="上传文本文件", visible=False, file_types=['text'])

    # 生成文本按钮
    generate_text_button = gr.Button("生成文本", visible=False)

    # 4. 预览文本文件（前 100 行）
    text_preview = gr.Textbox(label="文本预览（前 100 行）", lines=10, interactive=False)

    # 下载文本文件按钮
    text_download = gr.File(label="下载文本文件", visible=False)

    # 5. 生成字幕文件按钮
    generate_subtitles_button = gr.Button("生成字幕文件", visible=False)

    # 6. 字幕预览
    subtitles_preview = gr.Textbox(label="字幕预览（前 100 行）", lines=10, interactive=False)

    # 下载字幕文件按钮
    subtitles_download = gr.File(label="下载字幕文件", visible=False)


    # 根据选择显示组件
    def update_components(choice):
        if choice == "上传文本文件":
            return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
        else:
            return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)


    text_option.change(
        update_components,
        inputs=text_option,
        outputs=[text_file, generate_text_button, generate_subtitles_button]
    )


    # 加载上传的文本文件
    def load_text_file(file_obj):
        if file_obj is not None:
            text = open(file_obj.name, 'r', encoding='utf-8').read()
            # 保存文本到临时文件
            temp_text_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8')
            temp_text_file.write(text)
            temp_text_file.close()
            return (
                text,
                gr.update(value=preview_text(text)),
                gr.update(visible=True),
                gr.update(visible=True, value=temp_text_file.name)
            )
        else:
            return '', gr.update(), gr.update(), gr.update()


    text_file.change(
        load_text_file,
        inputs=text_file,
        outputs=[text_content, text_preview, generate_subtitles_button, text_download]
    )


    # 通过语音识别生成文本
    def generate_text(audio_path, language_choice):
        if audio_path is not None:
            language_code_whisper = language_map[language_choice]["whisper"]
            text = transcribe_audio(audio_path, language_code_whisper)
            # 保存文本到临时文件
            temp_text_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8')
            temp_text_file.write(text)
            temp_text_file.close()
            return (
                text,
                gr.update(value=preview_text(text)),
                gr.update(visible=True),
                gr.update(visible=True, value=temp_text_file.name)
            )
        else:
            return '', '', gr.update(), gr.update()


    generate_text_button.click(
        generate_text,
        inputs=[audio_input, language_choice],
        outputs=[text_content, text_preview, generate_subtitles_button, text_download]
    )


    # 生成字幕文件
    def create_subtitles(audio_path, text_content, language_choice):
        if audio_path is not None and text_content:
            language_code_aeneas = language_map[language_choice]["aeneas"]
            srt_content, srt_file_path = generate_subtitles(audio_path, text_content, language_code_aeneas)
            return (
                preview_text(srt_content),
                gr.update(visible=True, value=srt_file_path)
            )
        else:
            return '', gr.update()


    generate_subtitles_button.click(
        create_subtitles,
        inputs=[audio_input, text_content, language_choice],
        outputs=[subtitles_preview, subtitles_download]
    )


def start_gradio():
    demo.launch(inbrowser=True)


def close_gradio():
    demo.close()


if __name__ == '__main__':
    start_gradio()
