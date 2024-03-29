import json
import subprocess
import sys
import threading
import time

from PyQt5.QtCore import QDateTime, Qt, QTimer, QProcess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMainWindow, QLabel, QHBoxLayout, \
    QGroupBox, QMessageBox, QSystemTrayIcon, QStyle, QAction, QMenu
from pynput import mouse, keyboard

recording = []
count = 0
mouse_listener = None
keyboard_listener = None

key_mappings = {
    "cmd": "win",
    "alt_l": "alt",
    "alt_r": "alt",
    "ctrl_l": "ctrl",
    "ctrl_r": "ctrl"
}

# default button stylesheet
button_stylesheet = 'QPushButton {height: 20px; width: 30px;\
                                            border: 1.5px solid #8f8f91;\
                                            border-radius: 4px;\
                                            background-color: qlineargradient(x1: 0.2, y1: 0.2, x2: 0.2, y2: 1,\
                                            stop: 0 #f6f7fa, stop: 1 #dadbde);\
                                            min-width: 50px;}\
                    QPushButton:hover {background-color:white;\
                                        color: black;}\
                    QPushButton:pressed {background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\
                                        stop: 0 #dadbde, stop: 1 #f6f7fa);}'

# default button stylesheet
button_stylesheet_cancel = 'QPushButton {height: 20px; width: 30px;\
                                            border: 1.5px solid #8f8f91;\
                                            border-radius: 4px;\
                                            background-color: qlineargradient(x1: -1, y1: -1, x2: -1, y2: -0.5,\
                                            stop: 0 #f6f7fa, stop: 1 #dadbde);\
                                            min-width: 50px;}\
                    QPushButton:hover {background-color:white;\
                                        color: black;}\
                    QPushButton:pressed {background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\
                                        stop: 0 #dadbde, stop: 1 #f6f7fa);}'


def message_box_question(self, context, mode):
    # mode [R: 記録, Q: 退出]
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Question)
    msg_box.setWindowTitle("ツールメッセージ")
    msg_box.setText(context)
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg_box.setDefaultButton(QMessageBox.No)
    msg_box.button(QMessageBox.Yes).setText("はい(&Y)")
    msg_box.button(QMessageBox.Yes).setStyleSheet(button_stylesheet)
    msg_box.button(QMessageBox.No).setText("いいえ(&N)")
    msg_box.button(QMessageBox.No).setStyleSheet(button_stylesheet_cancel)
    result = msg_box.exec_()
    if result == QMessageBox.Yes:
        if mode == 'R':
            # process = QProcess()
            # process.startDetached(start_recording())
            # start_recording()
            # threading.Thread(target=start_recording).start()
            threading.Thread(target=self.start_recording_with_status_update).start()
        if mode == 'Q':
            # self.stop_recording_and_timer()
            stop_recording()
            self.tray_icon.hide()
            self.close()
    elif result == QMessageBox.No:
        if mode == 'R':
            self.exec_button.setDisabled(False)


def message_box_information(self, context):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setWindowTitle("ツールメッセージ")
    msg_box.setText(context)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.setDefaultButton(QMessageBox.Ok)
    msg_box.button(QMessageBox.Ok).setText("はい(&Y)")
    msg_box.button(QMessageBox.Ok).setStyleSheet(button_stylesheet)
    msg_box.exec_()


def show_tips(self, content):
    self.status_label.setText(content)


def on_press(key):
    try:
        json_object = {
            'action': 'pressed_key',
            'key': key.char,
            '_time': time.time()
        }
    except AttributeError:
        if key == keyboard.Key.esc:
            # stop_recording()
            my_app.stop_recording_and_timer()
            return False

        json_object = {
            'action': 'pressed_key',
            'key': str(key),
            '_time': time.time()
        }

    recording.append(json_object)


def on_release(key):
    try:
        json_object = {
            'action': 'released_key',
            'key': key.char,
            '_time': time.time()
        }
    except AttributeError:
        json_object = {
            'action': 'released_key',
            'key': str(key),
            '_time': time.time()
        }

    recording.append(json_object)


