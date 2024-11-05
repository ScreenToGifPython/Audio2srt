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
    # 示例用法
    the_video_file = "cpu_vs_gpu.mp4"  # 输入视频文件
    the_ass_file = "cpu_vs_gpu_subtitles_translated.ass"  # 已生成的 ASS 文件
    the_output_video_file = "cpu_vs_gpu_subtitles_2.mp4"  # 输出视频文件

    # 嵌入 ASS 字幕
    embed_ass_subtitles(the_video_file, the_ass_file, the_output_video_file)

    print(f"带有不同字体大小的中英文字幕的视频已生成: {the_output_video_file}")
