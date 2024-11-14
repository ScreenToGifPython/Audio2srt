# -*- encoding: utf-8 -*-
"""
@File: A07_ass_in_video.py
@Modify Time: 2024/11/3 17:08       
@Author: Kevin-Chen
@Descriptions: 
"""
import os


def embed_ass_subtitles(video_file, ass_file, output_video_file):
    # 使用 ffmpeg 将带有 ASS 字幕的样式嵌入到视频中
    command = f'ffmpeg -y -i "{video_file}" -vf "ass={ass_file}" -c:a copy "{output_video_file}"'

    # 运行命令
    os.system(command)


if __name__ == '__main__':
    pass
