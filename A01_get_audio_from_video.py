# -*- encoding: utf-8 -*-
"""
@File: A01_get_audio_from_video.py
@Modify Time: 2024/10/29 12:13       
@Author: Kevin-Chen
@Descriptions: 从视频中获取音频数据
"""

from moviepy.editor import VideoFileClip


def extract_audio_from_video(video_path, audio_output_path):
    # 加载视频文件
    video_clip = VideoFileClip(video_path)

    # 提取音频并保存
    video_clip.audio.write_audiofile(audio_output_path)

    # 关闭视频文件
    video_clip.close()


if __name__ == '__main__':
    pass
