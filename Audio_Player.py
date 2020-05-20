    
from PyQt5 import QtCore, QtGui, QtWidgets
import pygame
from io import BytesIO
import requests
from threading import Thread
import time
from mutagen.mp3 import MP3
import wave
import contextlib
#import pkg_resources.py2_warn


playing = False
play_stopped = True
url = ""
time_progress = 0
audio_length = 0
pthread_flag = False
player_init = False


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(827, 288)
        Form.setStyleSheet("background-color: #121212")
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(20, 32, 791, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        self.lineEdit.setFont(font)
        self.lineEdit.setStyleSheet("padding-left: 15px;\n"
                                    "padding-right: 15px;\n"
                                    "background-color: #282828;\n"
                                    "color: white;\n"
                                    "border-radius: 20px;\n"
                                    "")
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(300, 170, 81, 81))
        self.pushButton.setStyleSheet("background-color: #121212;\n")
        self.pushButton.setFlat(True)
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(410, 170, 81, 81))
        self.pushButton_2.setStyleSheet("background-color: #121212;\n")
        self.pushButton_2.setFlat(True)
        self.pushButton_2.setObjectName("pushButton_2")
        self.progressBar = QtWidgets.QProgressBar(Form)
        self.progressBar.setGeometry(QtCore.QRect(40, 140, 751, 21))
        self.progressBar.setAutoFillBackground(False)
        self.progressBar.setStyleSheet("")
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(False)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setStyleSheet("QProgressBar\n"
                                       "{\n"
                                       "background-color : #535353;\n"
                                       "border : 1px;\n"
                                       "border-radius: 10px;\n"
                                       "}\n"
                                       "QProgressBar::chunk\n"
                                       "{\n"
                                       "border : 1px;\n"
                                       "background: #b3b3b3;\n"
                                       "border-radius: 10px;\n"
                                       "}"
                                       )
        self.horizontalSlider = QtWidgets.QSlider(Form)
        self.horizontalSlider.setGeometry(QtCore.QRect(580, 210, 191, 22))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        progThread = Progess_Thread(self)
        progThread.start()

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Audio Player"))
        self.lineEdit.setPlaceholderText(_translate("Form", "Enter URL"))
        self.pushButton.setIcon(QtGui.QIcon('images/play.png'))
        self.pushButton.setIconSize(QtCore.QSize(75, 75))
        self.pushButton.clicked.connect(self.click_play)
        self.pushButton_2.setIcon(QtGui.QIcon('images/play.png'))
        self.pushButton_2.setIconSize(QtCore.QSize(75, 75))
        self.pushButton_2.clicked.connect(self.click_stop)
        self.horizontalSlider.setMinimum(0)
        self.horizontalSlider.setMaximum(100)
        self.horizontalSlider.setSingleStep(1)
        self.horizontalSlider.setValue(100)

        volThread = Volume_Rocker(self)
        volThread.start()

    def click_play(self):
        global playing
        global play_stopped
        global url
        url = self.lineEdit.text()

        if play_stopped:
            play_stopped = False
            playing = True
            play_thread = PlayThread(self)
            play_thread.start()
            self.pushButton.setIcon(QtGui.QIcon('images/pause.png'))
        elif playing:
            playing = False
            self.pushButton.setIcon(QtGui.QIcon('images/play.png'))
        else:
            playing = True
            self.pushButton.setIcon(QtGui.QIcon('images/pause.png'))

    def click_stop(self):
        global play_stopped
        play_stopped = True


class PlayThread(Thread):
    def __init__(self, GUI):
        Thread.__init__(self)
        self.GUI = GUI

    def run(self):
        global playing
        global play_stopped
        global url
        global time_progress
        global audio_length
        global player_init

        try:
            r = requests.get(url, stream=True)
        except requests.exceptions.MissingSchema:
            self.GUI.lineEdit.clear()
            self.GUI.lineEdit.setPlaceholderText("Enter Valid URL")
            play_stopped = True
            playing = False
            self.GUI.pushButton.setIcon(QtGui.QIcon('images/play.png'))
            return -1
        i = BytesIO(r.content)

        if url[-3:] == 'mp3':
            metadata = MP3(i)
            audio_length = metadata.info.length
            audio_sample_rate = metadata.info.sample_rate
        elif url[-3:] == 'wav':
            with contextlib.closing(wave.open(i, 'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                audio_length = frames / float(rate)
                audio_sample_rate = rate
        else:
            self.GUI.lineEdit.clear()
            self.GUI.lineEdit.setPlaceholderText("Enter Valid URL")
            play_stopped = True
            playing = False
            self.GUI.pushButton.setIcon(QtGui.QIcon('images/play.png'))
            return -1

        i = BytesIO(r.content)
        pygame.mixer.init(audio_sample_rate)
        pygame.mixer.music.load(i)
        player_init = True
        pygame.mixer.music.play()

        while True:
            if play_stopped:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                self.GUI.pushButton.setIcon(QtGui.QIcon('images/play.png'))
                player_init = False
                break
            while playing and not play_stopped:
                if not pygame.mixer.music.get_busy():
                    play_stopped = True
                    playing = False
                    break
                pygame.mixer.music.unpause()
                time_progress = pygame.mixer.music.get_pos()
                time.sleep(0.03)
            if not playing and not play_stopped:
                pygame.mixer.music.pause()
                while not playing and not play_stopped:
                    time.sleep(0.03)


class Progess_Thread(Thread):
    def __init__(self, GUI):
        Thread.__init__(self)
        self.GUI = GUI

    def run(self):
        global playing
        global play_stopped
        global time_progress
        global audio_length
        global pthread_flag
        global got_metadata
        audio_progress = 0

        while True:
            if pthread_flag:
                break
            if play_stopped:
                audio_length = 0
                time_progress = 0
                audio_progress = 0
                self.GUI.progressBar.setProperty("value", 0)
                time.sleep(0.1)

            while playing and player_init:
                audio_progress = ((time_progress/1000)/audio_length)*100
                self.GUI.progressBar.setProperty("value", audio_progress)
                time.sleep(0.1)
            else:
                time.sleep(0.1)


class Volume_Rocker(Thread):
    def __init__(self, GUI):
        Thread.__init__(self)
        self.GUI = GUI

    def run(self):
        while True:
            if pthread_flag:
                break
            while player_init:
                volume = self.GUI.horizontalSlider.value()
                pygame.mixer.music.set_volume(float(volume)/100)
                time.sleep(0.1)
            time.sleep(0.1)


def close():
    global play_stopped
    global pthread_flag
    play_stopped = True
    pthread_flag = True


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    app.aboutToQuit.connect(close)
    sys.exit(app.exec_())
