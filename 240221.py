import logging
import sys

from PyQt5.QtCore import QDateTime, Qt, QTimer, QProcess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMainWindow, QAction

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_datetime = QDateTime.currentDateTime().toString(Qt.ISODate)
        self.timer = QTimer()
        self.exec_action = QAction('実行', self)
        self.main_layout = QVBoxLayout()
        self.tips_label = QLabel('')
        self.status_label = QLabel('画面初期化...')
        self.tips_layout_2 = QHBoxLayout()
        self.tips_layout_1 = QHBoxLayout()
        self.tips_layout = QVBoxLayout()
        self.tips_group = QGroupBox("状態")
        self.exec_button = QPushButton('実行')
        self.button_layout = QHBoxLayout()
        self.button_group = QGroupBox("操作")
        self.init_ui()

    def init_ui(self):
        self.exec_button.clicked.connect(self.execute_for_py1)

        self.button_layout.addWidget(self.exec_button)
        self.button_group.setLayout(self.button_layout)

        self.tips_layout_1.addWidget(self.status_label)
        self.tips_layout_2.addWidget(self.tips_label)
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
        self.exec_action.triggered.connect(self.execute_for_py1)
        file_menu.addAction(self.exec_action)
        self.exec_action.setEnabled(True)
        self.exec_action.setShortcut('Ctrl+E')

    def timer_init(self):
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)

    def update_datetime(self):
        self.tips_label.setText(f'{self.current_datetime}')

    def execute_for_py1(self):
        logging.warning("execute_for_py1, script = record.py")
        process = QProcess()
        process.start('python', ['record.py'])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_app = MyApp()
    my_app.show()
    sys.exit(app.exec_())