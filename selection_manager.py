from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QVBoxLayout, QLineEdit, QListWidget, QSizePolicy, QInputDialog, QLabel, QSplitter
from constants import *

class SelectionManager(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.stored_selection_dict = {}

        self.app = QApplication.instance()
        self.parent = parent
        self.scene = parent.scene

        self.layout = QVBoxLayout()
        self.current_selection_layout = QVBoxLayout()
        self.stored_selection_layout = QVBoxLayout()

        self.current_selection_list = QListWidget()

        self.search_bar = QLineEdit()
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.textChanged.connect(self.update_stored_selection_list)

        self.stored_selection_list = QListWidget()

        self.stored_selection_list.itemDoubleClicked.connect(
            lambda _: self.on_list_item_double_clicked()
        )

        self.store_selection_button = QPushButton('Store Selection')
        self.store_selection_button.clicked.connect(self.store_selection)

        current_selection_container = QWidget()
        current_selection_container.setLayout(self.current_selection_layout)
        stored_selection_container = QWidget()
        stored_selection_container.setLayout(self.stored_selection_layout)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(current_selection_container)
        splitter.addWidget(stored_selection_container)
        splitter.setChildrenCollapsible(False)

        ## TODO store string constants separately
        self.current_selection_layout.addWidget(QLabel('Current Selection'))
        self.current_selection_layout.addWidget(self.current_selection_list)
        self.current_selection_layout.addWidget(self.store_selection_button)
        #self.stored_selection_layout.addWidget(divider)
        self.stored_selection_layout.addWidget(QLabel('Stored Selections'))
        self.stored_selection_layout.addWidget(self.search_bar)
        self.stored_selection_layout.addWidget(self.stored_selection_list)

        self.layout.addWidget(splitter)
        self.setLayout(self.layout)

        self.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Maximum
        )
        self.adjustSize()
        self.scene.selectionChanged.connect(self.update_current_selection_list)

    def update_current_selection_list(self):
        self.current_selection_list.clear()
        selection = self.scene.get_selection()
        for item in selection:
            self.current_selection_list.addItem(item.widget().node.label)

    def show_text_input_dialog(self, default_text=''):
        text, submit = QInputDialog.getText(self, 'Enter Selection Name', 'Name:', text=default_text)
        if submit:
            return text
        else:
            return ''

    def update_stored_selection_list(self):
        pass

    def store_selection(self, selection_name='', selection=[]):
        print(selection_name)
        if not selection_name or selection_name == '':
            selection_name = self.show_text_input_dialog()

        if selection_name == '':
            return

        if len(selection) == 0:
            selection = self.scene.get_selection()

        self.stored_selection_dict[selection_name] = selection
        self.stored_selection_list.addItem(selection_name)

    def load_selection(self, selection_name):
        if selection_name in self.stored_selection_dict.keys():
            for item in self.scene.get_selection():
                item.setSelected(False)
            for item in self.stored_selection_dict[selection_name]:
                item.setSelected(True)

    def on_list_item_double_clicked(self):
        item = self.stored_selection_list.currentItem()

        if item is not None:
            self.load_selection(item.text())
