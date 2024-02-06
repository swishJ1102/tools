import os
import shutil
import sys
from configparser import ConfigParser

from PyQt5.QtCore import QDateTime, Qt, QTimer, QCoreApplication
from PyQt5.QtWidgets import QApplication, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QProgressBar, \
    QPushButton, QTableWidget, QVBoxLayout, QWidget, QFileDialog, QMessageBox, QTableWidgetItem

from datetime import datetime


class EventHandler:
    def __init__(self, parent):
        self.config = None
        self.current_value = None
        self.current_row = None
        self.result_message = None
        self.timer_for_list = None
        self.pending_files_iterator = None
        self.pending_files = None
        self.folder_after = None
        self.parent = parent
        self.folder_before = None
        self.detail_table_timer = QTimer(self.parent)

    def button_before_click(self):
        self.folder_before = QFileDialog.getExistingDirectory(self.parent, "选择源目录")
        self.parent.input_field_before.setText(self.folder_before)
        self.update_pending_files_list()

    def update_pending_files_list(self):
        try:
            self.parent.list_widget.clear()
            if not os.listdir(self.folder_before):
                QMessageBox.critical(self.parent, '错误', '源文件夹中没有文件。')
                self.parent.input_field_before.clear()
            else:
                self.pending_files = {filename: "待复制" for filename in os.listdir(self.folder_before) if
                                      os.path.isfile(os.path.join(self.folder_before, filename))}
                self.update_detail_list()
        except Exception as e:
            print(f"Error during update_pending_files_list: {e}")

    def update_detail_list(self):
        try:
            self.parent.list_widget.clear()

            self.pending_files_iterator = iter(self.pending_files.items())
            self.parent.timer_for_list = QTimer(self.parent)
            self.parent.timer_for_list.timeout.connect(self.render_next_row)
            self.parent.timer_for_list.start(5)  # 设置间隔时间，单位为毫秒
        except Exception as e:
            print(f"Error during update_detail_list: {e}")

    def render_next_row(self):
        try:
            filename, status = next(self.pending_files_iterator)
            self.parent.list_widget.addItem(filename)
            self.parent.list_widget.scrollToBottom()
        except StopIteration:
            self.parent.timer_for_list.stop()

    def button_after_click(self):
        try:
            self.folder_after = QFileDialog.getExistingDirectory(self.parent, "选择目标目录")
            self.parent.input_field_after.setText(self.folder_after)

            if self.folder_after == self.folder_before:
                QMessageBox.warning(self.parent, '警告', '目标文件夹不能与原始文件夹相同。')
                self.parent.input_field_after.clear()
        except Exception as e:
            print(f"Error during folder selection: {e}")

    def confirm_and_execute(self):
        confirm = QMessageBox.question(self.parent, '确认', '确认目标文件夹，此操作会覆盖目标文件夹下的所有文件。',
                                       QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.Yes:
            self.execute_copy()

    def execute_copy(self):
        try:
            if self.folder_before and self.folder_after:
                success_count = 0
                failure_count = 0

                for filename, status in self.pending_files.items():
                    path_before = os.path.join(self.folder_before, filename)
                    folder_after = os.path.join(self.folder_after, os.path.splitext(filename)[0])
                    path_after = os.path.join(folder_after, filename)

                    try:
                        os.makedirs(folder_after, exist_ok=True)
                        shutil.copy2(path_before, path_after, follow_symlinks=True)
                        self.pending_files[filename] = "成功"
                        # self.update_detail_table()
                        success_count += 1
                    except Exception as e:
                        self.pending_files[filename] = f"失败: {str(e)}"
                        # self.update_detail_table()
                        failure_count += 1
                total_files = len(self.pending_files)
                self.result_message = f'文件复制完成！成功：{success_count}，失败：{failure_count}'
                self.parent.table_widget.setRowCount(0)
                self.update_detail_table()
        except Exception as e:
            print(f"Error during execute_copy: {e}")

    def update_detail_table(self):
        self.current_row = 0  # 添加一个实例变量来跟踪当前行
        self.parent.table_widget.clearContents()  # 清除表格内容
        self.pending_files_iterator = iter(self.pending_files.items())
        self.detail_table_timer.timeout.connect(self.render_next_table)
        self.detail_table_timer.start(5)  # 设置间隔时间，单位为毫秒

    def render_next_table(self):
        try:
            filename, status = next(self.pending_files_iterator)
            self.parent.table_widget.insertRow(self.current_row)
            self.parent.table_widget.setItem(self.current_row, 0, QTableWidgetItem(filename))  # 文件名
            self.parent.table_widget.setItem(self.current_row, 1, QTableWidgetItem(status))  # 状态
            # 将滚动条滚动到最底部
            self.parent.table_widget.scrollToBottom()
            self.parent.table_widget.resizeColumnsToContents()
            self.current_row += 1
            self.current_value = self.current_row / self.parent.list_widget.count() * 100
            self.parent.progress_bar.setValue(int(self.current_value))
            if self.current_value == 100:
                QMessageBox.information(self.parent, '完成', self.result_message)
        except StopIteration:
            self.detail_table_timer.stop()  # 所有行都已经渲染完成，停止 QTimer

    def save_records(self):
        try:
            save_dir = QFileDialog.getExistingDirectory(self.parent, "选择保存目录")
            if save_dir:
                save_path = os.path.join(save_dir, f"文件复制记录{datetime.now().strftime('%Y%m%d%H%M%S')}_records.txt")
                with open(save_path, "w") as file:
                    for filename, status in self.pending_files.items():
                        file.write(f"{filename}     {status}\n")

                QMessageBox.information(self.parent, '保存成功', f'记录已保存至：{save_path}')
        except Exception as e:
            print(f"Error during save_records: {e}")

    def get_program_directory(self):
        # return os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(os.path.abspath(sys.argv[0]))

    def get_config_file_path(self):
        return os.path.join(self.get_program_directory(), ".tool_config.ini")

    def save_file_paths(self):
        if self.folder_before and self.folder_after:
            config = ConfigParser()
            config['Paths'] = {'input_file_path': self.folder_before, 'output_file_path': self.folder_after}
            with open(self.get_config_file_path(), 'w') as configfile:
                config.write(configfile)

    def load_file_paths(self):
        self.config = ConfigParser()
        self.config.read(self.get_config_file_path())
        return self.config['Paths'] if 'Paths' in self.config else {}

    def update_from_config_paths(self):
        config_paths = self.load_file_paths()
        if config_paths:
            self.parent.input_field_before.setText(config_paths.get('input_file_path', ''))
            self.parent.input_field_after.setText(config_paths.get('output_file_path', ''))

    def app_exit(self):
        # self.save_file_paths()
        self.parent.close()


class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.current_datetime = None
        self.timer = None
        self.main_layout = None
        self.progress_bar = None
        self.tips_label = None
        self.tips_layout = None
        self.tips_group = None
        self.exit_button = None
        self.save_button = None
        self.exec_button = None
        self.button_layout = None
        self.button_group = None
        self.bottom_layout = None
        self.bottom_right_layout = None
        self.table_widget = None
        self.bottom_right_group = None
        self.list_widget = None
        self.bottom_left_layout = None
        self.bottom_left_group = None
        self.button_after = None
        self.input_field_after = None
        self.label_after = None
        self.button_before = None
        self.label_before = None
        self.top_layout = None
        self.top_layout_2 = None
        self.top_layout_1 = None
        self.top_group = None
        self.input_field_before = None
        self.event_handler = EventHandler(self)
        self.init_ui()

    def init_ui(self):
        self.top_group = QGroupBox("文件夹选择")
        self.top_layout_1 = QHBoxLayout()
        self.top_layout_2 = QHBoxLayout()
        self.top_layout = QVBoxLayout()
        self.label_before = QLabel('原始文件夹')
        self.input_field_before = QLineEdit()
        self.input_field_before.setReadOnly(True)
        self.button_before = QPushButton('选择文件夹')
        self.label_after = QLabel('目标文件夹')
        self.input_field_after = QLineEdit()
        self.input_field_after.setReadOnly(True)
        self.button_after = QPushButton('选择文件夹')
        self.button_before.clicked.connect(self.event_handler.button_before_click)
        self.button_after.clicked.connect(self.event_handler.button_after_click)

        self.top_layout_1.addWidget(self.label_before)
        self.top_layout_1.addWidget(self.input_field_before)
        self.top_layout_1.addWidget(self.button_before)
        self.top_layout_2.addWidget(self.label_after)
        self.top_layout_2.addWidget(self.input_field_after)
        self.top_layout_2.addWidget(self.button_after)
        self.top_layout.addLayout(self.top_layout_1)
        self.top_layout.addLayout(self.top_layout_2)
        self.top_group.setLayout(self.top_layout)

        self.bottom_left_group = QGroupBox('待复制')
        self.bottom_left_layout = QVBoxLayout()
        self.list_widget = QListWidget()

        self.bottom_left_layout.addWidget(self.list_widget)
        self.bottom_left_group.setLayout(self.bottom_left_layout)

        self.bottom_right_group = QGroupBox('结果')
        self.bottom_right_layout = QVBoxLayout()
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(['文件名', '状态'])

        self.bottom_right_layout.addWidget(self.table_widget)
        self.bottom_right_group.setLayout(self.bottom_right_layout)

        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.addWidget(self.bottom_left_group)
        self.bottom_layout.addWidget(self.bottom_right_group)

        self.button_group = QGroupBox("操作区")
        self.button_layout = QHBoxLayout()
        self.exec_button = QPushButton('Exec Button')
        self.save_button = QPushButton('Save Button')
        self.exit_button = QPushButton('Exit Button')
        self.exec_button.clicked.connect(self.event_handler.confirm_and_execute)
        self.save_button.clicked.connect(self.event_handler.save_records)
        self.exit_button.clicked.connect(self.event_handler.app_exit)

        self.button_layout.addWidget(self.exec_button)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.exit_button)
        self.button_group.setLayout(self.button_layout)

        self.tips_group = QGroupBox("状态")
        self.tips_layout = QHBoxLayout()
        self.tips_label = QLabel('')
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.tips_layout.addWidget(self.tips_label)
        self.tips_layout.addWidget(self.progress_bar)
        self.tips_group.setLayout(self.tips_layout)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.top_group)
        self.main_layout.addLayout(self.bottom_layout)
        self.main_layout.addWidget(self.button_group)
        self.main_layout.addWidget(self.tips_group)

        self.setLayout(self.main_layout)
        self.setWindowTitle('文件复制工具 pyqt5 Ver.1.0.1')
        self.setGeometry(100, 100, 800, 600)
        self.timer_init()

        # self.event_handler.load_file_paths()
        # self.event_handler.update_from_config_paths()

    def timer_init(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)

    def update_datetime(self):
        self.current_datetime = QDateTime.currentDateTime().toString(Qt.ISODate)
        self.tips_label.setText(f'{self.current_datetime}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_app = MyApp()
    my_app.show()
    sys.exit(app.exec_())
