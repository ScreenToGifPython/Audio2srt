import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit
from PyQt5.QtCore import QTimer
from start_gradio import start_gradio, close_gradio  # 导入 start_gradio 和 close_gradio 函数
import threading
import os
import io


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("音频转文字 & 字幕生成器")
        self.setGeometry(100, 100, 600, 400)

        # Start 按钮
        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_server)

        # Close 按钮
        self.close_button = QPushButton("Close", self)
        self.close_button.clicked.connect(self.close_server)

        # 日志显示框
        self.log_area = QTextEdit(self)
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("background-color: black; color: white;")

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.close_button)
        layout.addWidget(self.log_area)
        self.setLayout(layout)

        # 创建一个内存文件来捕获 Gradio 的输出
        self.output_stream = io.StringIO()

        # 使用 QTimer 来定期更新日志区域
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_log)

        self.gradio_thread = None  # 用于启动 Gradio 的线程

    def start_server(self):
        try:
            # 启动 Gradio 服务器，并捕获输出到 GUI
            self.log_area.append("Starting Gradio server...")
            self.timer.start(1000)  # 每秒更新日志区域

            # 在一个单独的线程中启动 Gradio，以免阻塞 GUI
            self.gradio_thread = threading.Thread(target=self.run_gradio)
            self.gradio_thread.setDaemon(True)  # 使线程成为守护线程
            self.gradio_thread.start()
        except Exception as e:
            # 捕获启动时的异常并显示在日志中
            self.log_area.append(f"Error starting Gradio server: {str(e)}")

    def run_gradio(self):
        try:
            # 将 Gradio 的输出重定向到内存文件
            sys.stdout = self.output_stream
            sys.stderr = self.output_stream
            start_gradio()  # 启动 Gradio 服务器
        except Exception as e:
            self.log_area.append(f"Gradio server error: {str(e)}")

    def close_server(self):
        try:
            # 关闭 Gradio 服务器
            self.log_area.append("Closing Gradio server...")
            close_gradio()  # 调用关闭函数
            self.timer.stop()  # 停止更新日志
            self.log_area.append("Gradio server closed")
        except Exception as e:
            # 捕获关闭时的异常并显示在日志中
            self.log_area.append(f"Error closing Gradio server: {str(e)}")

    def update_log(self):
        # 更新日志区域，将内存文件中的内容输出到日志显示框
        content = self.output_stream.getvalue()
        if content:
            self.log_area.append(content)
            # 清空输出流，避免重复显示
            self.output_stream.truncate(0)
            self.output_stream.seek(0)

    def closeEvent(self, event):
        # 捕获窗口关闭事件，确保 Gradio 服务器关闭
        self.log_area.append("Application closing...")
        self.close_server()  # 确保在关闭窗口时正确关闭 Gradio 服务器
        os._exit(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
