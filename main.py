from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPointF, QLineF, QPoint, QMimeData, QRectF
from PyQt6.QtGui import QPixmap, QPalette, QColor, QBrush, QPen, QPainter, QWheelEvent, QKeyEvent, QMouseEvent, QDrag, QIcon, QCursor, QTransform, QLinearGradient, QPainterPath
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QVBoxLayout, QComboBox, QHBoxLayout, QScrollArea, QPushButton, QFrame, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem, QGraphicsProxyWidget, QInputDialog, QGraphicsLineItem, QFrame, QStackedLayout, QGridLayout, QLineEdit, QSizePolicy, QSpacerItem, QSplitter, QTabWidget, QColorDialog, QFileDialog, QDialog
import sys
import os
import pandas as pd
import numpy as np
from constants import *
from toolbar import Toolbar
from style_palette_widget import StylePaletteWidget, ColorButton
from node_palette_widget import NodePaletteWidget, NodePaletteNodeWidget 
from status_bar import ModeWidget, NodeCounterWidget, ModeSelectionWidget
from project_manager import OpenProjectDialog
from node_list_widget import NodeListWidget

""" TODO

 * identify satellites
 * move node with single connection to parent
 * select all connected nodes with single connection
 * "arrange as subgraph"
 * groups: create, select, freeze, unfreeze
 * proper localization
 * dedicated config file
 * project files
 * modifier + click to select subgraph
 * drag/drop (or paste) text directly as nodes
   * warning if long text is pasted
 * snap to grid
 * in case of performance issues: use more efficient way to handle connections
   * (we currently have a central list of all connection which we iterate over)
   * central DataFrame for vectorized filtering
   * nodes handle their own connections
 * buttons to switch modes via GUI
 * use proper shortcut handling of PyQt6
 * exception handling for cancelled file opening
   * might be obsolete with new "project manager"
 * distribute code to more files
 * lasso selection
   * should be very similar to cut mode?
 * save/restore selection
 * constant naming for lock/freeze feature
 * "Meta Nodes"
   * for things like "belongs to course session"
   * should be able to hide connections
 * proper ID management when nodes get deleted
   * node IDs are assigned in the constructor and incremented
   * upon deletion, there is a gap in the ID list
   * when saving and loading the graph, newly created nodes after loading get wrong IDs as the counter is too low
 * icons for modes

DONE:
 * cut connections
 * highlight connections of selected node
 * connection as color gradient to identify source/sink?
 * show number of nodes/selected nodes in status bar
 * [bug] check file name creation in save function
 * freeze/unfreeze selection

"""

