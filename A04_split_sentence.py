# -*- encoding: utf-8 -*-
"""
@File: A04_split_sentence.py
@Modify Time: 2024/10/30 12:06       
@Author: Kevin-Chen
@Descriptions: 
"""
import re
import math
from itertools import combinations


def is_decimal_point(text, index):
    """
    判断给定文本中给定索引位置的字符是否为小数点。

    此函数通过检查索引位置的字符及其前后字符来确定该字符是否为小数点。
    小数点的定义是：它是一个点字符，且至少有一侧紧邻着一个数字字符。

    参数:
    text (str): 要检查的文本字符串。
    index (int): 要检查的字符在文本中的索引位置。

    返回:
    bool: 如果索引位置的字符是小数点，则返回True；否则返回False。
    """

    # 判断索引位置的字符是否为点字符
    if text[index] != '.':
        return False

    # 检查点字符是否位于两个数字字符之间
    if index > 0 and index < len(text) - 1:
        if text[index - 1].isdigit() and text[index + 1].isdigit():
            return True

    # 处理类似 "3." 的情况，即点字符左侧是数字，右侧没有字符
    if index > 0 and text[index - 1].isdigit():
        return True

    # 如果以上条件都不满足，则该点字符不是小数点
    return False


def split_line(line, max_length=50, min_length=3):
    line = line.strip()
    if len(line) <= max_length:
        return [line]
    else:
        # 寻找可以拆分的标点符号位置
        punctuation_marks = [',', ';', ':', '?', '!', '，', '；', '：', '？', '！']
        split_positions = []
        for i, char in enumerate(line):
            if char in punctuation_marks:
                if i != len(line) - 1 and i != 0:
                    split_positions.append(i)
            elif char == '.':
                if not is_decimal_point(line, i):
                    if i != len(line) - 1 and i != 0:
                        split_positions.append(i)
        if split_positions:
            # 尝试找到分割后各部分长度都不超过max_length的分割点
            # 优先选择使各部分长度最接近的分割方式
            best_splits = None
            min_length_diff = None
            for split_combination in generate_split_combinations(split_positions):
                parts = split_at_positions(line, split_combination)
                part_lengths = [len(part.strip()) for part in parts]
                if all(min_length <= l <= len(line) for l in part_lengths):
                    max_part_length = max(part_lengths)
                    min_part_length = min(part_lengths)
                    length_diff = max_part_length - min_part_length
                    if max(part_lengths) <= max_length:
                        if min_length_diff is None or length_diff < min_length_diff:
                            best_splits = split_combination
                            min_length_diff = length_diff
            if best_splits is not None:
                parts = split_at_positions(line, best_splits)
                result = []
                for part in parts:
                    # 递归地对每个部分进行处理
                    result.extend(split_line(part.strip(), max_length, min_length))
                return result
            else:
                # 无法通过标点符号分割满足要求，继续均匀拆分
                return split_long_segment(line, max_length, min_length)
        else:
            # 没有标点符号，均匀拆分
            return split_long_segment(line, max_length, min_length)


def generate_split_combinations(split_positions):
    # 生成所有可能的分割组合
    for r in range(1, len(split_positions) + 1):
        for comb in combinations(split_positions, r):
            yield list(comb)


def linear_partition(seq, k):
    n = len(seq)
    if k <= 0:
        return []
    if k >= n:
        return [[x] for x in seq]
    table = [[0] * (k + 1) for _ in range(n + 1)]
    solution = [[0] * (k + 1) for _ in range(n + 1)]

    prefix_sums = [0]
    for i in range(n):
        prefix_sums.append(prefix_sums[-1] + seq[i])

    for i in range(1, n + 1):
        table[i][1] = prefix_sums[i]
    for j in range(1, k + 1):
        table[1][j] = seq[0]

    for i in range(2, n + 1):
        for j in range(2, k + 1):
            min_cost = None
            for x in range(1, i):
                cost = max(table[x][j - 1], prefix_sums[i] - prefix_sums[x])
                if min_cost is None or cost < min_cost:
                    table[i][j] = cost
                    solution[i][j] = x
                    min_cost = cost

    def reconstruct_partition(s, n, k):
        if k == 1:
            return [s[:n]]
        else:
            result = reconstruct_partition(s, solution[n][k], k - 1)
            result.append(s[solution[n][k]:n])
            return result

    return reconstruct_partition(seq, n, k)


def split_long_segment(segment, max_length, min_length):
    words = segment.strip().split()
    total_length = sum(len(word) for word in words) + len(words) - 1  # 总字符数，包括空格
    num_lines = max(1, math.ceil(total_length / max_length))  # 需要的行数

    # 计算每个单词的长度，包括前面的空格（除了第一个单词）
    word_lengths = []
    for i, word in enumerate(words):
        if i == 0:
            word_lengths.append(len(word))
        else:
            word_lengths.append(len(word) + 1)  # 加上空格的长度

    # 使用线性划分算法
    partitions = linear_partition(word_lengths, num_lines)

    # 根据划分结果生成行文本
    lines = []
    index = 0
    for part in partitions:
        line_words = words[index:index + len(part)]
        line = ' '.join(line_words)
        lines.append(line)
        index += len(part)

    # 确保每行长度在限制范围内，如果不在，递归拆分
    final_result = []
    for line in lines:
        line_length = len(line)
        if line_length > max_length:
            # 递归拆分
            final_result.extend(split_long_segment(line, max_length, min_length))
        elif line_length < min_length:
            final_result.append(line)
        else:
            final_result.append(line)
    return final_result


def split_at_positions(line, positions):
    positions = sorted(positions)
    parts = []
    prev_pos = 0
    for pos in positions:
        parts.append(line[prev_pos:pos + 1])
        prev_pos = pos + 1
    parts.append(line[prev_pos:])
    return parts


def process_file(input_file, output_file, max_length=50, min_length=3):
    with open(input_file, 'r', encoding='utf-8') as fin, \
            open(output_file, 'w', encoding='utf-8') as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            new_lines = split_line(line, max_length, min_length)
            for new_line in new_lines:
                fout.write(new_line + '\n')


if __name__ == '__main__':
    process_file('output.txt', 'output_processed.txt', 50, 3)
