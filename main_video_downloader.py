# -*- encoding: utf-8 -*-
"""
@File: main_video_downloader.py
@Modify Time: 2024/11/15 15:09       
@Author: Kevin-Chen
@Descriptions: 
"""
import traceback
import yt_dlp
import gradio as gr
import os
import sys
import subprocess


def get_ffmpeg_path():
    # 获取可执行文件所在目录
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后的可执行文件
        base_path = sys._MEIPASS
    else:
        # 未打包，正常运行
        base_path = os.path.dirname(os.path.abspath(__file__))

    # 构建 ffmpeg 的完整路径
    ffmpeg_exe = 'My_ffmpeg'
    ffmpeg_path = os.path.join(base_path, 'ffmpeg_bin', ffmpeg_exe)

    # 确保 ffmpeg 可执行文件有执行权限
    os.chmod(ffmpeg_path, 0o755)
    print(f"ffmpeg 可执行文件路径: {ffmpeg_path}")
    return ffmpeg_path


def parse_speed_limit(speed_limit_str):
    units = {'K': 1024, 'M': 1024 * 1024}
    if speed_limit_str and speed_limit_str != '不限制':
        if speed_limit_str[-1].upper() in units:
            return int(float(speed_limit_str[:-1]) * units[speed_limit_str[-1].upper()])
        else:
            return int(speed_limit_str)
    else:
        return None


def get_video_info(url, cookies_file=None):
    ydl_opts = {}
    if cookies_file is not None:
        ydl_opts['cookiefile'] = cookies_file.name
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return info


# 根据提供的URL更新视频选择界面
def update_video_selection(url, cookies_file):
    """
    根据提供的URL更新视频选择界面。

    该函数首先获取视频信息，然后根据信息类型（播放列表或单个视频）更新用户界面。
    对于播放列表，它将生成视频标题列表供用户选择，并隐藏格式选择界面。
    对于单个视频，它将直接更新格式选择界面，提供不同格式的视频供用户选择。

    参数:
    url - 视频或播放列表的URL。
    cookies_file - 包含用户认证信息的cookies文件路径。

    返回值:
    更新的界面组件状态和获取的视频信息。
    """
    # 获取视频信息
    info = get_video_info(url, cookies_file)

    # 判断获取的信息类型是播放列表还是单个视频
    if info.get('_type') == 'playlist':
        # 对于播放列表，生成视频标题列表供用户选择
        video_titles = [entry.get('title', f"视频 {i + 1}") for i, entry in enumerate(info['entries'])]
        # 更新界面，显示视频标题选择界面，隐藏格式选择界面，并返回播放列表信息
        return gr.update(choices=video_titles, visible=True), gr.update(visible=False), info
    else:
        # 对于单个视频，直接更新格式列表
        format_list, format_options, _ = extract_formats(info)
        # 更新界面，隐藏视频标题选择界面，显示格式选择界面，并返回视频信息
        return gr.update(visible=False), gr.update(choices=format_options, visible=True), info


def extract_formats(video_info):
    format_list = []
    format_options = []
    for f in video_info.get('formats', []):
        format_id = f['format_id']
        ext = f['ext']
        resolution = f.get('resolution') or f"{f.get('height', 'NA')}p"
        note = f.get('format_note', '')
        filesize = f.get('filesize', 'NA')
        has_audio = '有' if f.get('has_audio') else '无'
        # 包含 has_audio 信息，以便后续使用
        format_desc = f"ID: {format_id}, 扩展名: {ext}, 分辨率: {resolution}, 注释: {note}"
        format_list.append([format_id, ext, resolution, note, filesize, has_audio])
        format_options.append(format_desc)
    return format_list, format_options, video_info


def update_format_dropdown(selected_video_title, info):
    if info.get('_type') == 'playlist':
        # 从播放列表中找到对应的视频
        video_info = None
        for entry in info['entries']:
            if entry.get('title') == selected_video_title:
                video_info = entry
                break
        if video_info is None:
            return gr.update(choices=[]), [], info
    else:
        video_info = info

    format_list, format_options, _ = extract_formats(video_info)
    return gr.update(choices=format_options, visible=True), format_list, video_info


