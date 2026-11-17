from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QVBoxLayout, QLineEdit, QListWidget, QSizePolicy, QInputDialog
from constants import *

class SelectionManager(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.selection_dict = {}

        self.app = QApplication.instance()
        self.parent = parent
        self.scene = parent.scene

        self.layout = QVBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.textChanged.connect(self.update_selection_list)


        self.selection_list = QListWidget()

        self.selection_list.itemDoubleClicked.connect(
            lambda _: self.on_list_item_double_clicked()
        )

        self.store_selection_button = QPushButton('Store Selection')
        self.store_selection_button.clicked.connect(self.store_selection)

        self.layout.addWidget(self.search_bar)
        self.layout.addWidget(self.selection_list)
        self.layout.addWidget(self.store_selection_button)

        self.setLayout(self.layout)

        self.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Maximum
        )
        self.adjustSize()

    def show_text_input_dialog(self, default_text=''):
        text, submit = QInputDialog.getText(self, 'Enter Selection Name', 'Name:', text=default_text)
        if submit:
            return text
        else:
            return ''

    def update_selection_list(self):
        pass

    def store_selection(self, selection_name=''):
        print(selection_name)
        if not selection_name or selection_name == '':
            selection_name = self.show_text_input_dialog()

        if selection_name == '':
            return

        self.selection_dict[selection_name] = self.scene.get_selection()
        self.selection_list.addItem(selection_name)

    def load_selection(self, selection_name):
        if selection_name in self.selection_dict.keys():
            for item in self.scene.get_selection():
                item.setSelected(False)
            for item in self.selection_dict[selection_name]:
                item.setSelected(True)

    def on_list_item_double_clicked(self):
        item = self.selection_list.currentItem()

        if item is not None:
            self.load_selection(item.text())
