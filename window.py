from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QToolBar
import sys

class Window(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PyQt App")
        self.setFixedSize(QSize(800, 600))

        toolbar = QToolBar(parent=self)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        open_file_btn = QAction("Open file", self)
        open_file_btn.setStatusTip("Open file")
        open_file_btn.triggered.connect(self.toolbar_open_file_btn_clicked)
        toolbar.addAction(open_file_btn)

        AND_PIXMAP = QPixmap("./symbols/AND_ANSI.png")
        drag1 = DraggableNode("Drag this", self)
        drag1.setPixmap(AND_PIXMAP)
        drag1.setGeometry(200, 100, AND_PIXMAP.size().width(), AND_PIXMAP.size().height())


        return

    def toolbar_open_file_btn_clicked(self, s) -> None:
        print("click ", s)

class DraggableNode(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.is_moving = False
        self.move_pos = None

    def mousePressEvent(self, ev):
        if ev is not None and ev.buttons() == Qt.MouseButton.LeftButton:
            print("Left Click")
            self.is_moving = True
            self.move_pos = ev.globalPosition()
        super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev):
        if ev is not None and ev.buttons() == Qt.MouseButton.LeftButton:
            if self.is_moving and self.move_pos is not None:
                delta = ev.globalPosition() - self.move_pos
                self.move(self.x() + int(delta.x()), self.y() + int(delta.y()))
                print("Moving", delta, " ", self.move_pos)
                self.move_pos = ev.globalPosition()
        super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev):
        if ev is not None and ev.button() == Qt.MouseButton.LeftButton:
            self.is_moving = False
        super().mouseReleaseEvent(ev)
