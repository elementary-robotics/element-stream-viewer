import cv2
import numpy as np
import sys
import time
from atom import Element
from atom.messages import LogLevel
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QLabel, QMainWindow, QToolBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage
from qimage2ndarray import array2qimage

LOGO_PATH = "assets/logo.png"

element = Element("stream-viewer")
stream = ""


class StreamThread(QThread):
    change_pixmap = pyqtSignal(QImage)
    max_size = 8192
    hz = 30

    def run(self):
        """
        Gets the latest data from the current stream and sends it to be displayed on the main window.
        """
        global stream
        last_set = time.time()
        while True:
            if stream:
                _, element_name, stream_name = stream.split(":")
                data = element.entry_read_n(element_name, stream_name, 1)
                try:
                    # Format binary data to be an image readable by pyqt
                    data = data[0]["data"]
                    img = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), -1)
                    for size in img.shape:
                        if size > self.max_size:
                            error_msg = "Selected stream has image too large to display!"
                            element.log(LogLevel.ERR, error_msg)
                            raise Exception(error_msg)
                    if len(img.shape) == 3:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    if img.dtype != np.uint8:
                        img = (img / img.max() * 255).astype(np.uint8)
                except Exception as e:
                    element.log(LogLevel.ERR, str(e))
                    img = cv2.cvtColor(cv2.imread(LOGO_PATH, -1), cv2.COLOR_BGR2RGB)
            else:
                img = cv2.cvtColor(cv2.imread(LOGO_PATH, -1), cv2.COLOR_BGR2RGB)
            qimg = array2qimage(img)
            self.change_pixmap.emit(qimg)
            time.sleep(max(1 / self.hz - (time.time() - last_set), 0))
            last_set = time.time()


class ComboBoxThread(QThread):
    update_streams = pyqtSignal()
    hz = 1

    def run(self):
        """
        Tells the main window to update the list of available streams.
        """
        while True:
            self.update_streams.emit()
            time.sleep(1 / self.hz)


class Inspect(QMainWindow):

    def __init__(self):
        """
        The main window of the application.
        """
        super().__init__()

        self.width = 960
        self.height = 720
        self.resize(self.width, self.height)

        # Creates a window to display the images in
        self.display = QLabel()
        self.display.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.display)

        # Creates a toolbar for displaying the stream combo box
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Creates a combo box that will update the stream global when clicked
        self.streams = ["select a stream"]+ sorted(element.get_all_streams())
        self.stream_selector = QComboBox()
        self.stream_selector.addItems(self.streams)
        self.stream_selector.currentIndexChanged.connect(self.select_stream)
        toolbar.addWidget(self.stream_selector)

        # Creates the stream thread that will get data from Atom and send it here
        stream_thread = StreamThread(self)
        stream_thread.change_pixmap.connect(self.set_img)
        stream_thread.start()

        # Creates the combo box thread that will notify this window of when to reupdate the stream list
        cb_thread = ComboBoxThread(self)
        cb_thread.update_streams.connect(self.update_streams)
        cb_thread.start()

        self.show()

    def select_stream(self, i):
        """
        Updates the stream global variable to the selected stream in the combo box.
        The variable must be global so that the stream thread also has access to it.
        """
        global stream
        if i == 0:
            stream = ""
        else:
            stream = self.streams[i]

    @pyqtSlot()
    def update_streams(self):
        """
        Updates the list of available streams in the combo box if it has changed.
        """
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
                # If we couldn't find the current stream, then we go back to the default
                self.stream_selector.setCurrentIndex(0)

    @pyqtSlot(QImage)
    def set_img(self, qimg):
        """
        Displays the received image in the window.
        """
        self.display.setPixmap(QPixmap.fromImage(qimg))


if __name__ == "__main__":
    app = QApplication([])
    app.setApplicationName("Inspect")
    window = Inspect()
    sys.exit(app.exec_())
