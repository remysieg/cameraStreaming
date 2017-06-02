import sys
import inspect
import numpy as np
from threading import Thread, Lock

import time
import cv2
from PySide import QtCore, QtGui

SCREEN_RESOLUTION = [1920, 1080]
VIDEO_RESOLUTION = [640, 480]


class QtSignal(QtCore.QObject):
    signal = QtCore.Signal(object)


class Interface(QtGui.QWidget):

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

        self.iniUI()

    def iniUI(self):
        self.setGeometry((SCREEN_RESOLUTION[0]-self.size[0])/2,
                         (SCREEN_RESOLUTION[1]-self.size[1])/2,
                         self.size[0], self.size[1])
        self.setWindowTitle('Camera')

        button_quit = QtGui.QPushButton('Quit', self)
        button_quit.setGeometry(10, 10, 100, 30)
        QtCore.QObject.connect(button_quit, QtCore.SIGNAL('clicked()'), self.quit)

        self.button_connect = QtGui.QPushButton('Connect', self)
        self.button_connect.setGeometry(10, 50, 100, 30)
        QtCore.QObject.connect(self.button_connect, QtCore.SIGNAL('clicked()'), self.connect)

        checkboxeGroup_mode = QtGui.QButtonGroup(self)
        checkboxeGroup_mode.setObjectName('Treatment')

        checkbox_raw = QtGui.QCheckBox('Raw image', self)
        checkbox_raw.setChecked(True)
        checkbox_raw.setGeometry(10, 130, 100, 30)
        QtCore.QObject.connect(checkbox_raw, QtCore.SIGNAL('stateChanged(int)'), self.updateMode)
        checkboxeGroup_mode.addButton(checkbox_raw)

        checkbox_gray = QtGui.QCheckBox('Gray image', self)
        checkbox_gray.setGeometry(10, 170, 100, 30)
        QtCore.QObject.connect(checkbox_raw, QtCore.SIGNAL('stateChanged(int)'), self.updateMode)
        checkboxeGroup_mode.addButton(checkbox_gray)

        checkbox_edges = QtGui.QCheckBox('Canny edges detection', self)
        checkbox_edges.setGeometry(10, 210, 100, 30)
        checkboxeGroup_mode.addButton(checkbox_edges)
        QtCore.QObject.connect(checkbox_raw, QtCore.SIGNAL('stateChanged(int)'), self.updateMode)

        self.modeCheckBoxes = {'raw': checkbox_raw, 'gray': checkbox_gray, 'edges': checkbox_edges}

        self.label_image = QtGui.QLabel(self)
        self.label_image.setGeometry(120, 10, 640, 480)

        self.show()

    def updateMode(self):
        for mode, checkbox in self.modeCheckBoxes.items():
            if checkbox.checkState():
                self.captureMode = mode

    def updateImage(self, frame):
        # FIXME: create cases for other modes
        if self.captureMode == 'raw':
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QtGui.QImage(frame, frame.shape[1], frame.shape[0], frame.shape[1]*3,
                                 QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap(image)
            self.label_image.setPixmap(pixmap)
        else:
            print 'This mode does not work for now'

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

        print 'Begin of Thread - videoCapture'
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

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # When everything done, release the capture
        capture.release()
        cv2.destroyAllWindows()
        print 'End of thread - videoCapture'

    def quit(self):
        self.stopVideoCaptureThread()
        quit()


def main():
    app = QtGui.QApplication(sys.argv)
    interface = Interface()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()