class QGraphApplication(QApplication):
    mode_changed = pyqtSignal()
    node_created = pyqtSignal()
    node_deleted = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(sys.argv)

        self.MODE_SELECTION = 'selection'
        self.MODE_CONNECTION = 'connection'
        self.MODE_CUT = 'cut'
        self.MODE = self.MODE_SELECTION
        self.SELECTION_MODE_RECT = 'rect'
        self.SELECTION_MODE_LASSO = 'lasso'
        self.PATH_SAVE_NODES = 'nodes.csv'
        self.PATH_SAVE_CONNECTIONS = 'connections.csv'
        self.PATH_LOAD_TOPICS = 'topics.txt'
        self.is_connecting = False
        self.connection_buffer = []

        self.nodes = []
        self.connections = []

        self.window = None

        self.cursor_pos = QPointF(0., 0.)

        self.project_name = ''
        self.project_path = ''

        # used for re-mapping node ids
        self.node_id_map = {}


    def connect_nodes(self, source, sink):
        if not self.connection_exists(source, sink):
            connection = Connection(source, sink)
            self.connections.append(connection)

    def connection_exists(self, source, sink):
        for connection in self.connections:
            if connection.source.id == source.id and connection.sink.id == sink.id:
                return True
            # we don't want bidirectional connections, so also check the other way around
            if connection.source.id == sink.id and connection.sink.id == source.id:
                return True
        return False

    def save_graph(self, file_name=''):
        nodes_list = []

        path_nodes = f'{PROJECTS_PATH}/{file_name}/{file_name}_nodes.csv'
        path_connections = f'{PROJECTS_PATH}/{file_name}/{file_name}_connections.csv'

        try:
            if not os.path.exists(f'{PROJECTS_PATH}/{file_name}'):
                os.mkdir(f'{PROJECTS_PATH}/{file_name}')
        except:
            print(f'Project directory "{PROJECTS_PATH}/{file_name}" does not exist and could not be created.')
            return

        for node in self.nodes:
            scene_pos = node.widget.getScenePos()
            nodes_list.append({'id' : node.id,
                               'label' : node.label,
                               'x' : scene_pos.x(),
                               'y' : scene_pos.y(),
                               'color' : node.color})

        df_nodes = pd.DataFrame(nodes_list)

        connections_list = []

        for i, connection in enumerate(self.connections):
            connections_list.append({'id' : i,
                                     'source' : connection.source.id,
                                     'sink' : connection.sink.id})

        df_connections = pd.DataFrame(connections_list)

        df_nodes.to_csv(path_nodes, index=False)
        df_connections.to_csv(path_connections, index=False)

    def get_node_by_id(self, id):
        for node in self.nodes:
            if node.id == id:
                return node
        return None

    def load_nodes(self, path_nodes):
        df_nodes = pd.read_csv(path_nodes)

        self.node_id_map = {}

        for i, row in df_nodes.iterrows():
            id = row.id
            label = row.label
            x = row.x
            y = row.y
            node = Node(label, x, y)
            if node.id != id:
                print(f're-mappig id: {id} -> {node.id}')
                self.node_id_map[id] = node.id
            #node.id = id
            #self.node_created.emit(node)
            self.window.scene.add_node(node)
            node.set_color(row.color)
            if row.color not in self.window.style_palette.color_list:
                self.window.style_palette.add_color(row.color)
        self.node_created.emit()

    def load_connections(self, path_connections):
        try:
            df_connections = pd.read_csv(path_connections)
        except pd.errors.EmptyDataError:
            return

        for i, row in df_connections.iterrows():
            id = row.id

            source_id = row.source
            sink_id = row.sink

            # re-map connection ids
            if source_id in self.node_id_map.keys():
                source_id = self.node_id_map[source_id]
            if sink_id in self.node_id_map.keys():
                sink_id = self.node_id_map[sink_id]

            source = self.get_node_by_id(source_id)
            sink = self.get_node_by_id(sink_id)
            self.connect_nodes(source, sink)
        self.node_created.emit()

    def load_graph(self, path_nodes, path_connections):
        self.load_nodes(path_nodes)
        self.load_connections(path_connections)
        self.node_created.emit()

    def get_cursor_position(self):
        return self.cursor_pos

    def load_topic_list(self):
        topics = []
        topics_path = self.PATH_LOAD_TOPICS
        topics_path = self.window.show_open_file_dialog('Open Node List')
        with open(topics_path, 'r') as f:
            for line in f.readlines():
                topics.append(line.strip())
        return topics

    def cut_connections(self, cut_line):
        connections_to_cut = []
        if len(cut_line) <= 1:
            return

        last_point = cut_line[0]
        for i, point in enumerate(cut_line):
            if i == 0:
                continue
            else:
                # TODO: should probably be done by the viewport before calling this function
                segment = QLineF(QPointF(self.window.view.mapToScene(last_point)), 
                                 QPointF(self.window.view.mapToScene(point)))
                last_point = point

                for connection in self.connections:
                    connection_line = QLineF(connection.widget.line())
                    intersects, intersection_point = connection_line.intersects(segment)
                    # intersection within the segment (in contrast to unbounded which assumes endless lines
                    if intersects == QLineF.IntersectionType.BoundedIntersection:
                        if connection not in connections_to_cut:
                            connections_to_cut.append(connection)

        for connection in connections_to_cut:
            connection.delete()

class Connection():
    def __init__(self, source, sink):
        self.app = QApplication.instance()
        self.window = app.window

        self.source = source
        self.sink = sink
        self.source.widget.on_move.connect(self.on_source_moved)
        self.sink.widget.on_move.connect(self.on_sink_moved)

        p1 = source.get_widget_center()
        p2 = sink.get_widget_center()
        connection_line = ConnectionWidget(self, QLineF(p1, p2))
        connection_line.setZValue(-1)
        self.widget = connection_line
        self.app.window.scene.addItem(self.widget)

    def set_widget(self, widget):
        self.widget = widget

    def on_source_moved(self):
        line = self.widget.line()
        line.setP1(self.source.get_widget_center())
        self.widget.setLine(line)

    def on_sink_moved(self):
        line = self.widget.line()
        line.setP2(self.sink.get_widget_center())
        self.widget.setLine(line)

    def delete(self):
        self.app.connections.remove(self)
        self.app.window.scene.removeItem(self.widget)

    def __repr__(self):
        return f'{self.source.label} ({self.source.id}) --> {self.sink.label} ({self.sink.id})'

