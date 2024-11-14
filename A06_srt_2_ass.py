import pysubs2
from moviepy.editor import VideoFileClip


def convert_srt_to_ass_with_line_split(input_srt_file, output_ass_file, video_file, eng_fontsize_ratio=0.03,
                                       cn_fontsize_ratio=0.05, eng_font="Arial", cn_font="STHeiti"):
    """
    将 SRT 字幕文件转换为 ASS 字幕文件，并根据视频高度动态调整字体大小，同时将中英文双行字幕拆分为独立的行。

    :param input_srt_file: 输入的 SRT 字幕文件路径
    :param output_ass_file: 输出的 ASS 字幕文件路径
    :param video_file: 视频文件路径，用于动态计算字体大小
    :param eng_fontsize_ratio: 英文字体大小与视频高度的比例
    :param cn_fontsize_ratio: 中文字体大小与视频高度的比例
    :param eng_font: 英文字体名称
    :param cn_font: 中文字体名称
    """
    # 加载视频文件
    video = VideoFileClip(video_file)

    # 动态计算字体大小，基于视频的高度
    video_height = video.h  # 获取视频的高度
    video_weight = video.w # 获取视频的宽度
    print(f"视频高度: {video_height}, 视频宽度: {video_weight}")
    eng_fontsize = int(video_height * eng_fontsize_ratio)  # 英文字体大小设置为视频高度的百分比
    cn_fontsize = int(video_height * cn_fontsize_ratio)  # 中文字体大小设置为视频高度的百分比
    print("英文字体大小:", eng_fontsize)
    print("中文字体大小:", cn_fontsize)

    # 读取 SRT 文件
    subs = pysubs2.load(input_srt_file, encoding="utf-8")

    # 定义英文字幕样式
    eng_style = pysubs2.SSAStyle()
    eng_style.fontname = eng_font
    eng_style.fontsize = eng_fontsize
    eng_style.primarycolor = "&H00FFFFFF"  # 白色字体，不透明
    eng_style.outlinecolor = "&H00000000"  # 黑色描边，不透明
    eng_style.bold = False
    eng_style.outline = 1
    eng_style.alignment = 2  # 居中下方对齐

    # 定义中文字幕样式
    cn_style = pysubs2.SSAStyle()
    cn_style.fontname = cn_font
    cn_style.fontsize = cn_fontsize
    cn_style.primarycolor = "&H00FFFFFF"  # 白色字体，不透明
    cn_style.outlinecolor = "&H00000000"  # 黑色描边，不透明
    cn_style.bold = False
    cn_style.outline = 0.2
    cn_style.alignment = 2  # 居中下方对齐

    # 添加样式到字幕文件
    subs.styles["English"] = eng_style
    subs.styles["Chinese"] = cn_style

    # 遍历字幕，将中英文分离并应用不同的样式
    new_events = []
    for line in subs:
        # 通过换行符区分中英文
        if "\n" in line.text:
            eng_text, cn_text = line.text.split("\n", 1)  # 只分割一次，避免意外的多行处理
        elif "\\N" in line.text:
            eng_text, cn_text = line.text.split("\\N", 1)  # 只分割一次，避免意外的多行处理
        else:
            eng_text, cn_text = line.text, ""
        # 创建英文字幕行
        if eng_text.strip():  # 确保英文字幕非空
            eng_line = pysubs2.SSAEvent(start=line.start, end=line.end, text=eng_text.strip(), style="English")
            new_events.append(eng_line)

        # 创建中文字幕行
        if cn_text.strip():  # 确保中文字幕非空
            cn_line = pysubs2.SSAEvent(start=line.start, end=line.end, text=cn_text.strip(), style="Chinese")
            new_events.append(cn_line)

    # 更新字幕的事件列表
    subs.events = new_events
    # 保存为 ASS 文件
    subs.save(output_ass_file)
    print(f"已成功生成 ASS 文件: {output_ass_file}")


if __name__ == '__main__':
    pass
