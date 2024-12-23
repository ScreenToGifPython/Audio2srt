# -*- encoding: utf-8 -*-
"""
@File: test_3.py
@Modify Time: 2024/10/30 14:39       
@Author: Kevin-Chen
@Descriptions: 
"""
import srt
from A03_translate_to_cn import translate_to_chinese


def translate_srt(input_srt_file, output_srt_file, language_code):
    print(f"为了避免过于频繁的访问翻译API导致IP被封, 我强制减低了翻译的速度, 请耐心等待 ...")
    # 读取原始的 SRT 文件
    with open(input_srt_file, 'r', encoding='utf-8') as file:
        srt_content = file.read()

    # 解析 SRT 文件
    subtitles = list(srt.parse(srt_content))

    # 对每个字幕进行翻译，并合并原文和译文
    translated_subtitles = []
    for subtitle in subtitles:
        original_text = subtitle.content.strip()  # 获取原文
        translated_text = translate_to_chinese(original_text, language_code)  # 获取翻译后的文本

        # 合并原文和翻译后的文本为新的字幕内容
        subtitle.content = f"{original_text}\n{translated_text}"
        translated_subtitles.append(subtitle)

    # 生成新的 SRT 文件内容
    translated_srt_content = srt.compose(translated_subtitles)

    # 将新的字幕写入到文件
    with open(output_srt_file, 'w', encoding='utf-8') as output_file:
        output_file.write(translated_srt_content)


if __name__ == '__main__':
    pass
