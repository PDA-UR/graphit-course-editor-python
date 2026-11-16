from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QColorDialog, QPushButton, QVBoxLayout
#from main import DraggableProxyWidget
from constants import *

class ColorButton(QWidget):
    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)

        self.color = color

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

        self.setMinimumWidth(SIZE_TOOLBAR_ICON.width())
        self.setMinimumHeight(SIZE_TOOLBAR_ICON.height())

        self.app = QApplication.instance()

    def mousePressEvent(self, event):
        selection = self.app.window.scene.selectedItems()

        for widget in selection:
            ## TODO: Workaround
            #if isinstance(widget, DraggableProxyWidget):
            try:
                widget.widget().node.set_color(self.color)
            except:
                continue

class StylePaletteWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.COLOR_GRID_NUM_COMUMNS = 4
        self.color_list = []

        self.color_grid_layout = QGridLayout()

        self.color_grid_index_row = 0
        self.color_grid_index_column = 0

        # TODO: move default color palette to config file?
        self.add_color('#CC0000')
        self.add_color('#4E9A06')
        self.add_color('#C4A000')
        self.add_color('#3465A4')
        self.add_color('#75507B')
        self.add_color('#06989A')
        self.add_color('#D3D7CF')
        self.add_color('#555753')
        self.add_color('#ef2929')
        self.add_color('#8AE234')
        self.add_color('#FCE94F')
        self.add_color('#729FCF')
        self.add_color('#AD7FA8')
        self.add_color('#34E2E2')
        self.add_color('#EEEEEC')

        self.button_add_custom_color = QPushButton('Add custom color...')
        self.button_add_custom_color.clicked.connect(self.show_custom_color_dialog)

        ## TODO: functionality to modify node size

        ## TODO: functionality to add custom metadata

        self.layout.addLayout(self.color_grid_layout)
        self.layout.addWidget(self.button_add_custom_color)
        self.layout.addStretch()
        self.setLayout(self.layout)
        self.app = QApplication.instance()

    def add_color(self, color_code: str):
        self.color_list.append(color_code)

        self.color_grid_layout.addWidget(ColorButton(color_code),
                                         self.color_grid_index_row,
                                         self.color_grid_index_column)

        self.color_grid_index_column += 1

        if self.color_grid_index_column >= self.COLOR_GRID_NUM_COMUMNS:
            self.color_grid_index_row += 1
            self.color_grid_index_column = 0

    def show_custom_color_dialog(self):
        color = QColorDialog.getColor()
        color_code = color.name()
        self.add_color(color_code)
