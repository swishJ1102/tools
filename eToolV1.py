"""成果物作成"""
import os
import shutil
import subprocess
import sys
from configparser import ConfigParser

from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import QApplication, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QProgressBar, \
    QPushButton, QVBoxLayout, QWidget, QFileDialog, QMessageBox, QMainWindow

FOLDER_LOG = "LOG"
FOLDER_COVERAGE = "カバレッジ"
FOLDER_COMPARE = "現新比較"
FOLDER_COMPARE_OLD = "現"
FOLDER_COMPARE_NEW = "新"
FOLDER_COMPARE_FILE = "ファイル"
FOLDER_COMPARE_DB = "DB"

EXCEL_EVIDENCE = "エビデンス.xlsx"
EXCEL_TEST = "テスト仕様書.xlsx"
EXCEL_COMPARE = "手修正確認.xlsx"
EXCEL_COVERAGE = "カバー.xlsx"

INPUT_BROWSE = ''
# button stylesheet
BUTTON_STYLESHEET = 'QPushButton {background-color:rgba(255,178,0,100%);\
                                                    color: white; \
                                                    border-radius: 10px; \
                                                    border: 2px groove gray; \
                                                    border-style: outset;}\
                    QPushButton:hover{background-color:white;\
                                        color: black;}\
                                        QPushButton:pressed{background-color:rgb(85, 170, 255); \
                                        border-style: inset; }'


def get_program_path():
    """アプリのパスを取得"""
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def get_config_file_path():
    """コンフィグのパスを取得"""
    return os.path.join(get_program_path(), ".eTool_config.ini")


def load_config_content(tag):
    """コンフィグをロード"""
    config = ConfigParser()
    config.read(get_config_file_path())
    return config[tag] if tag in config else {}


def save_file_paths():
    """コンフィグにパスインフォを保存"""
    if os.path.exists(INPUT_BROWSE):
        config = ConfigParser()
        config.read(get_config_file_path())
        config.set('Paths', 'default_path', os.path.dirname(os.path.abspath(INPUT_BROWSE)))
        with open(get_config_file_path(), 'w', encoding='utf-8') as configfile:
            config.write(configfile)


def is_null_check(self):
    """非空チェック"""
    check_flag = False
    context = ""
    if self.parent.input_browse.text() is None or self.parent.input_browse.text() == '':
        check_flag = True
        context = context + "サンプルパス\n"
    if self.parent.input_file.text() is None or self.parent.input_file.text() == '':
        check_flag = True
        context = context + "出力パス\n"
    if self.parent.input_kinoid.text() is None or self.parent.input_kinoid.text() == '':
        check_flag = True
        context = context + "機能ID\n"
    if self.parent.input_kinoname.text() is None or self.parent.input_kinoname.text() == '':
        check_flag = True
        context = context + "機能名\n"
    if self.parent.input_tantounsya.text() is None or self.parent.input_tantounsya.text() == '':
        check_flag = True
        context = context + "担当者\n"
    return check_flag, context


# todo
def set_message_box(message_type, title, context):
    """メッセージを反映"""
    if message_type == 'WARNING':
        QMessageBox.warning(None, title, context)
    if message_type == 'CRITICAL':
        QMessageBox.critical(None, title, context)
    if message_type == 'INFO':
        QMessageBox.information(None, title, context)


def folder_create(self):
    """フォルダを作成"""
    try:
        os.makedirs(os.path.join(self.parent.input_file.text(), self.parent.input_kinoid.text()))
    except FileExistsError:
        set_message_box("CRITICAL", "フォルダ", "フォルダがすでに存在します。")
        raise
    except OSError as e:
        set_message_box("INFO", "フォルダ", e)
        raise
    os.makedirs(os.path.join(self.parent.input_file.text(),
                             self.parent.input_kinoid.text(), FOLDER_COVERAGE))
    os.makedirs(os.path.join(self.parent.input_file.text(),
                             self.parent.input_kinoid.text(), FOLDER_LOG))
    os.makedirs(os.path.join(self.parent.input_file.text(),
                             self.parent.input_kinoid.text(), FOLDER_COMPARE))
    os.makedirs(os.path.join(self.parent.input_file.text(),
                             self.parent.input_kinoid.text(), FOLDER_COMPARE, FOLDER_COMPARE_OLD))
    os.makedirs(os.path.join(self.parent.input_file.text(), self.parent.input_kinoid.text(),
                             FOLDER_COMPARE, FOLDER_COMPARE_OLD, FOLDER_COMPARE_FILE))
    os.makedirs(os.path.join(self.parent.input_file.text(), self.parent.input_kinoid.text(),
                             FOLDER_COMPARE, FOLDER_COMPARE_OLD, FOLDER_COMPARE_DB))
    os.makedirs(os.path.join(self.parent.input_file.text(), self.parent.input_kinoid.text(),
                             FOLDER_COMPARE, FOLDER_COMPARE_NEW))
    os.makedirs(os.path.join(self.parent.input_file.text(), self.parent.input_kinoid.text(),
                             FOLDER_COMPARE, FOLDER_COMPARE_NEW, FOLDER_COMPARE_FILE))
    os.makedirs(os.path.join(self.parent.input_file.text(), self.parent.input_kinoid.text(),
                             FOLDER_COMPARE, FOLDER_COMPARE_NEW, FOLDER_COMPARE_DB))


