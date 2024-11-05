# -*- encoding: utf-8 -*-
"""
@File: A03_create_srt.py
@Modify Time: 2024/10/29 13:30       
@Author: Kevin-Chen
@Descriptions: 创建srt字幕文件
"""
from aeneas.executetask import ExecuteTask
from aeneas.task import Task
import os


def generate_srt(audio_file, text_file, srt_output_file):
    # 创建 aeneas 任务配置
    task_config = u"task_language=eng|is_text_type=plain|os_task_file_format=srt"
    # 创建任务对象
    task = Task(config_string=task_config)
    # 设置音频和文本文件
    task.audio_file_path_absolute = os.path.abspath(audio_file)
    task.text_file_path_absolute = os.path.abspath(text_file)
    # 设置输出文件路径
    task.sync_map_file_path_absolute = os.path.abspath(srt_output_file)
    # 执行任务
    ExecuteTask(task).execute()
    # 保存 SRT 文件
    task.output_sync_map_file()


if __name__ == '__main__':
    the_audio_file = "gpu.mp3"  # 音频文件路径
    the_text_file = "output_processed.txt"  # 已处理的文本文件路径
    the_srt_output_file = "output_subtitles.srt"  # 输出 SRT 文件路径
    generate_srt(the_audio_file, the_text_file, the_srt_output_file)
    print(f"SRT 文件已生成: {the_srt_output_file}")
