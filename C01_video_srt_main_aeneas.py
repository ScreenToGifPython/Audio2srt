# -*- encoding: utf-8 -*-
"""
@File: C01_video_srt_main_aeneas.py
@Modify Time: 2024/11/3 19:00       
@Author: Kevin-Chen
@Descriptions: 基于 aeneas 的字幕对齐
"""

from A01_get_audio_from_video import extract_audio_from_video
from A02_whisper_to_srt import transcribe_and_generate_srt
from A03_srt_add_cn import translate_srt
from A06_srt_2_ass import convert_srt_to_ass_with_line_split
from A07_ass_in_video import embed_ass_subtitles

if __name__ == '__main__':
    main_name = "cpu_vs_gpu"
    the_video_path = f"{main_name}.mp4"  # 输入视频路径
    the_audio_path = f"{main_name}.mp3"  # 输出音频路径
    the_srt_path = f"{main_name}_subtitles.srt"
    the_srt_translated_path = f"{main_name}_translated_subtitles.srt"
    the_ass_path = f"{main_name}_translated_subtitles.ass"
    the_output_video_path = f"{main_name}_output.mp4"

    # 提取音频
    extract_audio_from_video(the_video_path, the_audio_path)
    print(f"音频已提取: {the_audio_path}")
    # 音频识别文字
    transcribe_and_generate_srt(the_audio_path, the_srt_path)
    print(f"英文字幕已生成: {the_srt_path}")
