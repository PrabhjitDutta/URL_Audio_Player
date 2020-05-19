
from PyQt5 import QtCore, QtGui, QtWidgets
import pygame
from io import BytesIO
import requests
from threading import Thread
import time

playing = False
play_stopped = True
url = ""

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(827, 187)
        Form.setStyleSheet("background-color: #121212")
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(20, 20, 791, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        self.lineEdit.setFont(font)
        self.lineEdit.setStyleSheet("padding-left: 10px;\n"
"padding-right: 10px;\n"
"background-color: #282828;\n"
"color: white;\n"
"")
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(310, 80, 81, 81))
        self.pushButton.setStyleSheet("background-color: #121212")
        self.pushButton.setFlat(True)
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(410, 80, 81, 81))
        self.pushButton_2.setStyleSheet("background-color: #121212")
        self.pushButton_2.setFlat(True)
        self.pushButton_2.setObjectName("pushButton_2")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        pygame.mixer.init()

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

        r = requests.get(url, stream=True)
        i = BytesIO(r.content)

        pygame.mixer.music.load(i)
        pygame.mixer.music.play()

        while True:
            if play_stopped:
                pygame.mixer.music.stop()
                self.GUI.pushButton.setIcon(QtGui.QIcon('images/unnamed.png'))
                break
            while playing and not play_stopped:
                if not pygame.mixer.music.get_busy():
                    play_stopped = True
                    break
                pygame.mixer.music.unpause()
                time.sleep(0.05)
            if not playing and not play_stopped:
                pygame.mixer.music.pause()
                while not playing and not play_stopped:
                    time.sleep(0.05)


def close():
    global play_stopped
    play_stopped = True


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    app.aboutToQuit.connect(close)
    sys.exit(app.exec_())
