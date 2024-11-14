# -*- encoding: utf-8 -*-
"""
@File: test_5.py
@Modify Time: 2024/10/30 16:55       
@Author: Kevin-Chen
@Descriptions: 基于音频生成有字幕的视频
"""
from A02_whisper_to_srt import transcribe_and_generate_srt

import os
import re
import jieba
import pysubs2
import subprocess


def srt_to_ass(srt_file, ass_file):
    subs = pysubs2.load(srt_file)
    # 定义新的样式
    style = subs.styles["Default"]
    style.fontname = "Arial"
    style.fontsize = 40
    style.primarycolor = pysubs2.Color(255, 255, 255)  # 白色
    style.alignment = pysubs2.Alignment.MIDDLE_CENTER  # 居中对齐
    # style.wrap_style = 1  # 智能换行
    # # 设置左右边距，单位为像素，可根据需要调整
    # style.marginl = 120  # 左边距
    # style.marginr = 120  # 右边距
    subs.styles["Default"] = style
    # 保存为 ASS 文件
    subs.save(ass_file)


def custom_tokenize(text):
    # Split text into segments: sequences of English letters or other characters
    pattern = re.compile(r'[a-zA-Z ]+|[^a-zA-Z ]+')
    tokens = []
    for segment in pattern.findall(text):
        if re.match(r'[a-zA-Z ]+', segment):
            # Treat sequences of English letters and spaces as single tokens
            tokens.append(segment)
        else:
            # Use jieba to tokenize Chinese text
            tokens.extend(jieba.lcut(segment))
    return tokens


def get_token_length(token):
    num_letters = 0
    num_others = 0
    for char in token:
        if char.isspace() or char in set('，。、！？；：…—“”（）,.!?;:"\'“”‘’()'):
            continue  # Do not count spaces or punctuation
        elif re.match(r'[A-Za-z]', char):
            num_letters += 1
        else:
            num_others += 1  # Assume it's a Chinese character
    # Every two English letters count as one character length
    length = num_others + (num_letters + 1) // 2
    return length


def wrap_text(text, max_len):
    lines = []
    text = text.replace(r'\N', '')  # Remove existing line breaks
    while text:
        # Tokenize the text
        words = custom_tokenize(text)
        # Calculate cumulative lengths of words
        cum_lengths = [0]
        for word in words:
            token_length = get_token_length(word)
            cum_lengths.append(cum_lengths[-1] + token_length)
        total_length = cum_lengths[-1]
        if total_length <= max_len:
            lines.append(text)
            break
        else:
            # Try to find the last punctuation mark before MAX_LINE_LENGTH
            break_point = -1
            current_length = 0
            for idx, word in enumerate(words):
                current_length += get_token_length(word)
                if current_length > max_len:
                    break
                # Check for punctuation mark at the end of the word
                if word and word[-1] in set('，。、！？；：…—“”（）,.!?;:"\'“”‘’()'):
                    break_point = idx + 1
            if break_point != -1:
                # Break at the punctuation mark
                line1 = ''.join(words[:break_point])
                text = ''.join(words[break_point:])
                lines.append(line1)
            else:
                # Find the break_point near the middle without exceeding MAX_LINE_LENGTH
                half_length = total_length / 2
                best_break_point = 0
                min_diff = total_length
                for i in range(1, len(cum_lengths)):
                    line_length = cum_lengths[i]
                    remaining_length = total_length - line_length
                    if line_length > max_len or remaining_length > max_len:
                        continue
                    diff = abs(line_length - half_length)
                    if diff < min_diff:
                        min_diff = diff
                        best_break_point = i
                if best_break_point == 0:
                    # Forcefully split without splitting words
                    current_line = ''
                    current_length = 0
                    idx = 0
                    for word in words:
                        word_length = get_token_length(word)
                        if current_length + word_length <= max_len:
                            current_line += word
                            current_length += word_length
                            idx += 1
                        else:
                            break
                    lines.append(current_line)
                    text = ''.join(words[idx:])
                else:
                    # Break at the best break_point
                    line1 = ''.join(words[:best_break_point])
                    line2 = ''.join(words[best_break_point:])
                    lines.append(line1)
                    text = line2
    return r'\N'.join(lines)


def wrap_main(input_file="subtitles.ass", output_file="wrapped_subtitles.ass", max_len=15):
    subs = pysubs2.load(input_file, encoding='utf-8')
    for line in subs:
        if line.type == 'Dialogue':
            new_text = wrap_text(line.text, max_len)
            line.text = new_text
    subs.save(output_file, encoding='utf-8')


def get_audio_duration(wav_file):
    cmd = [
        'ffprobe',
        '-i', wav_file,
        '-show_entries', 'format=duration',
        '-v', 'quiet',
        '-of', 'csv=p=0'
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(result)
    duration = float(result.stdout.strip())
    return duration


def generate_video(wav_file, output_file, ass_file):
    # 获取音频文件的持续时间
    duration = get_audio_duration(wav_file)

    # 生成黑色背景视频
    video_file = 'black_video.mp4'
    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        f'-i', f'color=black:s=1920x1080:d={duration}',
        '-c:v', 'libx264',
        '-t', str(duration),
        '-y',  # 覆盖输出文件
        video_file
    ]
    subprocess.run(cmd, check=True)

    # 合并音频和字幕到视频中
    cmd = [
        'ffmpeg',
        '-i', video_file,
        '-i', wav_file,
        '-vf', f"subtitles='{ass_file}'",
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        '-y',  # 覆盖输出文件
        output_file
    ]
    subprocess.run(cmd, check=True)

    # 删除临时文件,黑幕视频
    os.remove(video_file)


if __name__ == '__main__':
    main_name = "期权3"
    the_audio_file = f"{main_name}.wav"
    the_srt_output_file = f"{main_name}.srt"
    the_output_file = f"{main_name}_output.mp4"
    the_ass_file = f'{main_name}.ass'
    wrapped_ass_file = f'{main_name}_wrapped.ass'
    whisper_model = 'whisper_models/large-v3.pt'

    # 生成字幕
    transcribe_and_generate_srt(the_audio_file, the_srt_output_file, language='Chinese', whisper_model=whisper_model)

    # 将 SRT 字幕转换为 ASS 字幕
    srt_to_ass(the_srt_output_file, the_ass_file)

    # 将 ASS 字幕智能换行
    wrap_main(input_file=the_ass_file, output_file=wrapped_ass_file, max_len=12)

    # 生成视频
    generate_video(the_audio_file, the_output_file, wrapped_ass_file)

    # 删除字幕文件
    os.remove(the_srt_output_file)
    os.remove(the_ass_file)
    os.remove(wrapped_ass_file)
