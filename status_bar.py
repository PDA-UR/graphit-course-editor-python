from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QHBoxLayout, QWidget, QSizePolicy
from constants import *

class ModeSelectionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        self.layout = QHBoxLayout()

        self.btn_selection_mode = QPushButton()
        self.btn_selection_mode.setIcon(ICON_MODE_SELECTION)
        self.btn_selection_mode.setIconSize(SIZE_TOOLBAR_ICON)
        self.btn_selection_mode.setCheckable(True)
        self.btn_selection_mode.setToolTip('Selection Mode')
        self.btn_selection_mode.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.btn_selection_mode.clicked.connect(self.selection_mode_button_clicked)
        self.btn_selection_mode.setChecked(True)

        self.btn_connection_mode = QPushButton()
        self.btn_connection_mode.setIcon(ICON_MODE_CONNECTION)
        self.btn_connection_mode.setIconSize(SIZE_TOOLBAR_ICON)
        self.btn_connection_mode.setCheckable(True)
        self.btn_connection_mode.setToolTip('Connection Mode')
        self.btn_connection_mode.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.btn_connection_mode.clicked.connect(self.connection_mode_button_clicked)

        self.btn_cut_mode = QPushButton()
        self.btn_cut_mode.setIcon(ICON_MODE_CUT)
        self.btn_cut_mode.setIconSize(SIZE_TOOLBAR_ICON)
        self.btn_cut_mode.setCheckable(True)
        self.btn_cut_mode.setToolTip('Cut Mode')
        self.btn_cut_mode.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.btn_cut_mode.clicked.connect(self.cut_mode_button_clicked)

        self.layout.addWidget(self.btn_selection_mode)
        self.layout.addWidget(self.btn_connection_mode)
        self.layout.addWidget(self.btn_cut_mode)
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.app.mode_changed.connect(self.modeChangedEvent)

    def selection_mode_button_clicked(self):
        self.btn_selection_mode.setChecked(True)
        self.btn_connection_mode.setChecked(False)
        self.btn_cut_mode.setChecked(False)
        self.app.MODE = self.app.MODE_SELECTION

        # hacky, but we want no callback loops
        self.app.mode_changed.disconnect(self.modeChangedEvent)
        self.app.mode_changed.emit()
        self.app.mode_changed.connect(self.modeChangedEvent)

    def connection_mode_button_clicked(self):
        self.btn_selection_mode.setChecked(False)
        self.btn_connection_mode.setChecked(True)
        self.btn_cut_mode.setChecked(False)
        self.app.MODE = self.app.MODE_CONNECTION

        self.app.mode_changed.disconnect(self.modeChangedEvent)
        self.app.mode_changed.emit()
        self.app.mode_changed.connect(self.modeChangedEvent)

    def cut_mode_button_clicked(self):
        self.btn_selection_mode.setChecked(False)
        self.btn_connection_mode.setChecked(False)
        self.btn_cut_mode.setChecked(True)
        self.app.MODE = self.app.MODE_CUT

        self.app.mode_changed.disconnect(self.modeChangedEvent)
        self.app.mode_changed.emit()
        self.app.mode_changed.connect(self.modeChangedEvent)

    def modeChangedEvent(self):
        if self.app.MODE == self.app.MODE_SELECTION:
            self.btn_selection_mode.setChecked(True)
            self.btn_connection_mode.setChecked(False)
            self.btn_cut_mode.setChecked(False)
        elif self.app.MODE == self.app.MODE_CONNECTION:
            self.btn_selection_mode.setChecked(False)
            self.btn_connection_mode.setChecked(True)
            self.btn_cut_mode.setChecked(False)
        elif self.app.MODE == self.app.MODE_CUT:
            self.btn_selection_mode.setChecked(False)
            self.btn_connection_mode.setChecked(False)
            self.btn_cut_mode.setChecked(True)

class ModeWidget(QLabel):
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        self.setText(f'Mode: {self.app.MODE}')
        self.app.mode_changed.connect(self.modeChangedEvent)
        #self.scene = window.scene

    def modeChangedEvent(self):
        self.setText(f'Mode: {self.app.MODE}')

## TODO: not updated when node is created, only when another scene event happens
class NodeCounterWidget(QLabel):
    def __init__(self, window):
        super().__init__()
        self.app = QApplication.instance()
        self.scene = window.scene
        self.setText(f'Total Nodes: {len(self.app.nodes)} ({len(self.scene.selectedItems())} selected)')
        #app.mode_changed.connect(self.modeChangedEvent)
        self.app.node_created.connect(self.node_count_changed_event)
        self.app.node_deleted.connect(self.node_count_changed_event)
        self.scene.selectionChanged.connect(self.node_count_changed_event)

    def node_count_changed_event(self):
        self.setText(f'Total Nodes: {len(self.app.nodes)} ({len(self.scene.selectedItems())} selected)')
