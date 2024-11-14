# -*- encoding: utf-8 -*-
"""
@File: A02_whisper_model.py
@Modify Time: 2024/10/29 13:13       
@Author: Kevin-Chen
@Descriptions: 
"""
import os
import re
import sys
import whisper

# 检查是否是打包后的可执行文件
if getattr(sys, 'frozen', False):
    # 获取当前文件目录（针对 Nuitka 的打包环境）
    current_dir = os.path.dirname(sys.executable)
else:
    # 开发环境中，使用当前文件路径
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)


def transcribe_audio(audio_file, language_code, model_path="small.pt"):
    model = whisper.load_model(model_path)

    # 转录音频
    result = model.transcribe(audio_file, language=language_code)
    text = result["text"]
    return text


def split_sentences(text):
    # pattern = re.compile(r'\.(?!\d)|(?<!\d)\.|[!?:]')
    # # 在匹配到的标点符号后添加换行符
    # text = pattern.sub(lambda x: x.group() + '\n', text)
    # # 按换行符拆分，并移除多余的空白和空行
    # sentences = [sentence.strip() for sentence in text.split('\n') if sentence.strip()]
    # return sentences

    # 匹配单个句号作为句末标点，但不匹配 ".."、"..." 和小数点（前后都是数字）
    pattern = re.compile(r'(?<!\.\.)(?<!\d)\.(?!\d)(?!\.)|[!?]')

    # 在匹配到的标点符号后添加换行符
    text = pattern.sub(lambda x: x.group() + '\n', text)

    # 按换行符拆分，并移除多余的空白和空行
    sentences = [sentence.strip() for sentence in text.split('\n') if sentence.strip()]

    # 合并单词少于2个的句子
    merged_sentences = []
    temp_sentence = ""

    for sentence in sentences:
        word_count = len(sentence.split())

        if word_count < 2:  # 如果句子少于两个单词
            if temp_sentence:  # 如果之前有句子缓存，合并到缓存句子
                temp_sentence += " " + sentence
            else:  # 否则开始新的缓存句子
                temp_sentence = sentence
        else:
            if temp_sentence:  # 如果有缓存句子，合并后加入结果
                merged_sentences.append(temp_sentence + " " + sentence)
                temp_sentence = ""
            else:  # 否则直接加入结果
                merged_sentences.append(sentence)

    # 如果最后还有未合并的句子，添加到结果
    if temp_sentence:
        merged_sentences.append(temp_sentence)

    return merged_sentences


def save_sentences_to_txt(sentences, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        for sentence in sentences:
            f.write(sentence.strip() + '\n')  # 每个句子写入一行


if __name__ == '__main__':
    pass