def excel_copy(self):
    """サンプルからファイルをコピー"""
    i = 0
    file_names = os.listdir(self.parent.input_browse.text())
    for file_name in file_names:
        if file_name.find("エビデンス") >= 0 \
                or file_name.find("カバー補足") >= 0 \
                or file_name.find("テスト仕様書") >= 0 \
                or file_name.find("手修正確認") >= 0:
            destination_file = os.path.join(self.parent.input_file.text(),
                                            self.parent.input_kinoid.text(),
                                            os.path.basename(file_name))
            shutil.copyfile(os.path.join(self.parent.input_browse.text(),
                                         file_name), destination_file)
            i += 1
    if i < 4:
        set_message_box("INFO", "EXPLORER", "サンプルが足りないので\nチェックしてください。")


def excel_format(self):
    """担当者、機能ID、機能名"""
    pass


def svn_operate(self):
    """SVNから更新"""
    print('svn_operate start...')
    # cmd_update = 'svn update ' + self.parent.input_browse.text()
    # result = os.system(cmd_update)
    # print("svn update result : ", result)
    result = subprocess.run(['svn', '--version'], text=True, capture_output=True, check=False)
    if "svn, version" in result.stdout:
        with subprocess.Popen(['svn', 'update', self.parent.input_browse.text()],
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True) as proc:
            stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            set_message_box("CRITICAL", "SVN",
                            "サンプルフォルダをSVNから最新版に更新することが失敗しました、\n自分で更新してください。")
            print(f"Command '{self.parent.input_browse.text()}' "
                  f"failed with return code {proc.returncode}")
            print("Errors:", stderr)
        else:
            set_message_box("INFO", "SVN", "SVNから更新することが成功しました、\n続けてください。")
            print(f"Command '{self.parent.input_browse.text()}' executed successfully")
            print("Output:", stdout)
    else:
        set_message_box("WARNING", "SVN",
                        "コンピューターにはまだSVNコマンドラインがインストールされていません。\nインストールしてください。")


class EventHandler:
    """EventHandler"""

    def __init__(self, parent):
        self.parent = parent

    def browse_button_click(self):
        """サンプル開く"""
        try:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            folder_path = QFileDialog.getExistingDirectory(self.parent, "サンプルパス選択", options=options)
            if folder_path:
                print("folder_path", folder_path)
                self.parent.input_browse.setText(folder_path)
                set_message_box("INFO", "注意", "サンプルフォルダをSVNから最新版に更新する必要があります。")
                svn_operate(self)
        except OSError as e:
            print("An error occurred : ", e)
            raise
        except RuntimeError as e:
            print("A runtime error occurred : ", e)
            raise

    def file_button_click(self):
        """出力開く"""
        try:
            folder_path = QFileDialog.getExistingDirectory(self.parent, "出力パス選択")
            if folder_path:
                print(folder_path)
                self.parent.input_file.setText(folder_path)
        except Exception as e:
            print("An error occurred : ", e)
            raise

    def execute(self):
        """実行"""
        self.parent.progress_bar.setValue(0)
        check_flag, context = is_null_check(self)
        if check_flag is True:
            set_message_box("WARNING", "非空チェック", context[:len(context) - 1])
            return
            # QMessageBox.warning(None, "非空チェック", context[:len(context) - 1])
        try:
            folder_create(self)
        except Exception as e:
            print("Caught an exception in some_method:", e)
            raise
        self.parent.progress_bar.setValue(10)
        excel_copy(self)
        self.parent.progress_bar.setValue(20)

        self.parent.save_button.setDisabled(False)

    def records_open(self):
        """フォルダを開く"""
        os.startfile(self.parent.input_file.text())

    def app_exit(self):
        """アプリを退出"""
        msg_box = QMessageBox()
        msg_box.setWindowTitle("ツールメッセージ")
        msg_box.setText("ツールを終了したいですか。")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText("はい(&Y)")
        msg_box.button(QMessageBox.No).setText("いいえ(&N)")
        result = msg_box.exec_()
        if result == QMessageBox.Yes:
            save_file_paths()
            self.parent.close()


