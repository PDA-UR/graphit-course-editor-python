from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QColorDialog, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit, QTableView, QHeaderView, QCheckBox, QInputDialog, QMenu
from PyQt6.QtCore import Qt, QSortFilterProxyModel
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from constants import *

# from ChatGPT
class NodeListWidget(QWidget):
    def __init__(self, view):
        super().__init__()

        self.app = QApplication.instance()
        self.view = view

        self.nodes = []

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search nodes...")
        self.search_bar.setClearButtonEnabled(True)

        self.show_isolated_checkbox = QCheckBox("Show Isolated Nodes")

        # Source model
        self.model = QStandardItemModel(0, 3, self)
        self.model.setHorizontalHeaderLabels([
            "Node",
            "Parents",
            "Children"
        ])

        # Sorting and filtering proxy
        self.proxy_model = NodeFilterModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterKeyColumn(0)
        self.proxy_model.setFilterCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )

        # Table
        self.table = QTableView()
        self.table.setModel(self.proxy_model)
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QTableView.SelectionMode.SingleSelection
        )
        self.table.setEditTriggers(
            QTableView.EditTrigger.NoEditTriggers
        )
        self.table.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.table.customContextMenuRequested.connect(
            self.showContextMenu
        )

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.search_bar)
        layout.addWidget(self.show_isolated_checkbox)
        layout.addWidget(self.table)

        # Signals
        self.search_bar.textChanged.connect(
            self.proxy_model.setFilterFixedString
        )

        self.table.doubleClicked.connect(
            self.onDoubleClick
        )

        self.show_isolated_checkbox.toggled.connect(
            #self.proxy_model_isolated.setShowIsolatedOnly
            self.proxy_model.setShowIsolatedOnly
        )

        self.app.node_created.connect(self.update_nodes)
        self.app.node_deleted.connect(self.update_nodes)

    def update_nodes(self):
        #print('update nodes')
        self.model.setRowCount(0)

        for node in self.app.nodes:
            parent_count = len(node.get_connections_incoming())
            child_count = len(node.get_connections_outgoing())

            #print(parent_count, child_count)

            name_item = QStandardItem(str(node.label))
            parent_item = QStandardItem(str(parent_count))
            child_item = QStandardItem(str(child_count))

            # Store the actual node object on the first item
            name_item.setData(node, Qt.ItemDataRole.UserRole)
            name_item.setToolTip(str(node.label))

            # Right-align numeric columns
            parent_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            child_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.model.appendRow([
                name_item,
                parent_item,
                child_item
            ])

    # from ChatGPT
    def showContextMenu(self, pos):
        index = self.table.indexAt(pos)

        if not index.isValid():
            return

        self.table.selectRow(index.row())

        menu = QMenu(self)

        rename_action = menu.addAction("Rename")

        action = menu.exec(
            self.table.viewport().mapToGlobal(pos)
        )

        if action == rename_action:
            self.renameNode(index)

    # from ChatGPT
    def renameNode(self, proxy_index):
        # Map proxy index to source model
        source_index = self.proxy_model.mapToSource(proxy_index)

        # Always retrieve the node from column 0
        node_index = self.model.index(source_index.row(), 0)

        node = node_index.data(Qt.ItemDataRole.UserRole)

        if node is None:
            return

        new_name, accepted = QInputDialog.getText(
            self,
            "Rename Node",
            "New Label:",
            text=node.label
        )

        if not accepted:
            return

        new_name = new_name.strip()

        if not new_name:
            return

        # Update the actual node
        #node.label = new_name
        node.set_name(new_name)

        # Update the model
        self.model.setData(
            node_index,
            new_name,
            Qt.ItemDataRole.DisplayRole
        )

        #node.widget.node.set_name(new_name)

    def onDoubleClick(self, proxy_index):
        source_index = self.proxy_model.mapToSource(proxy_index)

        node = self.model.item(
            source_index.row(), 0
        ).data(Qt.ItemDataRole.UserRole)

        if node is not None:
            self.view.centerOn(node.widget.scene_widget)

# from ChatGPT
class NodeFilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.show_isolated_only = False

    def setShowIsolatedOnly(self, enabled):
        self.show_isolated_only = enabled
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()

        # Check isolated-node condition
        if self.show_isolated_only:
            parents = int(model.index(source_row, 1, source_parent).data())
            children = int(model.index(source_row, 2, source_parent).data())

            if parents > 0 or children > 0:
                return False

        # Preserve normal text filtering
        return super().filterAcceptsRow(source_row, source_parent)
