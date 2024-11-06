import gradio as gr
import os
from A01_get_audio_from_video import extract_audio_from_video
from A02_whisper_to_srt import transcribe_and_generate_srt
from A03_srt_add_cn import translate_srt
from A06_srt_2_ass import convert_srt_to_ass_with_line_split
from A07_ass_in_video import embed_ass_subtitles


def process_video(video_file, language_code, whisper_model, cn_fontsize_ratio, eng_fontsize_ratio):
    # 获取视频名称
    main_name = os.path.splitext(os.path.basename(video_file.name))[0]

    # 临时文件路径
    the_audio_path = f"{main_name}.mp3"
    the_srt_path = f"{main_name}_subtitles.srt"
    the_srt_translated_path = f"{main_name}_translated_subtitles.srt"
    the_ass_path = f"{main_name}_translated_subtitles.ass"
    the_output_video_path = f"{main_name}_output.mp4"

    try:
        # 提取音频
        extract_audio_from_video(video_file.name, the_audio_path)

        # 音频识别文字
        transcribe_and_generate_srt(the_audio_path, the_srt_path, language_code, whisper_model)

        # srt添加中文翻译
        translate_srt(the_srt_path, the_srt_translated_path, language_code)

        # 生成ASS字幕文件
        convert_srt_to_ass_with_line_split(the_srt_translated_path, the_ass_path, video_file.name,
                                           eng_fontsize_ratio=eng_fontsize_ratio, cn_fontsize_ratio=cn_fontsize_ratio)

        # 嵌入字幕到视频中
        embed_ass_subtitles(video_file.name, the_ass_path, the_output_video_path)

        # 删除临时文件
        os.remove(the_audio_path)
        os.remove(the_srt_path)
        os.remove(the_srt_translated_path)
        os.remove(the_ass_path)

        return the_output_video_path  # 返回视频路径用于预览

    except Exception as e:
        return f"处理过程中出现错误: {e}"


# 当前文件夹路径
current_dir = os.path.dirname(os.path.abspath(__file__))
whisper_model_list = list()
# 从当前文件夹中寻找是否存在 'small.pt', 'base.pt', 'large-v3.pt' 文件
for file_name in ['small.pt', 'base.pt', 'large-v3.pt']:
    file_path = os.path.join(current_dir, file_name)
    if os.path.exists(file_path):
        whisper_model_list.append(file_name)

if not whisper_model_list:
    raise FileNotFoundError("未找到任何 whisper 模型文件，请确保当前目录下存在 small.pt 或 base.pt 或 large-v3.pt 文件")

# 创建Gradio界面
iface = gr.Interface(
    fn=process_video,
    inputs=[
        gr.File(label="上传视频", type="filepath"),
        gr.Dropdown(["English", "Japanese"], label="选择原视频的原始语言", value="English"),
        gr.Dropdown(whisper_model_list, label="选择Whisper模型", value="large-v3.pt"),
        gr.Slider(0.01, 0.05, label="中文字幕字体比例", value=0.018),
        gr.Slider(0.01, 0.05, label="原文字幕字体比例", value=0.018)
    ],
    outputs=gr.Video(label="生成的视频预览"),  # 使用gr.Video组件来显示视频
    title="视频双语字幕生成工具",
    description="上传视频并设置相关参数，生成带有中文和英文字幕的视频。\n"
                "为了避免过于频繁的访问翻译API导致IP被封, 我强制减低了翻译的速度, 请耐心等待 ... "
)

# # 启动Gradio界面
iface.launch(inbrowser=True)
