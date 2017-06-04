#!/usr/python3
# Camera.py
# This script open a qt window where one can display the computer's webcam stream. Basic treatments can be performed on
# those images.
#
# Software versions
# This script was developed using: python 3.5.3 / numpy 1.12.1 / opencv3 3.1.0 / pyqt 5.6.0

# Base packages
import os, sys
import time
import getopt
from threading import Thread, Lock

# Downloaded packages
import numpy as np
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets

# Global definitions
SCREEN_RESOLUTION = [1920, 1080]
VIDEO_RESOLUTION = [640, 480]
try:
    if os.uname()[1] == 'raspberrypi':
        PLATFORM = 'raspPi'
    else:
        PLATFORM = sys.platform
except AttributeError:
    PLATFORM = sys.platform
print('Running on', PLATFORM)

grayScaleTable = []
for i in range(0, 256):
    grayScaleTable.append(QtGui.qRgb(i, i, i))


class QtSignal(QtCore.QObject):
    # FIXME: try to get rid of this (i.e. better understand Qt signal process)
    signal = QtCore.pyqtSignal(object)


class Interface(QtWidgets.QWidget):

    def __init__(self):
        super(Interface, self).__init__()
        self.size = [800, 600]
        self.button_connect = None
        self.label_image = None

        self.captureThread = None
        self.captureRunning = False
        self.captureMode = 'raw'

        self.newImageSig = QtSignal()
        self.newImageSig.signal.connect(self.updateImage)

        self.initUI()

    def initUI(self):
        self.setGeometry(int((SCREEN_RESOLUTION[0]-self.size[0])/2),
                         int((SCREEN_RESOLUTION[1]-self.size[1])/2),
                         self.size[0], self.size[1])
        self.setWindowTitle('Camera')

        button_quit = QtWidgets.QPushButton('Quit', self)
        button_quit.setGeometry(10, 10, 100, 30)
        button_quit.clicked.connect(self.quit)

        self.button_connect = QtWidgets.QPushButton('Connect', self)
        self.button_connect.setGeometry(10, 50, 100, 30)
        self.button_connect.clicked.connect(self.connect)

        checkboxGroup_mode = QtWidgets.QButtonGroup(self)
        checkboxGroup_mode.setObjectName('Treatment')

        checkbox_raw = QtWidgets.QCheckBox('Raw image', self)
        checkbox_raw.setChecked(True)
        checkbox_raw.setGeometry(10, 130, 100, 30)
        checkbox_raw.stateChanged.connect(self.updateMode)
        checkboxGroup_mode.addButton(checkbox_raw)

        checkbox_gray = QtWidgets.QCheckBox('Gray image', self)
        checkbox_gray.setGeometry(10, 170, 100, 30)
        checkbox_gray.stateChanged.connect(self.updateMode)
        checkboxGroup_mode.addButton(checkbox_gray)

        checkbox_edges = QtWidgets.QCheckBox('Canny edges detection', self)
        checkbox_edges.setGeometry(10, 210, 100, 30)
        checkbox_edges.stateChanged.connect(self.updateMode)
        checkboxGroup_mode.addButton(checkbox_edges)

        self.modeCheckBoxes = {'raw': checkbox_raw, 'gray': checkbox_gray, 'edges': checkbox_edges}

        self.label_image = QtWidgets.QLabel(self)
        self.label_image.setGeometry(120, 10, 640, 480)

        self.show()

    def updateMode(self):
        for mode, checkbox in self.modeCheckBoxes.items():
            if checkbox.checkState():
                self.captureMode = mode

    def updateImage(self, frame):
        if len(frame.shape) == 3:  # RGB image
            # Convert ndarray to QImage
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QtGui.QImage(frame, frame.shape[1], frame.shape[0], frame.shape[1]*3,
                                 QtGui.QImage.Format_RGB888)

        elif len(frame.shape) == 2:  # Grayscale image
            # Convert ndarray to QImage
            image = QtGui.QImage(frame, frame.shape[1], frame.shape[0],
                                 QtGui.QImage.Format_Indexed8)
            image.setColorTable(grayScaleTable)

        # Pass image to QLabel to display it
        pixmap = QtGui.QPixmap(image)
        self.label_image.setPixmap(pixmap)

    def startvideoCaptureThread(self):
        self.captureThread = Thread(None, self.videoCapture, 'thread-capture')
        self.captureThread.daemon = True
        self.captureThread.start()

    def stopVideoCaptureThread(self):
        if self.captureThread is not None:
            self.captureRunning = False
            self.captureThread.join()
            self.captureThread = None

    def connect(self):
        if self.button_connect.text() == 'Connect':
            self.startvideoCaptureThread()
            self.button_connect.setText('Disconnect')
        else:
            self.stopVideoCaptureThread()
            self.button_connect.setText('Connect')

    def videoCapture(self):
        self.captureRunning = True

        print('Begin of Thread - videoCapture')
        capture = cv2.VideoCapture(0)

        while self.captureRunning:
            # Capture one frame
            # FIXME: check what the 'success' variable gets exactly
            time.sleep(0.05)
            success, frame = capture.read()
            # Operations on frame
            if self.captureMode == 'edges':
                frame = cv2.Canny(frame, 100, 200)
            elif self.captureMode == 'gray':
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Transmit image to GUI
            self.newImageSig.signal.emit(frame)

        # When everything done, release the capture
        capture.release()
        cv2.destroyAllWindows()
        print('End of thread - videoCapture')

    def quit(self):
        self.stopVideoCaptureThread()
        exit(0)


def main():
    # handle parameters for screen an video resolution
    global SCREEN_RESOLUTION
    global VIDEO_RESOLUTION
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:v:", "")
    except getopt.GetoptError as err:
        print(err)
    for option, argument in opts:
        if option == "-s":
            SCREEN_RESOLUTION = [int(x) for x in argument.split("x")]
        elif option == "-v":
            VIDEO_RESOLUTION = [int(x) for x in argument.split("x")]
        elif option == "-h":
            print("Usage:", sys.argv[0], "[options...]")
            print("Options:")
            print("-h               display help")
            print("-s <int>x<int>   screen resolution")
            print("-v <int>x<int>   video resolution")
            sys.exit(0)

    app = QtWidgets.QApplication(sys.argv)
    interface = Interface()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