def toggle_subtitle_options(download_subtitles):
    if download_subtitles:
        return gr.update(visible=True), gr.update(visible=True)
    else:
        return gr.update(visible=False), gr.update(visible=False)


def download_video(url, selected_format_desc, format_list_state, download_speed_limit, download_folder, filename,
                   download_subtitles, subtitle_folder, subtitle_filename, retries, cookies_file, video_info,
                   mirror_video):
    ydl_opts = {
        'retries': int(retries),
        'outtmpl': {'default': os.path.join(download_folder, filename + '.%(ext)s') if filename else os.path.join(
            download_folder, '%(title)s.%(ext)s')},
        'merge_output_format': 'mp4',
        'ffmpeg_location': get_ffmpeg_path(),  # 指定 ffmpeg 可执行文件路径
    }
    ratelimit = parse_speed_limit(download_speed_limit)
    if ratelimit:
        ydl_opts['ratelimit'] = ratelimit
    if cookies_file is not None:
        ydl_opts['cookiefile'] = cookies_file.name
    if download_subtitles:
        ydl_opts['writesubtitles'] = True
        ydl_opts['subtitleslangs'] = ['all']
        ydl_opts['subtitlesformat'] = 'best'
        ydl_opts['outtmpl']['subtitle'] = os.path.join(subtitle_folder,
                                                       subtitle_filename + '.%(ext)s') if subtitle_filename else os.path.join(
            subtitle_folder, '%(title)s.%(ext)s')

    selected_format_id = None
    selected_has_audio = False
    for f in format_list_state:
        format_id = f[0]
        ext = f[1]
        resolution = f[2]
        note = f[3]
        filesize = f[4]
        has_audio = f[5] == '有'
        format_desc = f"ID: {format_id}, 扩展名: {ext}, 分辨率: {resolution}, 注释: {note}"
        if format_desc == selected_format_desc:
            selected_format_id = format_id
            selected_has_audio = has_audio
            break
    if selected_format_id:
        if not selected_has_audio:
            # 如果所选格式没有音频，自动合并最佳音频
            ydl_opts['format'] = f"{selected_format_id}+bestaudio/best"
        else:
            ydl_opts['format'] = selected_format_id
    else:
        ydl_opts['format'] = 'bestvideo+bestaudio/best'

    download_url = video_info.get('webpage_url', url)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(download_url, download=True)

        # 下载完成后，检查是否需要左右反转视频
        if mirror_video:
            # 获取下载的视频文件路径
            if 'requested_downloads' in info_dict:
                # 获取合并后的视频文件路径
                video_file = ydl.prepare_filename(info_dict)
            else:
                video_file = info_dict.get('_filename')

            if not video_file or not os.path.exists(video_file):
                return "无法找到下载的视频文件。"

            # 使用 ffmpeg 进行左右反转，同时保留音频
            temp_file = video_file + '.temp.mp4'
            try:
                ffmpeg_path = get_ffmpeg_path()  # 获取 ffmpeg 可执行文件路径

                cmd = [
                    ffmpeg_path,
                    '-y',  # 覆盖输出文件
                    '-i', video_file,
                    '-vf', 'hflip',
                    '-c:a', 'copy',
                    temp_file
                ]

                # 运行命令
                subprocess.run(cmd, check=True)

                # 替换原始文件
                os.replace(temp_file, video_file)
            except Exception as e:
                print(traceback.format_exc())
                return f"视频反转失败：{str(e)}"

        return "下载完成。"
    except Exception as e:
        return f"发生错误：{str(e)}"