class ConnectionWidget(QGraphicsLineItem):
    LINE_GRADIENT_COLOR_SOURCE = QColor(100,100,100)
    LINE_GRADIENT_COLOR_SINK = QColor(200,200,200)
    LINE_GRADIENT_COLOR_SOURCE_SELECTED = QColor(100,0,0)
    LINE_GRADIENT_COLOR_SINK_SELECTED = QColor(250,100,100)
    def __init__(self, connection, line, parent=None):
        super().__init__(line, parent)

        self.pen = QPen(Qt.GlobalColor.black, 2, Qt.PenStyle.SolidLine)
        #self.pen_selected = QPen(Qt.GlobalColor.red, 3, Qt.PenStyle.SolidLine)
        self.setPen(self.pen)

        self.marker_radius = 4

        self.connection = connection

    def paint(self, painter: QPainter, option, widget=None):
        line = self.line()
        start = line.p1()
        end = line.p2()

        painter.save()

        if self.connection.source.widget.scene_widget in self.connection.app.window.scene.selectedItems() or self.connection.sink.widget.scene_widget in self.connection.app.window.scene.selectedItems():
            color_start = ConnectionWidget.LINE_GRADIENT_COLOR_SOURCE_SELECTED
            color_end = ConnectionWidget.LINE_GRADIENT_COLOR_SINK_SELECTED
        else:
            color_start = ConnectionWidget.LINE_GRADIENT_COLOR_SOURCE
            color_end = ConnectionWidget.LINE_GRADIENT_COLOR_SINK

        gradient = QLinearGradient(start, end)
        gradient.setColorAt(0.0, color_start)
        gradient.setColorAt(1.0, color_end)

        pen = QPen(QBrush(gradient), 5)

        painter.setPen(pen)
        painter.drawLine(line)

        painter.restore()

        super().paint(painter, option, widget)
        

class Node():
    id_counter = 0
    def __init__(self, label, x=0, y=0):
        self.id = Node.id_counter
        #print('adding node with id', self.id)
        Node.id_counter += 1
        self.label = label
        self.x = x
        self.y = y
        self.app = QApplication.instance()
        self.app.nodes.append(self)
        self.color = '#636d83'
        self.app.node_created.emit()

    def set_color(self, color_code):
        self.color = color_code
        self.widget.set_color(color_code)

    def set_widget(self, widget):
        self.widget = widget

    def get_widget_center(self):
        x = self.widget.pos().x()
        y = self.widget.pos().y()
        w = self.widget.width()
        h = self.widget.height()
        return QPointF(x + (w/2), y + (h/2))

    def get_connections_incoming(self):
        connections = self.app.connections
        result = []
        for connection in connections:
            if connection.sink.id == self.id:
                result.append(connection)
        return result

    def get_connections_outgoing(self):
        connections = self.app.connections
        result = []
        for connection in connections:
            if connection.source.id == self.id:
                result.append(connection)
        return result

    def delete_connections(self):
        connections = self.app.connections
        to_delete = []
        for connection in connections:
            if connection.sink.id == self.id or connection.source.id == self.id:
                to_delete.append(connection)

        for connection in to_delete:
            connection.delete()

    def delete(self):
        self.delete_connections()
        self.app.nodes.remove(self)
        self.widget.delete()
        self.app.node_deleted.emit()

    def __lt__(self, other):
        return self.id < other.id


class NodeWidget(QFrame):
    MAX_LABEL_WIDTH = NODE_WIDGET_MAX_LABEL_WIDTH
    MAX_WIDGET_HEIGHT = NODE_WIDGET_MAX_WIDGET_HEIGHT
    CORNER_RADIUS = NODE_WIDGET_CORNER_RADIUS

    PEN_BLACK = QPen(QColor('#000000'), 3, Qt.PenStyle.SolidLine)
    PEN_NORMAL = NODE_WIDGET_PEN_NORMAL
    PEN_SELECTED = QPen(QColor('#282c34'), 4, Qt.PenStyle.SolidLine)
    PEN_FROZEN_NORMAL = QPen(QColor('#383c4a'), 2, Qt.PenStyle.DashLine)
    PEN_FROZEN_SELECTED = QPen(QColor('#282c34'), 4, Qt.PenStyle.DashLine)
    COLOR_NORMAL = QColor('#636d83')
    BRUSH_NORMAL = NODE_WIDGET_BRUSH_NORMAL
    BRUSH_HOVER = QBrush(QColor('#767e8d'))

    on_move = pyqtSignal()
    def __init__(self, node, scene_widget):
        super().__init__()
        self.node = node
        self.scene_widget = scene_widget
        node.set_widget(self)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

        self.setAutoFillBackground(False)

        self.layout = QVBoxLayout()
        self.label = QLabel(node.label)
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(NodeWidget.MAX_LABEL_WIDTH)
        self.setMaximumHeight(NodeWidget.MAX_WIDGET_HEIGHT)
        self.label.setAutoFillBackground(False)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.selection_buffer = None
        self.reset_selection = False

        self.is_hovering = False

        self.app = QApplication.instance()

        self.current_pen = NodeWidget.PEN_NORMAL
        self.current_brush = NodeWidget.BRUSH_NORMAL

        self.current_color = NodeWidget.COLOR_NORMAL

        self.frozen = False

    def set_color(self, color_code):
        # TODO: make label text color white if background color is too dark
        # ... if QColor.lightness() < xyz -> text color is white
        self.current_color = QColor(color_code)
        self.current_brush = QBrush(self.current_color)

        if self.current_color.lightness() < 100:
            self.label.setStyleSheet('color: white')
        else:
            self.label.setStyleSheet('color: black')

    def delete(self):
        self.scene_widget.delete()
        self.deleteLater()

    def get_scene_widget_center(self):
        x = self.scene_widget.pos().x()
        y = self.scene_widget.pos().y()
        w = self.scene_widget.width()
        h = self.scene_widget.height()
        return QPointF(x + (w/2), y + (h/2))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        if self.frozen:
            if self.scene_widget.isSelected():
                self.current_pen = NodeWidget.PEN_FROZEN_SELECTED
            else:
                self.current_pen = NodeWidget.PEN_FROZEN_NORMAL
        else:
            if self.scene_widget.isSelected():
                self.current_pen = NodeWidget.PEN_SELECTED
            else:
                self.current_pen = NodeWidget.PEN_NORMAL

        painter.setPen(self.current_pen)
        painter.setBrush(self.current_brush)

        padding = 2
        rect = self.rect().adjusted(padding, padding, -padding, -padding)
        painter.drawRoundedRect(rect, NodeWidget.CORNER_RADIUS, NodeWidget.CORNER_RADIUS)

        super().paintEvent(event)


    def mousePressEvent(self, event):
        if self.app.MODE == self.app.MODE_CONNECTION:
            selection = self.app.window.scene.selectedItems()
            if len(selection) > 0:
                if self.scene_widget not in selection:
                    if not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                        for node_widget in selection:
                            node = node_widget.widget().node
                            source = node
                            sink = self.node
                            self.app.connect_nodes(source, sink)
                            self.selection_buffer = selection
                            self.reset_selection = True

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        if self.reset_selection:
            self.app.window.scene.clearSelection()
            for item in self.selection_buffer:
                item.setSelected(True)
            self.reset_selection = False

    def getScenePos(self):
        return self.scene_widget.pos()

    def mouseClickEvent(self, event):
        pass

    def hoverEnterEvent(self, event):
        hover_color = self.current_color
        hover_color = hover_color.lighter(150)
        self.current_brush = QBrush(hover_color)
        self.is_hovering = True

    def hoverLeaveEvent(self, event):
        self.current_brush = QBrush(self.current_color)
        self.is_hovering = False

    def mouseDoubleClickEvent(self, event):
        pass

    def moveEvent(self, event):
        self.on_move.emit()

    def freeze(self):
        self.frozen = True
        self.scene_widget.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)

    def unfreeze(self):
        self.frozen = False
        self.scene_widget.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

