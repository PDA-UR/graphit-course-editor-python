from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox, QSizePolicy

class OpenProjectDialog(QDialog):
    def __init__(self, projects, parent=None):
        super().__init__()

        self.setWindowTitle("Open Project")
        #self.setMinimumWidth(300)

        self.selected_project = None

        layout = QVBoxLayout(self)

        self.project_list = QListWidget()
        self.project_list.addItems(projects)
        layout.addWidget(self.project_list)

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

        # Double-click to open
        self.project_list.itemDoubleClicked.connect(
            lambda _: self.accept()
        )

    def accept(self):
        item = self.project_list.currentItem()

        if item is not None:
            self.selected_project = item.text()
            super().accept()