def start_gradio(in_browser=True):
    """
    启动Gradio界面的函数，用于构建和启动一个视频下载器的用户界面。
    参数:
        in_browser (bool): 是否在浏览器中自动打开界面，默认为True。
    """
    # 创建一个Gradio Blocks对象，用于构建自定义的UI布局
    with gr.Blocks() as demo:
        # 显示项目介绍和使用说明的Markdown文本
        gr.Markdown("## 视频下载器 \n"
                    "支持: YouTube, TikTok, Youku, Bilibili 等网站。  \n"
                    "需要权限的视频请使用Cookies文件进行登录操作, 并确保你有此权限。  \n"
                    "使用方法: 1.输入视频网站的URL   2.点击[检查视频信息]   3.选择视频格式   4.点击[下载视频]  \n")

        # 创建一个列布局，用于组织输入和控制元素
        with gr.Column():
            # 用于输入视频或播放列表URL的文本框
            url_input = gr.Textbox(label="视频或播放列表 URL")
            # 用于上传Cookies文件的文件输入框，以支持需要登录的视频下载
            cookies_input = gr.File(label="Cookies 文件（可选）", file_types=['file'])
            # 检查视频信息的按钮
            check_info_button = gr.Button("检查视频信息")
            # 下拉菜单，用于选择视频（当输入的是播放列表时）
            video_dropdown = gr.Dropdown(label="选择视频（针对播放列表）", visible=False)
            # 用于选择所需视频格式的下拉菜单
            format_dropdown = gr.Dropdown(label="选择所需的格式")
            # 用于存储格式列表的状态
            format_list_state = gr.State([])
            # 用于存储视频信息的状态
            video_info_state = gr.State(None)

            # 下载速度限制的选项
            download_speed_limit_options = ['不限制', '500K', '1M', '2M', '5M']
            # 用于选择下载速度限制的下拉菜单
            download_speed_limit = gr.Dropdown(label="下载速度限制", choices=download_speed_limit_options,
                                               value='不限制')

            # 用于输入下载文件夹路径的文本框，默认为当前文件夹
            download_folder = gr.Textbox(label="下载文件夹路径（默认当前文件夹）", value=os.getcwd())

            # 用于输入自定义视频文件名的文本框
            filename_input = gr.Textbox(label="自定义视频文件名（可选，不包括扩展名）")

            # 添加左右反转视频的选项
            mirror_video = gr.Checkbox(label="左右反转视频")

            # 用于选择是否下载字幕的复选框
            download_subtitles = gr.Checkbox(label="下载字幕（如果有）")
            # 当选择下载字幕时显示的字幕下载文件夹路径
            subtitle_folder = gr.Textbox(label="字幕下载文件夹", value=os.getcwd(), visible=False)
            # 当选择下载字幕时显示的字幕文件名
            subtitle_filename = gr.Textbox(label="字幕文件名（可选，不包括扩展名）", visible=False)

            # 下载失败时的重试次数选项
            retries_options = ['0', '1', '3', '5', '10']
            # 用于选择下载失败时的重试次数的下拉菜单
            retries_input = gr.Dropdown(label="下载失败时的重试次数", choices=retries_options, value='0')

            # 下载视频的按钮
            download_button = gr.Button("下载视频")
            # 用于显示输出信息的文本框
            output_text = gr.Textbox(label="输出信息")

        # 点击“检查视频信息”按钮时触发的动作
        check_info_button.click(
            fn=update_video_selection,
            inputs=[url_input, cookies_input],
            outputs=[video_dropdown, format_dropdown, video_info_state]
        )

        # 当选择了视频后，更新格式列表
        video_dropdown.change(
            fn=update_format_dropdown,
            inputs=[video_dropdown, video_info_state],
            outputs=[format_dropdown, format_list_state, video_info_state]
        )

        # 当选择下载字幕时，显示字幕相关选项
        download_subtitles.change(
            fn=toggle_subtitle_options,
            inputs=download_subtitles,
            outputs=[subtitle_folder, subtitle_filename]
        )

        # 点击“下载视频”按钮时触发的动作
        download_button.click(
            fn=download_video,
            inputs=[
                url_input, format_dropdown, format_list_state, download_speed_limit, download_folder, filename_input,
                download_subtitles, subtitle_folder, subtitle_filename, retries_input, cookies_input, video_info_state,
                mirror_video
            ],
            outputs=output_text
        )

    # 启动Gradio界面
    demo.launch(inbrowser=in_browser)


if __name__ == '__main__':
    start_gradio()
