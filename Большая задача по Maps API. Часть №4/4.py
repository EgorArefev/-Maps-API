import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class MainWindow(QMainWindow):
    pres_delta = 0.1

    def _init_(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("untitled1.ui", self)
        self.press_delta = 0.00001

        self.map_zoom = 6
        self.map_ll = [37.977751, 55.757718]
        self.map_l = "map"
        self.map_key = ""

        self.g_search.returnPressed.connect(self.search)
        self.g_layer1.clicked.connect(self.set_layer)
        self.g_layer2.clicked.connect(self.set_layer)
        self.g_layer3.clicked.connect(self.set_layer)

        self.refresh_map()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp and self.map_zoom < 17:
            self.map_zoom += 1
        elif event.key() == Qt.Key_PageDown and self.map_zoom > 0:
            self.map_zoom -= 1
        elif event.key() == Qt.Key_Up:
            self.map_ll[1] += self.pres_delta
        elif event.key() == Qt.Key_Down:
            self.map_ll[1] -= self.pres_delta
        elif event.key() == Qt.Key_Left:
            self.map_ll[0] -= self.pres_delta
        elif event.key() == Qt.Key_Right:
            self.map_ll[0] += self.pres_delta
        elif event.key() == Qt.Key_Escape:
            self.g_map.setFocus()
        self.refresh_map()

    def refresh_map(self):
        map_params = {
            "ll": ",".join(map(str, self.map_ll)),
            "l": self.map_l,
            "z": self.map_zoom
        }
        session = requests.Session()
        retry = Retry(total=10, connect=5, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        response = session.get("https://static-maps.yandex.ru/1.x/",
                               params=map_params)
        with open("tmp.png", mode="wb") as tmp:
            tmp.write(response.content)
        pixmap = QPixmap()
        pixmap.load("tmp.png")
        self.g_map.setPixmap(pixmap)

    def set_layer(self):
        snd = self.sender().text()
        if snd == "Спутник":
            self.map_l = "sat"
        elif snd == "Схема":
            self.map_l = "map"
        else:
            self.map_l = "sat,skl"
        self.refresh_map()


def clip(v, _min, _max):
    if v < _min:
        return _min
    if v > _max:
        return _max
    return v


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())