# -*- encoding: utf-8 -*-
"""
@File: A03_translate_to_cn.py
@Modify Time: 2024/10/29 14:04       
@Author: Kevin-Chen
@Descriptions: 
"""
import requests
import time
import random


# 定义翻译函数
def translate_to_chinese(text, raw_language="en"):
    raw_language = raw_language.lower()
    if raw_language == 'english':
        raw_language = 'en'
    print(text.strip())
    # 有道翻译API地址
    if raw_language == "en":
        url = f'https://dict.youdao.com/jsonapi?q={text}'
    elif raw_language == "japanese":
        url = f'https://dict.youdao.com/jsonapi?le=jap&q={text}'
    else:
        raise ValueError("不支持的语言类型")
    response = requests.get(url)
    data = response.json()

    # 从返回结果中提取翻译内容
    if 'fanyi' in data and 'tran' in data['fanyi']:
        cn_data = data['fanyi']['tran']
    elif data['web_trans']['web-translation'][0]['trans'][0]['value']:
        cn_data = data['web_trans']['web-translation'][0]['trans'][0]['value']
    else:
        cn_data = ""
    print(cn_data)

    # 随机等待1-10秒, 避免请求过于频繁被封IP
    time.sleep(random.randint(1, 10))
    return cn_data


# 按行读取文件
def translate_file(file_path):
    cn_result = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            print(line.strip())
            cn_txt = translate_to_chinese(line)
            print(cn_txt)
            cn_result.append(cn_txt)
    return cn_result


# 按行写入文件
def write_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        for line in data:
            f.write(line)
            f.write('\n')


def translate_text_main(input_file, output_file):
    res_list = translate_file(input_file)
    write_file(output_file, res_list)


if __name__ == '__main__':
    # from A02_whisper_model import transcribe_audio, split_sentences, save_sentences_to_txt
    # the_en_file = "output_en.txt"  # 语言识别后的英文文件
    # the_cn_file = "output_cn.txt"  # 翻译后的中文文件
    #
    # the_audio_file = "gpu.mp3"
    # the_language_code = "en"
    #
    # # 识别语音
    # the_text = transcribe_audio(the_audio_file, the_language_code)
    # print(the_text)
    # # 分割文本为句子并保存
    # the_sentences = split_sentences(the_text)
    # save_sentences_to_txt(the_sentences, the_en_file)
    # # 翻译文本为中文
    # translate_text_main(the_en_file, the_cn_file)

    print(translate_to_chinese("君は負けず嫌 君がMy boy 夢を叶えて", "japanese"))
