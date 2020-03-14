import cv2
import numpy as np
import os
import sys
import time
from atom import Element
from atom.messages import LogLevel
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QLabel, QMainWindow, QToolBar, QPushButton, QSizePolicy
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
    img = None

    def run(self):
        """
        Gets the latest data from the current stream and sends it to be displayed on the main window.
        """
        global stream
        last_set = time.time()
        is_array = False #    default, can be overriden by stream
        #    tracks whether streaming was active in the last iteration of the while loop below
        was_streaming = False
        last_element_name = None
        last_stream_name = None

        while True:
            if stream:
                _, element_name, stream_name = stream.split(":")
                if element_name != last_element_name or stream_name != last_stream_name:
                    was_streaming = False
                    last_element_name = element_name
                    last_stream_name = stream_name
                if not was_streaming: #    ensure we render the most recent frame
                    data = element.entry_read_n(element_name, stream_name, 1)
                    was_streaming = True
                else: #    block and render the next new frame
                    data = element.entry_read_since(
                        element_name,
                        stream_name,
                        last_id="$",
                        n=1,
                        block=int(1/self.hz * 1000),
                        serialization=None,
                        force_serialization=False,
                    )
                if len(data) == 0: #    if stream is empty or wasn't updated in time
                    continue
                try:
                    # Format binary data to be an image readable by pyqt
                    if "is_array" in data[0]:
                        is_array = bool(int(data[0]["is_array"]))
                    if not is_array:
                        img = cv2.imdecode(np.frombuffer(data[0]["data"], dtype=np.uint8), -1)
                    else:
                        img = data[0]["data"]
                    for size in img.shape:
                        if size > self.max_size:
                            error_msg = "Selected stream has image too large to display!"
                            element.log(LogLevel.ERR, error_msg)
                            raise Exception(error_msg)
                    if len(img.shape) == 3:
                        self.img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    if img.dtype != np.uint8:
                        self.img = (img / img.max() * 255).astype(np.uint8)
                except Exception as e:
                    element.log(LogLevel.ERR, str(e))
                    self.img = cv2.cvtColor(cv2.imread(LOGO_PATH, -1), cv2.COLOR_BGR2RGB)
                qimg = array2qimage(self.img)
                self.change_pixmap.emit(qimg)
            elif was_streaming: #   if transitioned from streaming to not streaming
                self.img = cv2.cvtColor(cv2.imread(LOGO_PATH, -1), cv2.COLOR_BGR2RGB)
                qimg = array2qimage(self.img)
                self.change_pixmap.emit(qimg)
                was_streaming = False
                last_element_name = None
                last_stream_name = None
            #   throttle the rendering rate
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

        # Create save image button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_image)
        spacer = QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)
        toolbar.addWidget(self.save_button)

        # Creates the stream thread that will get data from Atom and send it here
        self.stream_thread = StreamThread(self)
        self.stream_thread.change_pixmap.connect(self.set_img)
        self.stream_thread.start()

        # Creates the combo box thread that will notify this window of when to reupdate the stream list
        cb_thread = ComboBoxThread(self)
        cb_thread.update_streams.connect(self.update_streams)
        cb_thread.start()

        self.show()

    def save_image(self):
        """
        Saves currently viewed frame to disk.
        """
        fname = time.strftime("%Y%m%d_%H%M%S.png")
        cv2.imwrite(os.path.join("/Pictures", fname), self.stream_thread.img[..., ::-1])
        element.log(LogLevel.INFO, f"Saving image as {fname}")

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