# from ChatGPT
class DraggableProxyWidget(QGraphicsProxyWidget):
    def mousePressEvent(self, event):
        self.widget().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            QGraphicsItem.mousePressEvent(self, event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        QGraphicsItem.mouseMoveEvent(self, event)
        self.widget().mouseMoveEvent(event)

    def hoverEnterEvent(self, event):
        QGraphicsItem.hoverEnterEvent(self, event)
        self.widget().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        QGraphicsItem.hoverLeaveEvent(self, event)
        self.widget().hoverLeaveEvent(event)

    def mouseReleaseEvent(self, event):
        QGraphicsItem.mouseReleaseEvent(self, event)
        self.widget().mouseReleaseEvent(event)

    def mouseClickEvent(self, event):
        self.widget().mouseClickEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.widget().mouseDoubleClickEvent(event)

    def ItemSelectedHasChanged(self, event):
        pass

    def ItemPositionHasChanged(self, event):
        self.widget().moveEvent(event)

    ## TODO does nothing
    def itemChange(self, change, value):
        return QGraphicsProxyWidget.itemChange(self, change, value)

    def delete(self):
        self.scene().removeItem(self)
        self.deleteLater()

class GraphScene(QGraphicsScene):
    GAP_SIZE = 2
    def __init__(self, window):
        super().__init__()
        self.setSceneRect(-100000, -100000, 200000, 200000)
        self.window = window
        self.app = QApplication.instance()

    def add_node(self, tmp_node):
        proxy = DraggableProxyWidget()
        tmp_widget = NodeWidget(tmp_node, proxy)
        proxy.setWidget(tmp_widget)
        self.addItem(proxy)
        proxy.setFlag(
                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable,
                    True
        )

        proxy.setFlag(
                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable,
                    True
        )

        proxy.setPos(tmp_node.x, tmp_node.y)

    def freeze_selection(self):
        for node_widget in self.get_selection():
            node_widget.widget().freeze()

    def unfreeze_selection(self):
        for node_widget in self.get_selection():
            node_widget.widget().unfreeze()

    def delete_connections(self):
        widgets_selected = self.selectedItems()
        for scene_widget in widgets_selected:
            scene_widget.widget().node.delete_connections()

    def delete_selection(self):
        widgets_selected = self.selectedItems()
        for scene_widget in widgets_selected:
            scene_widget.widget().node.delete()

    def get_selection(self):
        result = []
        for item in self.selectedItems():
            result.append(item)
        return result

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            item_at_click_position = self.itemAt(event.scenePos(), QTransform())

            if isinstance(item_at_click_position, DraggableProxyWidget):
                label = self.window.show_label_input_dialog(item_at_click_position.widget().node.label)
                if len(label) > 0:
                    item_at_click_position.widget().node.label = label
                    item_at_click_position.widget().label.setText(label)
            else:
                label = self.window.show_label_input_dialog()
                if len(label) > 0:
                    node = Node(label, event.scenePos().x(), event.scenePos().y())
                    self.add_node(node)

    def align_nodes_vertical(self, method=ALIGN_TO_MEAN):
        # TODO not efficient!
        widgets_selected = self.selectedItems()
        y_coords = []

        for scene_widget in widgets_selected:
            widget = scene_widget.widget()
            scene_pos = widget.getScenePos()
            y = scene_pos.y()
            y_coords.append(y)

        new_y = np.mean(y_coords)
        #if method == ALIGN_TO_MEAN:
        #    new_y = np.mean(y_coords)
        if method == ALIGN_TO_FIRST:
            new_y = y_coords[0]

        for scene_widget in widgets_selected:
            widget = scene_widget.widget()
            scene_pos = widget.getScenePos()
            x = scene_pos.x()
            widget.move(int(x), int(new_y))

    def align_nodes_horizontal(self, method=ALIGN_TO_MEAN):
        # TODO not efficient!
        widgets_selected = self.selectedItems()
        x_coords = []

        for scene_widget in widgets_selected:
            #print(scene_widget, type(scene_widget))
            widget = scene_widget.widget()
            scene_pos = widget.getScenePos()
            x = scene_pos.x()
            x_coords.append(x)

        new_x = np.mean(x_coords)
        #if method == ALIGN_TO_MEAN:
        #    new_x = np.mean(x_coords)
        if method == ALIGN_TO_FIRST:
            new_x = x_coords[0]

        for scene_widget in widgets_selected:
            widget = scene_widget.widget()
            scene_pos = widget.getScenePos()
            y = scene_pos.y()
            widget.move(int(new_x), int(y))

    def arrange_square(self):
        widgets_selected = []
        widest = 0
        highest = 0
        x_coords = []
        y_coords = []

        for widget in self.selectedItems():
            if isinstance(widget, DraggableProxyWidget):
                widgets_selected.append(widget)
                x = widget.scenePos().x()
                y = widget.scenePos().y()

                x_coords.append(x)
                y_coords.append(y)

                width = widget.widget().width()
                height = widget.widget().height()
                scene_pos = widget.widget().getScenePos()

                if width > widest:
                    widest = width
                if height > highest:
                    highest = height

        n_nodes = len(widgets_selected)
        if n_nodes < 2:
            return

        n_columns = int(np.sqrt(n_nodes))
        n_rows = int(n_nodes / n_columns) + 1

        center_x = int(np.mean(x_coords))
        center_y = int(np.mean(y_coords))
        center = QPoint(center_x, center_y)

        node_width = widest + GraphScene.GAP_SIZE
        node_height = highest + GraphScene.GAP_SIZE

        x_offset = int(node_width * n_columns / 2)
        y_offset = int(node_height * n_rows / 2)

        col_counter = 0
        row_counter = 0
        for widget in widgets_selected:
            new_x = (center_x - x_offset) + (node_width * col_counter)
            new_y = (center_y - y_offset) + (node_height * row_counter)
            widget.widget().move(int(new_x), int(new_y))
            col_counter += 1
            if col_counter >= n_columns:
                col_counter = 0
                row_counter += 1

    def distribute_vertical(self):
        # TODO not efficient!
        widgets_selected = self.selectedItems()
        y_coords = []
        nodes_to_sort = {}

        total_height = 0

        for scene_widget in widgets_selected:
            widget = scene_widget.widget()
            scene_pos = widget.getScenePos()
            y = scene_pos.y()
            nodes_to_sort[widget.node] = y
            total_height += scene_widget.boundingRect().height()

        # sort by initial coord so the sequence order stays the same
        nodes_sorted = dict(sorted(nodes_to_sort.items(), key=lambda item: item[1]))
        y_coords = list(nodes_sorted.values())

        total_height += (len(y_coords) - 1) * GraphScene.GAP_SIZE

        top = int(np.mean(y_coords) - (total_height / 2))
        bottom = int(np.mean(y_coords) + (total_height / 2))

        # distribute evenly
        distributed_y = np.linspace(top, bottom, len(y_coords)) #(np.max(y_coords) - np.min(y_coords)) / len(y_coords))

        # assign new y values to buffer dict
        # dictiories are little mimimis, that's why this is 3 lines of code
        for i, new_y in enumerate(distributed_y):
            key = list(nodes_sorted.keys())[i]
            nodes_sorted[key] = new_y

        # assign new positions to nodes
        for node, new_y in nodes_sorted.items():
            widget = node.widget
            scene_pos = widget.getScenePos()
            x = scene_pos.x()
            widget.move(int(x), int(new_y))

    def distribute_horizontal(self):
        # TODO not efficient!
        widgets_selected = self.selectedItems()
        x_coords = []
        nodes_to_sort = {}

        total_width = 0

        for scene_widget in widgets_selected:
            widget = scene_widget.widget()
            scene_pos = widget.getScenePos()
            x = scene_pos.x()
            nodes_to_sort[widget.node] = x
            total_width += scene_widget.boundingRect().width()

        # sort by initial coord so the sequence order stays the same
        nodes_sorted = dict(sorted(nodes_to_sort.items(), key=lambda item: item[1]))
        x_coords = list(nodes_sorted.values())
        # distribute evenly

        total_width += (len(x_coords) - 1) * GraphScene.GAP_SIZE

        left = int(np.mean(x_coords) - (total_width / 2))
        right = int(np.mean(x_coords) + (total_width / 2))

        distributed_x = np.linspace(left, right, len(x_coords)) #(np.max(x_coords) - np.min(x_coords)) / len(x_coords))

        # assign new y values to buffer dict
        # dictiories are little mimimis, that's why this is 3 lines of code
        for i, new_x in enumerate(distributed_x):
            key = list(nodes_sorted.keys())[i]
            nodes_sorted[key] = new_x

        # assign new positions to nodes
        for node, new_x in nodes_sorted.items():
            widget = node.widget
            scene_pos = widget.getScenePos()
            y = scene_pos.y()
            widget.move(int(new_x), int(y))

    ## TODO: handle colors (first selected? majority?)
    def merge_nodes(self):
        new_node_label = self.window.show_label_input_dialog()

        widgets_selected = self.selectedItems()

        all_x = []
        all_y = []
        for scene_widget in widgets_selected:
            all_x.append(scene_widget.pos().x())
            all_y.append(scene_widget.pos().y())

        x = int(np.mean(all_x))
        y = int(np.mean(all_y))

        node = Node(new_node_label, x, y)
        self.add_node(node)

        nodes_to_delete = []

        for scene_widget in widgets_selected:
            for connection in scene_widget.widget().node.get_connections_incoming():
                self.window.app.connect_nodes(connection.source, node)
                connection.delete()
            for connection in scene_widget.widget().node.get_connections_outgoing():
                self.window.app.connect_nodes(node, connection.sink)
                connection.delete()
            nodes_to_delete.append(scene_widget.widget().node)

        for node_to_delete in nodes_to_delete:
            node_to_delete.delete()

    ## TODO: move those to app
    def select_all(self):
        for node in self.app.nodes:
            node.widget.scene_widget.setSelected(True)

    def set_selection_mode_rect(self):
        self.selection_mode = self.app.SELECTION_MODE_RECT

    def set_selection_mode_lasso(self):
        self.selection_mode = self.app.SELECTION_MODE_LASSO

    def shrink_selection(self):
        pass

    def grow_selection(self):
        pass

    def select_parents(self):
        selected_nodes = []
        new_selection = []
        for item in self.get_selection():
            selected_nodes.append(item.widget().node)

        for connection in self.app.connections:
            if connection.sink in selected_nodes:
                new_selection.append(connection.source.widget.scene_widget)

        for item in list(set(new_selection)):
            item.setSelected(True)

    def select_children(self):
        selected_nodes = []
        new_selection = []
        for item in self.get_selection():
            #item.scene_widget.setSelected(True)
            selected_nodes.append(item.widget().node)

        for connection in self.app.connections:
            if connection.source in selected_nodes:
                new_selection.append(connection.sink.widget.scene_widget)

        for item in list(set(new_selection)):
            item.setSelected(True)

    def arrange_by_number_of_parents(self):
        num_parent_dict = {}

        selected_nodes = []
        for item in self.get_selection():
            selected_nodes.append(item.widget().node)

        #for node in self.app.nodes:
        for node in selected_nodes:
            connections = node.get_connections_incoming()
            num_connections = len(connections)
            if num_connections not in num_parent_dict.keys():
                num_parent_dict[num_connections] = []
            num_parent_dict[num_connections].append(node)

        for i, num_connections in enumerate(reversed(sorted(list(num_parent_dict.keys())))):
            for node in num_parent_dict[num_connections]:
                widget = node.widget
                scene_pos = widget.getScenePos()
                x = scene_pos.x()
                ## TODO magic number
                widget.move(int(x), int(i * (150 + GraphScene.GAP_SIZE)))


# from ChatGPT
class GraphView(QGraphicsView):

    PEN_CONNECTION_PREVIEW = QPen(QColor('#00b3bb'), 2, Qt.PenStyle.DashLine)

    def __init__(self, scene):
        super().__init__(scene)
        ## turn off scrolbars in case we want dragging behavior
        #self.setHorizontalScrollBarPolicy(
        #    Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        #)
        #self.setVerticalScrollBarPolicy(
        #    Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        #)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )

        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

        self.zoom = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.ZOOM_THRESHOLD = 0.6
        self.space_held = False
        self.panning = False
        self.last_mouse_pos = QPoint()
        self.mouse_down = False
        self.scene = scene
        self.cut_mode_line = []
        self.connections_to_cut = []
        self.app = QApplication.instance()
        self.app.mode_changed.connect(self.mode_changed)

        self.setAcceptDrops(True)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setInteractive(True)

    def mode_changed(self):
        if self.app.MODE == self.app.MODE_SELECTION:
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        elif self.app.MODE == self.app.MODE_CUT:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)

    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)
        painter.save()
        painter.resetTransform()
        zoom_level = self.transform().m11()

        if zoom_level < self.ZOOM_THRESHOLD:
            cursor_pos_viewport = self.mapFromGlobal(QCursor.pos())
            hovered_widget = self.itemAt(cursor_pos_viewport)
            if isinstance(hovered_widget, DraggableProxyWidget):
                scene_rect = hovered_widget.mapRectToScene(hovered_widget.boundingRect())
                pos = self.mapFromScene(hovered_widget.scenePos())
                w = scene_rect.width()
                h = scene_rect.height()
                rect = QRectF(int(pos.x() + ((w / 2) * zoom_level) - w / 2), 
                              int(pos.y() + ((h / 2) * zoom_level) - h / 2),
                              w, h) 

                painter.setPen(NodeWidget.PEN_NORMAL)
                painter.setBrush(QBrush(hovered_widget.widget().current_color))
                painter.drawRoundedRect(rect, NodeWidget.CORNER_RADIUS, NodeWidget.CORNER_RADIUS)

                if hovered_widget.widget().current_color.lightness() < 100:
                    painter.setPen(QPen(QColor('white')))
                else:
                    painter.setPen(NodeWidget.PEN_BLACK)

                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap, hovered_widget.widget().node.label)

        painter.restore()

        painter.setPen(QPen(QColor('red')))
        if self.app.MODE == self.app.MODE_CUT:
            if len(self.cut_mode_line) > 1:
                line = []
                for i, point in enumerate(self.cut_mode_line):
                    line.append(self.mapToScene(point))
                painter.drawPolyline(line)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setPen(GraphView.PEN_CONNECTION_PREVIEW)
        if self.app.MODE == self.app.MODE_CONNECTION:
            for node_widget in self.scene.selectedItems():
                if isinstance(node_widget, DraggableProxyWidget):
                    node_scene_pos = node_widget.mapToScene(node_widget.boundingRect().center())
                    node_pos = self.mapFromScene(node_scene_pos)
                    cursor_pos = self.mapFromGlobal(QCursor.pos())
                    painter.drawLine(node_pos, cursor_pos)
                    #print(node_pos, cursor_pos)
        painter.end()

        super().paintEvent(event)

    def zoom_by(self, factor):
        new_zoom = self.zoom * factor
        new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))
        factor = new_zoom / self.zoom

        if factor != 1.0:
            self.scale(factor, factor)
            self.zoom = new_zoom

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_by(1.15)
            elif event.angleDelta().y() < 0:
                self.zoom_by(1 / 1.15)
            event.accept()
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self.panning = True
            return
        elif event.key() == Qt.Key.Key_Equal:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.scene.distribute_vertical()
            else:
                self.scene.align_nodes_vertical()
        elif event.key() == Qt.Key.Key_QuoteDbl or event.key() == Qt.Key.Key_Bar:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.scene.distribute_horizontal()
            else:
                self.scene.align_nodes_horizontal()

        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
                self.zoom_by(1.15)
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Minus:
                self.zoom_by(1 / 1.15)
                event.accept()
                return
            elif event.key() == Qt.Key.Key_0:
                self.resetTransform()
                self.zoom = 1.0
                event.accept()
                return

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self.panning = False
            return

        super().keyReleaseEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        self.mouse_down = True

        pan_requested = (
            event.button() == Qt.MouseButton.MiddleButton
            or (
                event.button() == Qt.MouseButton.LeftButton
                and self.space_held
            )
        )

        if pan_requested:
            self.panning = True
            self.last_mouse_pos = event.position().toPoint()
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):

        ## event.position() seems to be in viewport space already!

        pos = event.position().toPoint()

        if self.app.MODE == self.app.MODE_CUT and self.mouse_down:
            self.cut_mode_line.append(self.mapFromGlobal(QCursor.pos()))

        if self.panning:
            delta = pos - self.last_mouse_pos
            self.last_mouse_pos = pos

            # Move the viewport with the mouse.
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
            return

        QApplication.instance().cursor_pos = pos

        self.viewport().update()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.mouse_down = False

        if self.app.MODE == self.app.MODE_CUT:
            self.app.cut_connections(self.cut_mode_line)

        self.cut_mode_line = []
        self.viewport().update()

        #print('mouse release')
        if self.panning and event.button() in (
            Qt.MouseButton.MiddleButton,
            Qt.MouseButton.LeftButton,
        ):
            self.panning = False
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

        super().mouseReleaseEvent(event)

    def dragEnterEvent(self, e):
        e.accept()

    def dragMoveEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        pos = e.position().toPoint() # viewport coords
        pos = self.mapToScene(pos)

        widget = e.source()

        widget.remove()
        self.scene.add_node(Node(widget.text, pos.x(), pos.y()))

        e.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.app: QGraphApplication = QApplication.instance()
        self.selection_mode = app.SELECTION_MODE_RECT

        self.setWindowTitle(f'Course Graph Creator')

        y_layout = QVBoxLayout()
        x_layout = QHBoxLayout()

        self.scene = GraphScene(self)
        self.view = GraphView(self.scene)
        self.view.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

        self.palette_tab_widget = QTabWidget()
        self.node_palette = NodePaletteWidget()
        self.style_palette = StylePaletteWidget()
        self.node_manager = NodeListWidget(self.view)
        tool_bar_layout = Toolbar(self)

        ## status bar

        status_bar_layout = QHBoxLayout()
        mode_selection_widget = ModeSelectionWidget()
        mode_widget = ModeWidget()
        node_counter_widget = NodeCounterWidget(self)

        status_bar_layout.addWidget(mode_selection_widget)
        status_bar_layout.addWidget(mode_widget)

        divider = QFrame() 
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        status_bar_layout.addWidget(divider)

        status_bar_layout.addWidget(node_counter_widget)

        ## build final layout

        x_layout.addLayout(tool_bar_layout)
        x_layout.addWidget(self.view)
        self.palette_tab_widget.addTab(self.node_palette, 'Node Palette')
        self.palette_tab_widget.addTab(self.style_palette, 'Style Palette')
        self.palette_tab_widget.addTab(self.node_manager, 'Node Manager')
        x_layout.addWidget(self.palette_tab_widget)

        y_layout.addLayout(x_layout)
        y_layout.addLayout(status_bar_layout)

        main_widget = QWidget()
        main_widget.setLayout(y_layout)
        self.setCentralWidget(main_widget)

    def show_label_input_dialog(self, default_text=''):
        text, submit = QInputDialog.getText(self, 'Enter Node Label', 'Label:', text=default_text)
        if submit:
            return text
        else:
            return ''
    
    def show_open_project_dialog(self):
        project_list = []
        for project_dir in os.listdir(PROJECTS_PATH):
            project_dir_content = os.listdir(f'{PROJECTS_PATH}/{project_dir}')
            nodes_file = f'{project_dir}_nodes.csv'
            connections_file = f'{project_dir}_connections.csv'
            if nodes_file in project_dir_content and connections_file in project_dir_content:
                project_list.append(project_dir)

        if len(project_list) > 0:
            dialog = OpenProjectDialog(project_list, self)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_project = dialog.selected_project
                self.app.project_name = selected_project
                self.app.project_path = f'{PROJECTS_PATH}/{selected_project}'
                self.app.load_nodes(f'{PROJECTS_PATH}/{selected_project}/{selected_project}_nodes.csv')
                self.app.load_connections(f'{PROJECTS_PATH}/{selected_project}/{selected_project}_connections.csv')

    def show_open_file_dialog(self, caption='Open File', filter=''):
        file_name, selectedFilter = QFileDialog.getOpenFileName(self, caption=caption, filter=filter)
        return file_name

    def save_graph(self, file_name=''):
        if file_name == '':
            file_name, ok_clicked = QInputDialog.getText(self, 'Enter Project Name for Saving', 'Name:')
            if not ok_clicked:
                return

        self.app.save_graph(file_name)

    def load_graph(self):
        node_path = self.show_open_file_dialog(caption='Open Node File', filter='*.csv')
        connection_path = self.show_open_file_dialog(caption='Open Connection File', filter='*.csv')
        self.app.load_graph(node_path, connection_path)

    def keyPressEvent(self, event):
        #app = QApplication.instance()
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_S.value:
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    self.save_graph()
                else:
                    self.save_graph(self.app.project_name)
            elif event.key() == Qt.Key.Key_O.value:
                self.show_open_project_dialog()
            elif event.key() == Qt.Key.Key_A.value:
                self.scene.select_all()

        else:
            if event.key() == Qt.Key.Key_C.value:
                self.app.MODE = self.app.MODE_CONNECTION
                self.app.mode_changed.emit()
            elif event.key() == Qt.Key.Key_S.value or event.key() == Qt.Key.Key_Escape.value:
                self.app.MODE = self.app.MODE_SELECTION
                self.app.mode_changed.emit()
            elif event.key() == Qt.Key.Key_X.value:
                self.app.MODE = self.app.MODE_CUT
                self.app.mode_changed.emit()
            elif event.key() == Qt.Key.Key_Delete.value:
                self.scene.delete_selection()

if __name__ == '__main__':
    app = QGraphApplication(sys.argv)

    window = MainWindow()
    app.window = window
    window.show()

    app.exec()
