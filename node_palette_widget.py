from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QPixmap, QPainter, QDrag
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QScrollArea, QPushButton, QFrame, QFrame, QLineEdit, QSizePolicy
from constants import *


class NodePaletteWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.y_layout = QVBoxLayout()
        self.layout = QVBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.textChanged.connect(self.onSearchBarChanged)
        self.search_bar.setPlaceholderText('Search ...')
        self.search_bar.setMaximumWidth(400)
        self.search_bar.setClearButtonEnabled(True)

        self.y_layout.addWidget(self.search_bar)

        # Scrollable area
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_widget.setLayout(self.layout)

        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.y_layout.addWidget(self.scroll_area)

        self.setLayout(self.y_layout)
        self.setMinimumWidth(300)

        self.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Expanding
        )

        self.app = QApplication.instance()
        
    def add_node(self, text):
        for node in self.app.nodes:
            if node.label == text:
                return

        widget_count = self.layout.count()
        for i in range(widget_count):
            item = self.layout.itemAt(i).widget()
            if item.text == text:
                return

        widget = NodePaletteNodeWidget(text)
        widget.set_palette_layout(self.layout)
        self.layout.addWidget(widget)

    def onSearchBarChanged(self, text):
        widget_count = self.layout.count()
        for i in range(widget_count):
            item = self.layout.itemAt(i).widget()
            if text in item.text:
                item.setVisible(True)
            else:
                item.setVisible(False)

    def load_topics(self):
        topics = self.app.load_topic_list()
        for topic in topics:
            self.add_node(topic)
            
class NodePaletteNodeWidget(QFrame):
    def __init__(self, text):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.setAutoFillBackground(False)
        self.text = text
        self.layout = QVBoxLayout()
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(NODE_WIDGET_MAX_LABEL_WIDTH)
        self.setMaximumHeight(NODE_WIDGET_MAX_WIDGET_HEIGHT)
        self.label.setAutoFillBackground(False)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.current_pen = NODE_WIDGET_PEN_NORMAL
        self.current_brush = NODE_WIDGET_BRUSH_NORMAL

    def set_palette_layout(self, layout):
        self.palette_layout = layout

    def remove(self):
        self.palette_layout.removeWidget(self)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        painter.setPen(self.current_pen)
        painter.setBrush(self.current_brush)

        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.drawRoundedRect(rect, NODE_WIDGET_CORNER_RADIUS, NODE_WIDGET_CORNER_RADIUS)

        super().paintEvent(event)

    
    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.exec(Qt.DropAction.MoveAction)