class MyApp(QMainWindow):
    """UI Class"""

    def __init__(self):
        """init"""
        super().__init__()
        self.current_datetime = QDateTime.currentDateTime().toString(Qt.ISODate)
        self.timer = QTimer()
        self.top_group = QGroupBox("選択")
        self.top_layout_1 = QHBoxLayout()
        self.top_layout_2 = QHBoxLayout()
        self.top_layout_3 = QHBoxLayout()
        self.top_layout_4 = QHBoxLayout()
        self.top_layout = QVBoxLayout()
        self.label_browse = QLabel('サンプル ')
        self.input_browse = QLineEdit()
        self.input_browse.setReadOnly(True)
        self.button_browse = QPushButton('開く')
        self.label_file = QLabel('出力パス')
        self.input_file = QLineEdit()
        self.input_file.setReadOnly(True)
        self.button_file = QPushButton('開く')
        # todo QComboBoxに変更
        self.label_kinoid = QLabel('機能ID  ')
        self.input_kinoid = QLineEdit()
        self.label_kinoname = QLabel('機能名  ')
        self.input_kinoname = QLineEdit()
        self.label_tantounsya = QLabel('担当者  ')
        self.input_tantounsya = QLineEdit()

        self.top_layout_1.addWidget(self.label_browse)
        self.top_layout_1.addWidget(self.input_browse)
        self.top_layout_1.addWidget(self.button_browse)
        self.top_layout_2.addWidget(self.label_file)
        self.top_layout_2.addWidget(self.input_file)
        self.top_layout_2.addWidget(self.button_file)
        self.top_layout_3.addWidget(self.label_kinoid)
        self.top_layout_3.addWidget(self.input_kinoid)
        self.top_layout_3.addWidget(self.label_kinoname)
        self.top_layout_3.addWidget(self.input_kinoname)
        self.top_layout_4.addWidget(self.label_tantounsya)
        self.top_layout_4.addWidget(self.input_tantounsya)
        self.top_layout.addLayout(self.top_layout_1)
        self.top_layout.addLayout(self.top_layout_2)
        self.top_layout.addLayout(self.top_layout_3)
        self.top_layout.addLayout(self.top_layout_4)
        self.top_group.setLayout(self.top_layout)

        self.button_group = QGroupBox("操作")
        self.button_layout = QHBoxLayout()
        self.exec_button = QPushButton('実行')
        self.save_button = QPushButton('出力フォルダを開く')
        self.save_button.setDisabled(True)
        self.exit_button = QPushButton('退出')
        self.exit_button.setStyleSheet("background-color: lightgray")

        self.button_layout.addWidget(self.exec_button)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.exit_button)
        self.button_group.setLayout(self.button_layout)

        self.tips_group = QGroupBox("状態")
        self.tips_layout = QVBoxLayout()
        self.tips_layout_1 = QHBoxLayout()
        self.tips_layout_2 = QHBoxLayout()
        self.status_label = QLabel('')
        self.tips_label = QLabel('')
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.tips_layout_1.addWidget(self.status_label)
        self.tips_layout_2.addWidget(self.tips_label)
        self.tips_layout_2.addWidget(self.progress_bar)
        # self.tips_layout.addLayout(self.tips_layout_1)
        self.tips_layout.addLayout(self.tips_layout_2)
        self.tips_group.setLayout(self.tips_layout)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.top_group)
        self.main_layout.addWidget(self.button_group)
        self.main_layout.addWidget(self.tips_group)

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

        self.setLayout(self.main_layout)
        self.setWindowTitle('BIP-成果物作成-Ver.1.0-Powered by PyQt5')
        self.setGeometry(650, 350, 600, 300)
        self.setFixedSize(600, 300)
        self.event_handler = EventHandler(self)
        self.init_ui()

    def init_ui(self):
        """init_ui"""
        self.button_browse.clicked.connect(self.event_handler.browse_button_click)
        # self.button_browse.released.connect(self.event_handler.browse_button_released)
        self.button_file.clicked.connect(self.event_handler.file_button_click)
        self.exec_button.clicked.connect(self.event_handler.execute)
        self.save_button.clicked.connect(self.event_handler.records_open)
        self.exit_button.clicked.connect(self.event_handler.app_exit)

        self.timer_init()

    def timer_init(self):
        """タイマーコントロール"""
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)

    def update_datetime(self):
        """タイマーを更新"""
        self.tips_label.setText(f'{self.current_datetime}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Windows')  # Windows , windowsvista , Fusion
    my_app = MyApp()
    my_app.show()
    sys.exit(app.exec_())
