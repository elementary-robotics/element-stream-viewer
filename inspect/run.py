import cv2
import numpy as np
import sys
import time
from atom import Element
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QLabel
from PyQt5.QtWidgets import QMainWindow, QStatusBar, QToolBar
from PyQt5.QtCore import QSize, QRect, Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage
from qimage2ndarray import array2qimage

LOGO_PATH = "assets/logo.png"

element = Element("inspect")
stream = ""


class StreamThread(QThread):
    change_pixmap = pyqtSignal(QImage)
    max_fps = 30

    def run(self):
        global stream
        last_set = time.time()
        while True:
            if stream:
                _, element_name, stream_name = stream.split(":")
                data = element.entry_read_n(element_name, stream_name, 1)
                try:
                    data = data[0]["data"]
                    img = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), -1)
                    if len(img.shape) == 3:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    if img.dtype != np.uint8:
                        img = (img / img.max() * 255).astype(np.uint8)
                except:
                    img = cv2.cvtColor(cv2.imread(LOGO_PATH, -1), cv2.COLOR_BGR2RGB)
            else:
                img = cv2.cvtColor(cv2.imread(LOGO_PATH, -1), cv2.COLOR_BGR2RGB)
            qimg = array2qimage(img)
            self.change_pixmap.emit(qimg)
            time.sleep(1 / self.max_fps - (time.time() - last_set))
            last_set = time.time()


class ComboBoxThread(QThread):
    update_streams = pyqtSignal()

    def run(self):
        while True:
            self.update_streams.emit()
            time.sleep(1)


class Inspect(QMainWindow):

    def __init__(self):
        super().__init__()
        self.streams = ["select a stream"]+ sorted(element.get_all_streams())

        self.width = 960
        self.height = 720
        self.resize(self.width, self.height)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        toolbar = QToolBar()
        self.addToolBar(toolbar)

        self.display = QLabel()
        self.display.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.display)

        self.stream_selector = QComboBox()
        self.stream_selector.addItems(self.streams)
        self.stream_selector.currentIndexChanged.connect(self.select_stream)
        toolbar.addWidget(self.stream_selector)

        stream_thread = StreamThread(self)
        stream_thread.change_pixmap.connect(self.set_img)
        stream_thread.start()

        cb_thread = ComboBoxThread(self)
        cb_thread.update_streams.connect(self.update_streams)
        cb_thread.start()

        self.show()

    def select_stream(self, i):
        global stream
        if i == 0:
            stream = ""
        else:
            stream = self.streams[i]

    @pyqtSlot()
    def update_streams(self):
        updated_streams = ["select a stream"]+ sorted(element.get_all_streams())
        if updated_streams != self.streams:
            self.streams = updated_streams
            current_stream = self.stream_selector.currentText()
            self.stream_selector.clear()
            self.stream_selector.addItems(self.streams)
            try:
                current_index = self.streams.index(current_stream)
                self.stream_selector.setCurrentIndex(current_index)
            except ValueError:
                self.stream_selector.setCurrentIndex(0)

    @pyqtSlot(QImage)
    def set_img(self, qimg):
        self.display.setPixmap(QPixmap.fromImage(qimg))


if __name__ == "__main__":
    app = QApplication([])
    app.setApplicationName("Inspect")
    window = Inspect()
    sys.exit(app.exec_())
