# -*- encoding: utf-8 -*-
"""
@File: video_rotation.py
@Modify Time: 2024/11/3 13:53       
@Author: Kevin-Chen
@Descriptions: 
"""
from moviepy.editor import VideoFileClip

# 载入横屏视频
clip = VideoFileClip("BJ Hot Pink.mp4")

# 将视频旋转 90 度，变为竖屏
rotated_clip = clip.rotate(-90)

# 保存竖屏视频
rotated_clip.write_videofile("output_video_BJ Hot Pink.mp4")
