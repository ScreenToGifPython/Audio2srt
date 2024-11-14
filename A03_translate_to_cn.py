# -*- encoding: utf-8 -*-
"""
@File: A03_translate_to_cn.py
@Modify Time: 2024/10/29 14:04       
@Author: Kevin-Chen
@Descriptions: 
"""
import requests
import random
import time
import re


def remove_symbols_and_spaces(input_string):
    # 使用正则表达式去除所有非字母数字字符，包括空格
    cleaned_string = re.sub(r'\W+', '', input_string)
    return cleaned_string


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
    cn_data = ""
    if 'fanyi' in data and 'tran' in data['fanyi']:
        cn_data = data['fanyi']['tran']
    elif 'web_trans' in data:
        for you_dao_data in data['web_trans']['web-translation']:
            if remove_symbols_and_spaces(you_dao_data['key'].lower()) == remove_symbols_and_spaces(text.strip().lower()):
                cn_data = you_dao_data['trans'][0]['value']
                break
    elif 'ec' in data and cn_data == "":
        cn_data = data['ec']['word'][0]['trs'][0]['tr'][0]['l']['i'][0]
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
            cn_txt = translate_to_chinese(line)
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
    pass
