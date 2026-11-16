from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QColor, QBrush, QPen

PROJECTS_PATH = 'projects'

ALIGN_TO_MEAN = 'align_to_mean'
ALIGN_TO_FIRST = 'align_to_first'

SIZE_TOOLBAR_ICON = QSize(32, 32)
#SIZE_TOOLBAR_ICON = QSize(64, 64)
ICON_PLACEHOLDER = QIcon('icons/placeholder.svg')
ICON_ALIGN_HORIZONTAL = QIcon('icons/align_horizontal.svg')
ICON_ALIGN_VERTICAL = QIcon('icons/align_vertical.svg')
ICON_DISTRIBUTE_HORIZONTAL = QIcon('icons/distribute_horizontal.svg')
ICON_DISTRIBUTE_VERTICAL = QIcon('icons/distribute_vertical.svg')
ICON_ARRANGE_SQUARE = QIcon('icons/arrange_square.svg')
ICON_SAVE = QIcon('icons/save.svg')
ICON_OPEN = QIcon('icons/open.svg')
ICON_LOAD_PALETTE = QIcon('icons/open_list.svg')
ICON_SELECT_CHILDREN = QIcon('icons/select_children_simple.svg')
ICON_SELECT_PARENTS = QIcon('icons/select_parents_simple.svg')
ICON_SELECT_ALL = QIcon('icons/select_all.svg')
ICON_SELECT_GROW = QIcon('icons/select_grow.svg')
ICON_SELECT_SHRINK = QIcon('icons/select_shrink.svg')
ICON_DELETE = QIcon('icons/delete.svg')
ICON_DELETE_CONNECTIONS = QIcon('icons/delete_connections.svg')
ICON_MERGE_NODES = QIcon('icons/merge.svg')
ICON_LOCK_NODES = QIcon('icons/lock.svg')
ICON_UNLOCK_NODES = QIcon('icons/unlock.svg')


NODE_WIDGET_MAX_LABEL_WIDTH = 300
NODE_WIDGET_MAX_WIDGET_HEIGHT = 100
NODE_WIDGET_PEN_NORMAL = QPen(QColor('#383c4a'), 2, Qt.PenStyle.SolidLine)
NODE_WIDGET_BRUSH_NORMAL = QBrush(QColor('#636d83'))
NODE_WIDGET_CORNER_RADIUS = 20