def on_move(x, y):
    if len(recording) >= 1:
        if (recording[-1]['action'] == "pressed" and \
            recording[-1]['button'] == 'Button.left') or \
                (recording[-1]['action'] == "moved" and \
                 time.time() - recording[-1]['_time'] > 0.02):
            json_object = {
                'action': 'moved',
                'x': x,
                'y': y,
                '_time': time.time()
            }

            recording.append(json_object)


def on_click(x, y, button, pressed):
    json_object = {
        'action': 'clicked' if pressed else 'unclicked',
        'button': str(button),
        'x': x,
        'y': y,
        '_time': time.time()
    }

    recording.append(json_object)

    if len(recording) > 1:
        if recording[-1]['action'] == 'unclicked' and \
                recording[-1]['button'] == 'Button.right' and \
                recording[-1]['_time'] - recording[-2]['_time'] > 2:
            pass
            # with open('recording.json', 'w') as f:
            #     json.dump(recording, f)
            # print("Mouse recording ended.")
            # return False


def on_scroll(x, y, dx, dy):
    json_object = {
        'action': 'scroll',
        'vertical_direction': int(dy),
        'horizontal_direction': int(dx),
        'x': x,
        'y': y,
        '_time': time.time()
    }

    recording.append(json_object)


def start_recording():
    my_app.showMinimized()
    print("Press 'ESC' to finish recording")
    # my_app.showMinimized()
    global keyboard_listener, mouse_listener, recording
    # 初期化動作集
    recording = []
    keyboard_listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)

    mouse_listener = mouse.Listener(
        on_click=on_click,
        on_scroll=on_scroll,
        on_move=on_move)

    keyboard_listener.start()
    mouse_listener.start()
    keyboard_listener.join()
    mouse_listener.join()


def stop_recording():
    # showfront
    # my_app.show_front()
    if keyboard_listener:
        keyboard_listener.stop()
        print("Keyboard recording ended.")
    if mouse_listener:
        mouse_listener.stop()
        print("Mouse recording ended.")
    if recording:
        with open('recording.json', 'w') as f:
            json.dump(recording, f)

    # recording_for_convert = read_json_file()
    # convert_to_pyautogui_script(recording_for_convert)


def read_json_file():
    with open('recording.json') as f:
        recording = json.load(f)

    def excluded_actions(object):
        # return "released" not in object["action"] and \
        #     "scroll" not in object["action"]
        return "released" not in object["action"]

    recording = list(filter(excluded_actions, recording))

    return recording


