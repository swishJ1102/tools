import logging
import sys

from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread
from PyQt5.QtWidgets import QApplication, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QProgressBar, \
    QPushButton, QTableWidget, QVBoxLayout, QWidget, QMainWindow, \
    QAction
import subprocess


class Worker(QThread):
    def __init__(self, script):
        super().__init__()
        self.script = script

    def run(self):
        logging.warning("run, script = %s", self.script)
        subprocess.call(['python', self.script])


class EventHandler:
    def __init__(self, parent):
        self.parent = parent
        self.detail_table_timer = QTimer(self.parent)
        self.pic_no_cell = []
        logging.basicConfig(filename='recordScreen.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    @staticmethod
    def execute(self):
        logging.warning("execute, script = record.py")
        worker = Worker('record.py')
        logging.warning("execute, start")
        worker.start()
        # subprocess.call(['python', 'record.py'])


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_datetime = QDateTime.currentDateTime().toString(Qt.ISODate)
        self.timer = QTimer()
        self.info_action = QAction('バージョン', self)
        self.exit_action = QAction('退出', self)
        self.open_action = QAction('報告を開く', self)
        self.exec_action = QAction('実行', self)
        self.main_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.tips_label = QLabel('')
        self.status_label = QLabel('画面初期化...')
        self.tips_layout_2 = QHBoxLayout()
        self.tips_layout_1 = QHBoxLayout()
        self.tips_layout = QVBoxLayout()
        self.tips_group = QGroupBox("状態")
        self.exit_button = QPushButton('退出')
        self.save_button = QPushButton('報告を開く')
        self.exec_button = QPushButton('実行')
        self.button_layout = QHBoxLayout()
        self.button_group = QGroupBox("操作")
        self.event_handler = EventHandler(self)
        self.init_ui()

    def init_ui(self):
        # self.exec_button.setDisabled(True)
        # self.save_button.setDisabled(True)
        # self.exec_button.clicked.connect(self.event_handler.execute)
        self.exec_button.clicked.connect(self.execute_for_py1)
        # self.save_button.clicked.connect(self.event_handler.records_open)
        # self.exit_button.clicked.connect(self.event_handler.app_exit)

        self.button_layout.addWidget(self.exec_button)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.exit_button)
        self.button_group.setLayout(self.button_layout)

        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.tips_layout_1.addWidget(self.status_label)
        self.tips_layout_2.addWidget(self.tips_label)
        self.tips_layout_2.addWidget(self.progress_bar)
        self.tips_layout.addLayout(self.tips_layout_1)
        self.tips_layout.addLayout(self.tips_layout_2)
        self.tips_group.setLayout(self.tips_layout)

        self.main_layout.addWidget(self.button_group)
        self.main_layout.addWidget(self.tips_group)

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

        self.setLayout(self.main_layout)
        self.setWindowTitle('BIP Screen-Tool Ver.1.0 PyQt5')
        self.setGeometry(100, 100, 600, 300)
        self.timer_init()

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('操作')
        self.exec_action.triggered.connect(self.event_handler.execute)
        file_menu.addAction(self.exec_action)
        self.exec_action.setEnabled(True)
        self.exec_action.setShortcut('Ctrl+E')

        # self.open_action.triggered.connect(self.event_handler.records_open)
        file_menu.addAction(self.open_action)
        self.open_action.setEnabled(False)
        self.open_action.setShortcut('Alt+O')

        # self.exit_action.triggered.connect(self.event_handler.app_exit)
        file_menu.addAction(self.exit_action)
        self.exit_action.setEnabled(True)
        self.exit_action.setShortcut('Alt+Q')

        info_menu = menu_bar.addMenu('インフォメーション')
        # self.info_action.triggered.connect(self.event_handler.app_info)
        info_menu.addAction(self.info_action)
        self.info_action.setShortcut('Alt+I')

    def timer_init(self):
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)

    def update_datetime(self):
        self.tips_label.setText(f'{self.current_datetime}')

    @staticmethod
    def execute_for_py1():
        logging.warning("execute_for_py1, script = record.py")
        worker = Worker('record.py')
        logging.warning("execute_for_py1, start")
        worker.start()
        # subprocess.call(['python', 'record.py'])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_app = MyApp()
    my_app.show()
    sys.exit(app.exec_())
