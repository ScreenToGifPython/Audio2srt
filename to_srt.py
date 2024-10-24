from aeneas.tools.execute_task import main

if __name__ == "__main__":
    # 请将以下路径替换为实际文件路径
    txt_path = "input.txt"
    audio_path = "x4_yeting.mp3"
    srt_path = "output_subtitles.srt"

    main(txt_path, audio_path, srt_path)
