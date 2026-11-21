from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QPushButton, QApplication, QVBoxLayout, QFrame
from constants import *

class Toolbar(QVBoxLayout):
    def __init__(self, window):
        super().__init__()

        self.app = QApplication.instance()
        self.window = window
        self.scene = window.scene

        button_save = QPushButton()
        button_save.setIcon(ICON_SAVE)
        button_save.setIconSize(SIZE_TOOLBAR_ICON)
        button_save.clicked.connect(self.window.save_graph)
        button_save.setToolTip('Save Graph')
        self.addWidget(button_save)

        button_open = QPushButton()
        button_open.setIcon(ICON_OPEN)
        button_open.setIconSize(SIZE_TOOLBAR_ICON)
        button_open.clicked.connect(self.window.show_open_project_dialog)
        button_open.setToolTip('Open Graph')
        self.addWidget(button_open)

        button_load_topics = QPushButton()
        button_load_topics.setIcon(ICON_LOAD_PALETTE)
        button_load_topics.setIconSize(SIZE_TOOLBAR_ICON)
        button_load_topics.clicked.connect(self.window.node_palette.load_topics)
        button_load_topics.setToolTip('Load Node Palette List')
        self.addWidget(button_load_topics)

        divider = QFrame() 
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        self.addWidget(divider)

        ## Selection

        button_select_all = QPushButton()
        button_select_all.setIcon(ICON_SELECT_ALL)
        button_select_all.setIconSize(SIZE_TOOLBAR_ICON)
        button_select_all.clicked.connect(self.scene.select_all)
        button_select_all.setToolTip('Select All')
        self.addWidget(button_select_all)

        button_select_children = QPushButton()
        button_select_children.setIcon(ICON_SELECT_CHILDREN)
        button_select_children.setIconSize(SIZE_TOOLBAR_ICON)
        button_select_children.clicked.connect(self.scene.select_children)
        button_select_children.setToolTip('Select Children')
        self.addWidget(button_select_children)

        button_select_parents = QPushButton()
        button_select_parents.setIcon(ICON_SELECT_PARENTS)
        button_select_parents.setIconSize(SIZE_TOOLBAR_ICON)
        button_select_parents.clicked.connect(self.scene.select_parents)
        button_select_parents.setToolTip('Select Parents')
        self.addWidget(button_select_parents)

        divider = QFrame() 
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        self.addWidget(divider)

        ## Delete

        button_delete_selection = QPushButton()
        button_delete_selection.setIcon(ICON_DELETE)
        button_delete_selection.setIconSize(SIZE_TOOLBAR_ICON)
        button_delete_selection.clicked.connect(self.scene.delete_selection)
        button_delete_selection.setToolTip('Delete Seleted Nodes')
        self.addWidget(button_delete_selection)

        button_delete_connections = QPushButton()
        button_delete_connections.setIcon(ICON_DELETE_CONNECTIONS)
        button_delete_connections.setIconSize(SIZE_TOOLBAR_ICON)
        button_delete_connections.clicked.connect(self.scene.delete_connections)
        button_delete_connections.setToolTip('Delete Node Connections')
        self.addWidget(button_delete_connections)

        button_merge_nodes = QPushButton()
        button_merge_nodes.setIcon(ICON_MERGE_NODES)
        button_merge_nodes.setIconSize(SIZE_TOOLBAR_ICON)
        button_merge_nodes.clicked.connect(self.scene.merge_nodes)
        button_merge_nodes.setToolTip('Merge Selected Nodes')
        self.addWidget(button_merge_nodes)

        divider = QFrame() 
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        self.addWidget(divider)

        ## Freeze/Lock

        ## TODO: constant naming -> freeze or lock?

        button_freeze_nodes = QPushButton()
        button_freeze_nodes.setIcon(ICON_LOCK_NODES)
        button_freeze_nodes.setIconSize(SIZE_TOOLBAR_ICON)
        button_freeze_nodes.clicked.connect(self.scene.freeze_selection)
        button_freeze_nodes.setToolTip('Lock Selected Nodes')
        self.addWidget(button_freeze_nodes)

        button_unfreeze_nodes = QPushButton()
        button_unfreeze_nodes.setIcon(ICON_UNLOCK_NODES)
        button_unfreeze_nodes.setIconSize(SIZE_TOOLBAR_ICON)
        button_unfreeze_nodes.clicked.connect(self.scene.unfreeze_selection)
        button_unfreeze_nodes.setToolTip('Unlock Selected Nodes')
        self.addWidget(button_unfreeze_nodes)

        divider = QFrame() 
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        self.addWidget(divider)


        ## Align and Distribute
        
        button_arrange_square = QPushButton()
        button_arrange_square.setIcon(ICON_ARRANGE_SQUARE)
        button_arrange_square.setIconSize(SIZE_TOOLBAR_ICON)
        button_arrange_square.clicked.connect(self.scene.arrange_square)
        button_arrange_square.setToolTip('Arrange as Square')
        self.addWidget(button_arrange_square)

        button_arrange_by_number_of_parents = QPushButton()
        button_arrange_by_number_of_parents.setIcon(ICON_ARRANGE_BY_PARENT_COUNT)
        button_arrange_by_number_of_parents.setIconSize(SIZE_TOOLBAR_ICON)
        button_arrange_by_number_of_parents.clicked.connect(self.scene.arrange_by_number_of_parents)
        button_arrange_by_number_of_parents.setToolTip('Arrange by Number of Parents')
        self.addWidget(button_arrange_by_number_of_parents)

        button_align_horizontal = QPushButton()
        button_align_horizontal.setIcon(ICON_ALIGN_HORIZONTAL)
        button_align_horizontal.setIconSize(SIZE_TOOLBAR_ICON)
        button_align_horizontal.clicked.connect(self.scene.align_nodes_horizontal)
        button_align_horizontal.setToolTip('Align Horizontal')
        self.addWidget(button_align_horizontal)

        button_align_vertical = QPushButton()
        button_align_vertical.setIcon(ICON_ALIGN_VERTICAL)
        button_align_vertical.setIconSize(SIZE_TOOLBAR_ICON)
        button_align_vertical.clicked.connect(self.scene.align_nodes_vertical)
        button_align_vertical.setToolTip('Align Vertical')
        self.addWidget(button_align_vertical)

        button_distribute_horizontal = QPushButton()
        button_distribute_horizontal.setIcon(ICON_DISTRIBUTE_HORIZONTAL)
        button_distribute_horizontal.setIconSize(SIZE_TOOLBAR_ICON)
        button_distribute_horizontal.clicked.connect(self.scene.distribute_horizontal)
        button_distribute_horizontal.setToolTip('Distribute Horizontal')
        self.addWidget(button_distribute_horizontal)

        button_distribute_vertical = QPushButton()
        button_distribute_vertical.setIcon(ICON_DISTRIBUTE_VERTICAL)
        button_distribute_vertical.setIconSize(SIZE_TOOLBAR_ICON)
        button_distribute_vertical.clicked.connect(self.scene.distribute_vertical)
        button_distribute_vertical.setToolTip('Distribute Vertical')
        self.addWidget(button_distribute_vertical)

        self.addStretch()
