import sys
import numpy as np
from threading import Thread, Lock

import cv2
from PySide import QtCore, QtGui

SCREEN_RESOLUTION = [1920, 1080]


class Interface(QtGui.QWidget):

    def __init__(self):
        super(Interface, self).__init__()
        self.size = [800, 600]
        self.button_connect = None

        self.captureThread = None
        self.captureRunning = False

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

        self.show()

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
            success, frame = capture.read()

            # Operations on frame
            edges = cv2.Canny(frame, 100, 200)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Display the frame
            # cv2.imshow('frame', frame)
            cv2.imshow('Canny edges detection', edges)
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