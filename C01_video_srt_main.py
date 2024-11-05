# -*- encoding: utf-8 -*-
"""
@File: B01_video_srt_main.py
@Modify Time: 2024/11/1 11:56       
@Author: Kevin-Chen
@Descriptions: 功能整合:英文视频加中英文字幕
"""

from A01_get_audio_from_video import extract_audio_from_video
from A02_whisper_to_srt import transcribe_and_generate_srt
from A03_srt_add_cn import translate_srt
from A06_srt_2_ass import convert_srt_to_ass_with_line_split
from A07_ass_in_video import embed_ass_subtitles
from B01_youtuber_download import get_video

if __name__ == '__main__':
    # 重要参数
    youtube_url = "https://www.youtube.com/shorts/UoBXCi4jBug"
    main_name = "dace_girl"
    language_code = "en"  # "japanese"
    whisper_model = 'large-v3.pt'  # small.pt, base.pt, large-v3.pt

    # 其他参数
    download_fold = "/Users/chenjunming/Desktop/Audio2srt"
    the_video_path = f"{main_name}.mp4"  # 输入视频路径
    the_audio_path = f"{main_name}.mp3"  # 输出音频路径
    the_srt_path = f"{main_name}_subtitles.srt"
    the_srt_translated_path = f"{main_name}_translated_subtitles.srt"
    the_ass_path = f"{main_name}_translated_subtitles.ass"
    the_output_video_path = f"{main_name}_output.mp4"

    # 从YouTube下载视频
    get_video(youtube_url, download_fold, main_name)
    print(f"YouTube视频已完成下载: {download_fold}/{main_name}")

    # # 提取音频
    # extract_audio_from_video(the_video_path, the_audio_path)
    # print(f"音频已提取: {the_audio_path}")
    #
    # # 音频识别文字
    # transcribe_and_generate_srt(the_audio_path, the_srt_path, language_code,
    #                             whisper_model)
    # print(f"原文字幕已生成: {the_srt_path}")
    #
    # # srt添加中文翻译
    # translate_srt(the_srt_path, the_srt_translated_path, language_code)
    # print(f"中英文字幕已生成: {the_srt_translated_path}")
    #
    # # 生成ASS字幕文件
    # convert_srt_to_ass_with_line_split(the_srt_translated_path, the_ass_path,
    #                                    the_video_path,
    #                                    eng_fontsize_ratio=0.018, cn_fontsize_ratio=0.018)
    # print(f"ASS字幕已生成: {the_ass_path}")
    #
    # # 嵌入字幕到视频中
    # embed_ass_subtitles(the_video_path, the_ass_path, the_output_video_path)
    # print(f"视频已生成: {the_output_video_path}")
