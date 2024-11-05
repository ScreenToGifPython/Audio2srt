import os
from moviepy.editor import VideoFileClip


def embed_bilingual_subtitles(video_file, subtitle_file, output_video_file, font="Arial", fontsize_ratio=0.05,
                              color="white", stroke_color="black", stroke_width=1):
    # 加载视频文件
    video = VideoFileClip(video_file)

    # 动态计算字体大小，基于视频的高度
    video_height = video.h  # 获取视频的高度
    fontsize = int(video_height * fontsize_ratio)  # 字体大小设置为视频高度的百分比

    # 设置 ffmpeg 的 subtitles 滤镜参数
    force_style = (
        f"Fontname='{font}',"
        f"Fontsize={fontsize},"
        f"PrimaryColour=&H00{color},"
        f"OutlineColour=&H00{stroke_color},"
        f"Outline={stroke_width},"
        f"Alignment=2"  # 字幕位于下方居中
    )

    # 构建 ffmpeg 命令，使用 moviepy 的 ffmpeg 支持来处理字幕嵌入
    command = (
        f'ffmpeg -i "{video_file}" -vf "subtitles={subtitle_file}:force_style=\'{force_style}\'" '
        f'-c:a copy "{output_video_file}"'
    )
    print(f"运行 ffmpeg 命令: {command}")

    # 运行 ffmpeg 命令
    os.system(command)

    print(f"带有中英文字幕的视频已生成: {output_video_file}")


if __name__ == '__main__':
    the_video_file = "cpu_vs_gpu.mp4"  # 输入视频文件
    the_subtitle_file = "cpu_vs_gpu_subtitles_translated.srt"  # 双语 SRT 文件
    the_output_video_file = "cpu_vs_gpu_subtitles_1.mp4"  # 输出视频文件

    # 嵌入双语字幕并生成视频
    embed_bilingual_subtitles(
        the_video_file, the_subtitle_file, the_output_video_file,
        font="Arial", fontsize_ratio=0.05, color="FFFFFF", stroke_color="000000", stroke_width=1
    )
