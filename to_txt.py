# -*- encoding: utf-8 -*-
"""
@File: test.py
@Modify Time: 2024/10/20 06:25       
@Author: Kevin-Chen
@Descriptions: 
"""
import whisper


def to_txt(audio_path, output_path):
    # 加载模型
    model = whisper.load_model("small.pt")

    # 处理语音文件并输出结果
    result = model.transcribe(audio_path)

    # 将结果保存为文本文件
    text = result["text"]
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(text)

    print(f"文本已保存至 {output_path}")


if __name__ == '__main__':
    the_audio_path = "/Users/chenjunming/Downloads/aeneas-1.7.3.0/x4_yeting.mp3"
    the_output_path = "/Users/chenjunming/Downloads/aeneas-1.7.3.0/x4_yeting_words.txt"

    to_txt(the_audio_path, the_output_path)

