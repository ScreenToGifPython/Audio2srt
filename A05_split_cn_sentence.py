# -*- encoding: utf-8 -*-
"""
@File: A05_split_cn_sentence.py
@Modify Time: 2024/10/30 13:15       
@Author: Kevin-Chen
@Descriptions: 
"""
import jieba
import re


def read_file_lines(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.readlines()


def write_file_lines(filename, lines):
    with open(filename, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line.strip() + '\n')


def get_split_indices(english_line, processed_lines):
    indices = []
    pos = 0
    for processed_line in processed_lines:
        length = len(processed_line.replace('\n', '').replace(' ', ''))
        pos += length
        indices.append(pos)
    return indices[:-1]  # 最后一个位置不需要


def split_chinese_line(chinese_line, split_indices_english, english_line):
    # 将中文行进行分词
    words = list(jieba.cut(chinese_line.strip()))
    # 将中文分词后的字符位置映射出来
    chinese_chars = ''.join(words)
    total_chinese_chars = len(chinese_chars)
    # 如果中文句子为空，返回空列表
    if total_chinese_chars == 0:
        return []

    # 将英文行拼接并去除空格，获取总英文字符数
    english_chars = english_line.replace(' ', '').replace('\n', '')
    total_english_chars = len(english_chars)

    # 如果英文句子为空，直接返回中文分词结果
    if total_english_chars == 0:
        return [''.join(words)]

    # 计算每个英文拆分位置在总英文字符数中的比例
    ratios = [index / total_english_chars for index in split_indices_english]

    # 根据比例计算中文拆分位置
    split_positions = [int(r * total_chinese_chars) for r in ratios]

    # 根据拆分位置，在不拆分词语的情况下，调整到最近的词边界
    split_indices_chinese = []
    char_count = 0
    word_end_positions = []
    for word in words:
        char_count += len(word)
        word_end_positions.append(char_count)

    for pos in split_positions:
        # 找到不小于 pos 的最近的词结束位置
        for word_pos in word_end_positions:
            if word_pos >= pos:
                split_indices_chinese.append(word_pos)
                break
        else:
            split_indices_chinese.append(total_chinese_chars)

    # 根据调整后的拆分索引，拆分中文句子
    splits = []
    prev_index = 0
    last_index = 0  # 记录实际的拆分次数
    for index in split_indices_chinese:
        if index <= prev_index:
            index = prev_index + 1  # 确保至少拆分一个字符
        segment = ''.join(words)[prev_index:index]
        splits.append(segment)
        prev_index = index
        last_index += 1

    # 添加最后一段
    segment = ''.join(words)[prev_index:]
    if segment:
        splits.append(segment)
        last_index += 1

    # 如果拆分后的中文行数少于英文行数，尝试均匀地增加中文拆分
    while len(splits) < len(split_indices_english) + 1:
        # 找到最长的一行进行再次拆分
        max_length = max(len(s) for s in splits)
        for i, s in enumerate(splits):
            if len(s) == max_length:
                # 使用 jieba 对该行进行再次分词
                sub_words = list(jieba.cut(s))
                if len(sub_words) >= 2:
                    # 将该行拆分为两行
                    mid = len(sub_words) // 2
                    splits[i:i + 1] = [''.join(sub_words[:mid]), ''.join(sub_words[mid:])]
                    break
                else:
                    # 如果无法再拆分，跳过
                    continue
        else:
            # 无法再拆分，退出循环
            break

    # 如果拆分后的中文行数多于英文行数，合并最短的两行
    while len(splits) > len(split_indices_english) + 1:
        # 找到最短的两行
        lengths = [(len(s), i) for i, s in enumerate(splits)]
        lengths.sort()
        i1 = lengths[0][1]
        i2 = lengths[1][1]
        # 合并这两行
        combined = splits[i1] + splits[i2]
        if i1 < i2:
            splits[i1:i2 + 1] = [combined]
        else:
            splits[i2:i1 + 1] = [combined]

    return splits


def process_files(english_original_file, english_processed_file, chinese_original_file, chinese_processed_file):
    english_lines = read_file_lines(english_original_file)
    processed_english_lines = read_file_lines(english_processed_file)
    chinese_lines = read_file_lines(chinese_original_file)

    output_chinese_lines = []

    eng_line_index = 0
    processed_index = 0
    total_eng_lines = len(english_lines)

    while eng_line_index < total_eng_lines:
        english_line = english_lines[eng_line_index].strip()
        chinese_line = chinese_lines[eng_line_index].strip()
        processed_lines = []

        # 收集属于同一原始英文行的所有处理后的英文行
        combined_length = 0
        original_length = len(english_line.replace(' ', '').replace('\n', ''))
        while processed_index < len(processed_english_lines):
            processed_line = processed_english_lines[processed_index].strip()
            processed_line_length = len(processed_line.replace(' ', '').replace('\n', ''))
            processed_lines.append(processed_line)
            combined_length += processed_line_length
            processed_index += 1
            if combined_length >= original_length:
                break

        # 获取英文拆分位置
        split_indices = get_split_indices(english_line.replace(' ', '').replace('\n', ''), processed_lines)

        # 拆分中文行
        chinese_splits = split_chinese_line(chinese_line, split_indices,
                                            english_line.replace(' ', '').replace('\n', ''))

        # 检查拆分后的中文行数是否与英文行数一致
        expected_lines = len(processed_lines)
        actual_lines = len(chinese_splits)

        if actual_lines < expected_lines:
            # 尝试均匀地增加中文拆分
            while len(chinese_splits) < expected_lines:
                # 找到最长的一行进行再次拆分
                max_length = max(len(s) for s in chinese_splits)
                for i, s in enumerate(chinese_splits):
                    if len(s) == max_length and len(s) >= 2:
                        # 使用 jieba 对该行进行再次分词
                        sub_words = list(jieba.cut(s))
                        if len(sub_words) >= 2:
                            # 将该行拆分为两行
                            mid = len(sub_words) // 2
                            chinese_splits[i:i + 1] = [''.join(sub_words[:mid]), ''.join(sub_words[mid:])]
                            break
                else:
                    # 无法再拆分，退出循环
                    break
        elif actual_lines > expected_lines:
            # 合并最短的两行
            while len(chinese_splits) > expected_lines:
                # 找到最短的两行
                lengths = [(len(s), i) for i, s in enumerate(chinese_splits)]
                lengths.sort()
                i1 = lengths[0][1]
                i2 = lengths[1][1]
                # 合并这两行
                combined = chinese_splits[i1] + chinese_splits[i2]
                if i1 < i2:
                    chinese_splits[i1:i2 + 1] = [combined]
                else:
                    chinese_splits[i2:i1 + 1] = [combined]

        # 确保每一行至少有一个字符，且没有空行
        chinese_splits = [line if line else ' ' for line in chinese_splits]

        # 将拆分后的中文行添加到输出列表
        output_chinese_lines.extend(chinese_splits)

        eng_line_index += 1

    # 写入处理后的中文文件
    write_file_lines(chinese_processed_file, output_chinese_lines)


if __name__ == '__main__':
    process_files('output.txt', 'output_processed.txt', 'output_cn.txt', 'output_cn_processed.txt')
