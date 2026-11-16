from PyQt6.QtWidgets import QApplication, QLabel
from constants import *

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
