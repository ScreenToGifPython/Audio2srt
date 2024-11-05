# -*- encoding: utf-8 -*-
"""
@File: B01_youtuber_download.py
@Modify Time: 2024/11/2 17:42       
@Author: Kevin-Chen
@Descriptions: 
"""
import subprocess
import os
import re


def get_best_mp4_itag(url):
    """获取视频的最高清 MP4 格式的 itag"""
    try:
        # 获取视频的可用格式列表
        result = subprocess.run(
            ["python",  # 使用 python3 来执行 you-get
             "/Users/chenjunming/Downloads/you-get-develop/you-get",  # you-get 脚本路径
             "-i", url],
            text=True,
            capture_output=True,
            check=True
        )

        # 在结果中查找 MP4 格式的 itag 和分辨率
        pattern = re.compile(r"- itag:\s+(\d+)\s+container:\s+mp4\s+quality:\s+(\d+)x(\d+)")
        mp4_formats = pattern.findall(result.stdout)

        # 按分辨率降序排序，选择最高分辨率的 itag
        best_mp4_format = sorted(mp4_formats, key=lambda x: (int(x[1]), int(x[2])), reverse=True)[0]
        best_itag = best_mp4_format[0]
        print(f"找到最高清的 MP4 格式 itag: {best_itag}")
        return best_itag
    except (subprocess.CalledProcessError, IndexError):
        print("未找到可用的 MP4 格式。")
        return None


def get_video(url, output_dir, output_filename=None):
    # 检查下载文件夹是否存在，如果不存在则创建
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建下载文件夹: {output_dir}")

    # 选择下载的格式
    format_id = get_best_mp4_itag(url)

    # 构造 you-get 命令行
    if format_id:
        command = [
            "python",  # 使用 python3 来执行 you-get
            "/Users/chenjunming/Downloads/you-get-develop/you-get",  # you-get 脚本路径
            "-o", output_dir,  # 指定输出目录
            "-f",  # 强制覆盖已存在的文件
            "--output-filename", output_filename,
            "-F", format_id,  # 指定下载格式为 mp4
            url  # 下载目标URL
        ]
    else:
        command = [
            "python",  # 使用 python3 来执行 you-get
            "/Users/chenjunming/Downloads/you-get-develop/you-get",  # you-get 脚本路径
            "-o", output_dir,  # 指定输出目录
            "-f",  # 强制覆盖已存在的文件
            "--output-filename", output_filename,
            url  # 下载目标URL
        ]

    # 执行命令
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print("下载完成:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("下载出错:", e.stderr)


if __name__ == '__main__':
    # 设置下载链接和下载目录
    the_url = "https://www.youtube.com/watch?v=W8dXOz_XZL8&ab_channel=PlatinaJazz"
    the_output_dir = "/Users/chenjunming/Desktop/Audio2srt/download_audio"
    the_file_name = "moonlight_jazz_cover"
    # 开始下载
    get_video(the_url, the_output_dir, the_file_name)