def convert_to_pyautogui_script(recording):
    if not recording:
        return

    output = open("play.py", "w")
    output.write("import time\n")
    output.write("import pyautogui\n\n")

    for i, step in enumerate(recording):
        print(step)

        not_first_element = (i - 1) > 0
        if not_first_element:
            # compare time to previous time for the 'sleep' with a 10% buffer
            pause_in_seconds = (step["_time"] - recording[i - 1]["_time"]) * 1.1

            output.write(f"time.sleep({pause_in_seconds})\n\n")
        else:
            output.write("time.sleep(1)\n\n")

        if step["action"] == "pressed_key":
            key = step["key"].replace("Key.", "") if "Key." in step["key"] else step["key"]

            if key in key_mappings.keys():
                key = key_mappings[key]

            output.write(f"pyautogui.press('{key}')\n")

        if step["action"] == "clicked":
            output.write(f"pyautogui.moveTo({step['x']}, {step['y']})\n")

            if step["button"] == "Button.right":
                output.write("pyautogui.mouseDown(button='right')\n")
            else:
                output.write("pyautogui.mouseDown()\n")

        if step["action"] == "unclicked":
            output.write(f"pyautogui.moveTo({step['x']}, {step['y']})\n")

            if step["button"] == "Button.right":
                output.write("pyautogui.mouseUp(button='right')\n")
            else:
                output.write("pyautogui.mouseUp()\n")
        # 20240221
        if step["action"] == "scroll":
            output.write(f"pyautogui.moveTo({step['x']}, {step['y']})\n")

            if step["vertical_direction"]:
                output.write(f"pyautogui.scroll({step['vertical_direction'] * 200})\n")

    output.write(f"print('finish playing!')\n")

    print("Recording converted. Saved to 'play.py'")


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.process = None
        self.current_datetime = QDateTime.currentDateTime().toString(Qt.ISODate)
        self.tray_icon = QSystemTrayIcon(self)
        self.init_tray_icon()
        self.timer = QTimer()
        self.timer_for_status = QTimer()
        self.scroll_offset = 0
        self.scroll_direction = 1

        self.main_layout = QVBoxLayout()

        self.exec_layout = QHBoxLayout()
        self.exec_group = QGroupBox("操作")
        self.exec_button = QPushButton('記録を始めます！')
        self.exec_button.setStyleSheet(button_stylesheet)

        self.conv_layout = QHBoxLayout()
        self.conv_group = QGroupBox("コンバート")
        self.conv_button = QPushButton('記録ファイルをコンバートしましょう～')
        self.conv_button.setStyleSheet(button_stylesheet)

        self.play_layout = QHBoxLayout()
        self.play_group = QGroupBox("再現")
        self.play_button = QPushButton('プレー')
        self.play_button.setStyleSheet(button_stylesheet)

        self.tips_label = QLabel('')
        self.status_label = QLabel('画面初期化...')
        self.tips_layout_2 = QHBoxLayout()
        self.tips_layout_1 = QHBoxLayout()
        self.tips_layout = QVBoxLayout()
        self.tips_group = QGroupBox("状態")

        self.exit_button = QPushButton('退出')
        self.exit_button.setStyleSheet(button_stylesheet_cancel)
        self.bottom_layout_1 = QHBoxLayout()
        self.bottom_layout_2 = QHBoxLayout()
        self.bottom_layout = QVBoxLayout()
        self.bottom_group = QGroupBox("")
        self.init_ui()

    def init_ui(self):
        # 信号
        self.exec_button.clicked.connect(self.execute)
        self.conv_button.clicked.connect(self.convert)
        self.play_button.clicked.connect(self.play)

        self.exec_layout.addWidget(self.exec_button)
        self.exec_group.setLayout(self.exec_layout)

        self.conv_layout.addWidget(self.conv_button)
        self.conv_group.setLayout(self.conv_layout)

        self.play_layout.addWidget(self.play_button)
        self.play_group.setLayout(self.play_layout)

        self.tips_layout_1.addWidget(self.status_label)
        self.tips_layout.addLayout(self.tips_layout_1)
        # self.tips_layout.addLayout(self.tips_layout_2)
        self.tips_group.setLayout(self.tips_layout)

        self.exit_button.clicked.connect(self.exit)
        self.bottom_layout_1.addWidget(self.exit_button)
        self.bottom_layout_2.addWidget(self.tips_label)
        self.bottom_layout.addLayout(self.bottom_layout_1)
        self.bottom_layout.addLayout(self.bottom_layout_2)
        self.bottom_group.setLayout(self.bottom_layout)

        self.main_layout.addWidget(self.exec_group)
        self.main_layout.addWidget(self.conv_group)
        self.main_layout.addWidget(self.play_group)
        self.main_layout.addWidget(self.tips_group)
        self.main_layout.addWidget(self.bottom_group)

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

        self.setLayout(self.main_layout)
        self.setWindowTitle('BIP Screen-Tool Ver.1.0 PyQt5')
        self.setGeometry(750, 275, 400, 400)
        self.timer_init()

    def init_tray_icon(self):
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show_normal)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_app)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(exit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def show_normal(self):
        self.showNormal()

    def exit_app(self):
        self.exit()

    def timer_init(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)

    def update_datetime(self):
        self.current_datetime = QDateTime.currentDateTime().toString(Qt.ISODate)
        self.tips_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tips_label.setText(f'{self.current_datetime}')

    def execute(self):
        self.exec_button.setDisabled(True)
        # logging.warning("execute_for_py1, script = record.py")
        # process = QProcess()
        # # process.start('python', ['record.py'])
        # process.startDetached('python', ['record.py'])
        show_tips(self, "画面の記録を開始いたします。")
        # show tips in motion
        message_box_question(self, "画面の記録を開始します。\n[Esc]を押して操作を終了します。", "R")

    def convert(self):
        recording_for_convert = read_json_file()
        convert_to_pyautogui_script(recording_for_convert)
        show_tips(self, "ファイルがコンバートしました。")

    def show_front(self):
        flags = self.windowFlags()
        self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        self.show()
        self.setWindowFlags(flags)
        self.show()

    def play(self):
        show_tips(self, "再現を始まる。")
        self.showMinimized()
        st = subprocess.STARTUPINFO()
        st.dwFlags = subprocess.STARTF_USESHOWWINDOW
        st.wShowWindow = subprocess.SW_HIDE
        # self.process = QProcess()
        # self.process.finished.connect(self.show_play_finished_message)
        # self.process.startDetached('python', ['play.py'])
        subp = subprocess.Popen(
            'python ./play.py',
            encoding='utf-8',
            stdout=subprocess.PIPE,
            startupinfo=st
        )
        # out, err = subp.communicate()
        # subp.wait()

        while subp.poll() is None:
            print("processing!!!!!!!!")
        if subp.poll() == 0:
            print("subp.poll()subp.poll()subp.poll()", subp.poll())
            self.show_normal()
            # self.showNormal()
            # self.show_front()
            show_tips(self, "再現しました。")
            # message_box_information(self, "再現完了。")
        if subp.stdout.read() == 'finish playing!':
            print("DONE DONE DONE")
        # print('subp~~~~~~out : ', out)
        # print('subp~~~~~~err : ', err)
        # if out == 'finish playing!':
        #     print('subp~~~~~~out handan : ', out)
        #     self.show_play_finished_message()
        # if self.process.waitForStarted():
        #     self.process.waitForFinished(-1)
        #     self.show_play_finished_message()

    def exit(self):
        message_box_question(self, "ツールを終了したいですか。", "Q")

    def start_recording_with_status_update(self):
        self.status_label.setText("※画面の記録を開始します※[Esc]を押して操作を終了します※ご不明な点がございましたら、管理者にお問い合わせください")
        self.scroll_offset = 0
        self.scroll_direction = 1
        # self.timer_for_status.timeout.connect(self.update_status_label)
        # self.timer_for_status.start(1000)
        QTimer.singleShot(0, self.start_timer)
        threading.Thread(target=start_recording).start()
        # start_recording()
        # self.setWindowState(Qt.WindowMinimized)

    def start_timer(self):
        self.timer_for_status.timeout.connect(self.update_status_label)
        self.timer_for_status.start(750)

    def stop_recording_and_timer(self):
        self.stop_timer()
        my_app.showNormal()
        self.status_label.setText("画面の記録が終わりました。")
        # message_box_information(self, "記録完了。")
        stop_recording()

    def stop_timer(self):
        self.timer_for_status.stop()

    def update_status_label(self):
        current_text = self.status_label.text()
        displayed_text = current_text[self.scroll_offset:] + current_text[:self.scroll_offset]
        self.status_label.setText(displayed_text)
        self.scroll_offset = (self.scroll_offset + 1) % len(current_text)
        # new_text = f'{current_text[1:]}{current_text[0]}'
        # new_text = current_text[-1] + current_text[:-1]
        # self.status_label.setText(new_text)
        # if len(current_text) < 5:
        #     self.scroll_direction *= -1
        # elif len(current_text) > 10:
        #     self.scroll_direction *= -1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Windows , windowsvista , Fusion
    my_app = MyApp()
    my_app.show()
    sys.exit(app.exec_())
