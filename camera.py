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
import math
from threading import Thread, Lock
from copy import deepcopy

# Downloaded packages
import numpy as np
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets

# Global definitions
SCREEN_RESOLUTION = [1920, 1080]
VIDEO_RESOLUTION = [640, 480]

# Get current platform and print it
try:
    if os.uname()[1] == 'raspberrypi':
        PLATFORM = 'raspPi'
    else:
        PLATFORM = sys.platform
except AttributeError:
    PLATFORM = sys.platform
print('Running on', PLATFORM)

# Grayscale table
grayScaleTable = []
for i in range(0, 256):
    grayScaleTable.append(QtGui.qRgb(i, i, i))


class QtSignal(QtCore.QObject):
    # FIXME: try to get rid of this (i.e. better understand Qt signal process)
    signal = QtCore.pyqtSignal(object)


class Interface(QtWidgets.QWidget):
    def __init__(self):
        super(Interface, self).__init__()
        self.size = SCREEN_RESOLUTION
        self.button_connect = None
        self.label_image = None

        self.captureThread = None
        self.captureRunning = False
        self.captureMode = 'raw'
        self.cannyEdges = [50, 70]

        self.newImageSig = QtSignal()
        self.newImageSig.signal.connect(self.updateImage)

        self.initUI()

    def initUI(self):
        # Init window
        self.setGeometry(int((SCREEN_RESOLUTION[0]-self.size[0])/2),
                         int((SCREEN_RESOLUTION[1]-self.size[1])/2),
                         self.size[0], self.size[1])
        self.setWindowTitle('Camera')

        # Init buttons
        button_quit = QtWidgets.QPushButton('Quit', self)
        button_quit.setGeometry(10, 10, 100, 30)
        button_quit.clicked.connect(self.quit)

        self.button_connect = QtWidgets.QPushButton('Connect', self)
        self.button_connect.setGeometry(10, 50, 100, 30)
        self.button_connect.clicked.connect(self.connect)

        # Init checkboxes group that will monitor image treatments (i.e. modes)
        checkboxGroup_mode = QtWidgets.QButtonGroup(self)
        checkboxGroup_mode.setObjectName('Treatment')

        checkbox_raw = QtWidgets.QCheckBox('Raw image', self)
        checkbox_raw.setChecked(True)
        checkbox_raw.setGeometry(10, 130, 250, 30)
        checkbox_raw.stateChanged.connect(self.updateMode)
        checkboxGroup_mode.addButton(checkbox_raw)

        checkbox_gray = QtWidgets.QCheckBox('Gray image', self)
        checkbox_gray.setGeometry(10, 170, 250, 30)
        checkbox_gray.stateChanged.connect(self.updateMode)
        checkboxGroup_mode.addButton(checkbox_gray)

        checkbox_blur = QtWidgets.QCheckBox('Blurred image', self)
        checkbox_blur.setGeometry(10, 210, 250, 30)
        checkbox_blur.stateChanged.connect(self.updateMode)
        checkboxGroup_mode.addButton(checkbox_blur)

        checkbox_edges = QtWidgets.QCheckBox('Canny edges detection', self)
        checkbox_edges.setGeometry(10, 250, 250, 30)
        checkbox_edges.stateChanged.connect(self.updateMode)
        checkboxGroup_mode.addButton(checkbox_edges)

        slider_cannyedgesvalue = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        slider_cannyedgesvalue.setGeometry(10,290,250,30)
        slider_cannyedgesvalue.setValue(25)
        slider_cannyedgesvalue.valueChanged[int].connect(self.changeValueSlider)


        self.modeCheckBoxes = {'raw': checkbox_raw, 'gray': checkbox_gray, 'edges': checkbox_edges,
                               'blur': checkbox_blur}

        # Init QLabel to display images
        self.label_image = QtWidgets.QLabel(self)
        self.label_image.setGeometry(270, 10, 640, 480)

        self.show()

    def changeValueSlider(self, value):
        value *= 2
        self.cannyEdges = [value, value+math.floor(value/5)]

    def updateMode(self):
        """ Check the state of the checkboxes and update 'self.mode' accordingly """
        for mode, checkbox in self.modeCheckBoxes.items():
            if checkbox.checkState():
                self.captureMode = mode

    def updateImage(self, frame):
        """ Convert received <frame> (numpy.ndarray) to QImage, then QPixmap, and displayi it """
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
        """ Properly start the capture thread """
        self.captureThread = Thread(None, self.videoCapture, 'thread-capture')
        self.captureThread.daemon = True
        self.captureThread.start()

    def stopVideoCaptureThread(self):
        """ Properly stop teh capture thread"""
        if self.captureThread is not None:
            self.captureRunning = False
            self.captureThread.join()
            self.captureThread = None

    def connect(self):
        """ start/stop the capture thread and update the connection button accordingly"""
        if self.button_connect.text() == 'Connect':
            self.startvideoCaptureThread()
            self.button_connect.setText('Disconnect')
        else:
            self.stopVideoCaptureThread()
            self.button_connect.setText('Connect')

    def videoCapture(self):
        """ Loop of the capture thread
            Use opencv to capture camera frames, treat them and pass them to the main thread """
        self.captureRunning = True

        print('Begin of Thread - videoCapture')
        capture = cv2.VideoCapture(0)

        while self.captureRunning:
            # Capture one frame
            time.sleep(0.05)
            success, frame = capture.read()
            if not success:
                print('[videoCapture] No frame was captured')
                continue

            # Operations on frame
            if self.captureMode == 'edges':
                frame = cv2.Canny(frame, self.cannyEdges[0], self.cannyEdges[1])
            elif self.captureMode == 'gray':
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            elif self.captureMode == 'blur':
                # Convolution by an averaging kernel
                kernelSize = 11
                kernel = np.resize(np.array([1]*kernelSize**2), (kernelSize, kernelSize)) / kernelSize**2
                frameBuffer = deepcopy(frame)
                cv2.filter2D(frameBuffer, -1, kernel, frame, (-1, -1), 0, cv2.BORDER_DEFAULT)

            # Transmit image to GUI
            self.newImageSig.signal.emit(frame)

        # When everything done, release the capture
        capture.release()
        cv2.destroyAllWindows()
        print('End of thread - videoCapture')

    def quit(self):
        """ Stop capture thread and quit application """
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
