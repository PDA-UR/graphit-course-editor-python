from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox, QSizePolicy, QLineEdit

class ListDialog(QDialog):
    def __init__(self, list_elements, title='Select Item', allow_custom=False, parent=None):
        super().__init__()

        self.setWindowTitle(title)
        #self.setMinimumWidth(300)

        self.allow_custom = allow_custom
        self.selected_text = ''

        layout = QVBoxLayout(self)

        self.dialog_list = QListWidget()
        self.dialog_list.addItems(list_elements)

        if len(list_elements) > 0:
            self.selected_text = list_elements[0]

        self.custom_text_entry = QLineEdit(self.selected_text)

        layout.addWidget(self.dialog_list)
        if allow_custom:
            layout.addWidget(self.custom_text_entry)
        else:
            self.custom_text_entry.setVisible(False)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Open |
            QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        self.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Maximum
        )
        self.adjustSize()

        self.custom_text_entry.textChanged.connect(self.on_custom_text_changed)
        self.dialog_list.currentItemChanged.connect(self.on_current_list_item_changed)
        self.dialog_list.itemDoubleClicked.connect(self.on_list_item_double_clicked)

    def on_custom_text_changed(self):
        self.selected_text = self.custom_text_entry.text()

    def on_current_list_item_changed(self):
        item = self.dialog_list.currentItem()

        if item is not None:
            self.selected_text = item.text()
            self.custom_text_entry.setText(self.selected_text)

    def on_list_item_double_clicked(self):
        item = self.dialog_list.currentItem()

        if item is not None:
            self.selected_text = item.text()
            self.accept()

    def accept(self):
        super().accept()

        #item = self.dialog_list.currentItem()

        #if item is not None:
        #    self.selected_item = item.text()
        #    super().accept()
