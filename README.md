# GraphIT Course Editor

## Usage

The GraphIT Course Editor can be used to manually create and edit graphs in a simple UI.
Nodes can be created, moved, arranged, and renamed, as well as connected with each other.

| **Feature** | **Description** |
| --- | --- |
| Creating a Node | The most simple way to create a node is to double click the canvas. Then, a node name can be entered via a popup prompt and then, a node is created at the click position. Nodes can also be added to the graph by dragging them from the node palette (see below) or by dragging any text into the canvas. When the latter feature is used, a new node is created for each line in the pasted text. |
| Deleting Nodes | Nodes (and their connections) can be deleted with the *del* key or the *delete* button in the toolbar. |
| Renaming Nodes | Double clicking a node opens a text input prompt, with which a new name for the node can be entered. |
| Moving Nodes | Nodes can be moved by dragging them around with the mouse. |
| Navigating the Canvas | The mouse wheel can be used to move the view up and down, holding *Shift* while using the mouse wheel moves left and right. Pressing and holding the middle mouse button allows for panning. Holding *Ctrl* while scrolling the mouse wheel zooms the viewport. This can also be achieved with *Ctrl* and the plus/minus keys. |
| Selecting Nodes | A single node an be selected by clicking it. More nodes an be added to the selection by holding *Ctrl* and clicking new nodes. Holding *Ctrl* while clicking already selected nodes removes them from the selection. While in *Selection Mode*, rubber band selection is active: multiple nodes can be selected by dragging a rectangular selection area around them. Additionally, the toolbar contains a few buttons for intelligent selection: selecing all nodes in the scene, or adding all children or parents of the currently selected nodes to the selection. |
| Connecting Nodes | In order to connect nodes, one must first switch to the *Connection Mode* by either clicking the corresponding button in the status bar or using the *Ctrl + C* shortcut. While in connection mode, if one or more nodes are selected, clicking another node establishes a new connection from the selected nodes (source) to the clicked node (sink). While in selection mode, if nodes are selected, a dashed line from selected nodes to the mouse cursor indicates where a connection would be created. |
| Deleting Connections | Connections can be deleted individually while in *Cut Mode* (entered with the corresponding button in the status bar, or the *Ctrl + X* shortcut). While in cut mode, connections can be cut by striking them out with the mouse. In order to delete all connection of a node, the corresponding button in the toolbar can be used. |
| Arranging Nodes | The *align* and *distribute* buttons in the toolbar can be used to arrange nodes along an axis, establish constant gap sizes, or distribute them in a grid. |

## GUI

<img src="./docs/images/overview.png">

### Tool Bar

| Icon | Function | Shortcut | Description |
| ---- | -------- | -------- | ----------- |
| <img src="./icons/save.svg"> | Save Graph | Ctrl + S | Saves the graph to the "projects" directory. If the project name is not yet set, a project name can be entered via a popup prompt. |
| <img src="./icons/open.svg"> | Open Graph | Ctrl + O | Shows a list of all projects in the project directory. Double clicking a list element opens the selected project. |
| <img src="./icons/open_list.svg"> | Load Node List |  | Opens a node list file via a file browser. A node list file is a plain text file with one node name per line. The loaded nodes are stored in the node palette menu. |
| <img src="./icons/select_all.svg"> | Select All | Ctrl + A | Selects all nodes in the graph. |
| <img src="./icons/select_children_simple.svg"> | Select Children |  | Selects children of all selected nodes in the graph. |
| <img src="./icons/select_parents_simple.svg"> | Select Parents |  | Selects parents of all selected nodes in the graph. |
| <img src="./icons/delete.svg"> | Delete Nodes | del | Deletes all selected nodes. |
| <img src="./icons/delete_connections.svg"> | Delete Connections |  | Deletes all connectios of all connected nodes. |
| <img src="./icons/merge.svg"> | Merge Nodes |  | Merges all selected nodes into a single node. A name for the new node can be entered with a text input prompt. All connections of merged nodes are retained. |
| <img src="./icons/lock.svg"> | Lock Selection |  | Selected nodes are locked so they can not be moved any more. |
| <img src="./icons/unlock.svg"> | Unlock Selection |  | Selected nodes are unlocked. |
| <img src="./icons/arrange_square.svg"> | Arrange in Square |  | Selected nodes are arranged in a square. Useful when loading a graph without position information. |
| <img src="./icons/arrange_by_parent_count.svg"> | Arrange by Parent Count |  | Selected nodes are arranged vertically by their number of parents. Horizontally, they are distributed evenly. |
| <img src="./icons/align_vertical.svg"> | Align Vertical |  | Selected nodes are aligned along a vertical line. |
| <img src="./icons/align_horizontal.svg"> | Align Horizontal |  | Selected nodes are aligned along a horizontal line. |
| <img src="./icons/distribute_horizontal.svg"> | Distribute Horizontal |  | Selected nodes are distributed evenly in horizontal direction. |
| <img src="./icons/distribute_vertical.svg"> | Distribute Vertical |  | Selected nodes are distributed evenly in vertical direction. |

### Side Bar

| **Node Palette** |  |
| --- | --- |
| <img src="./docs/images/node_palette.png"> | List of nodes that can be dragged into the canvas. The node list can be loaded with the "Load Node List" button. A node list is a plain text file with one node name per line. |
| **Style Palette** |  |
| <img src="./docs/images/style_palette.png"> | Color palette that can be used to assign colors to nodes. There is a small standard palette, but custom colors can be added with the corresponding button. |
| **Node Manager** |  |
| <img src="./docs/images/node_manager.png"> | Tabular overview of all nodes in the graph. Displays the number of children and parents for each node. Double clicking a list entry focuses the viewport on the corresponding node. Can be useful to identify unconnected nodes (nodes without children and parents). |
| **Selection Manager** |  |
| <img src="./docs/images/selection_manager.png"> | Clicking the "Store Selection" button allows for saving and later restorig the current node selection. Selections are named via a text input prompt. Double clicking a list item restores the corresponding selection. Useful to quickly select sub-graphs. |

### Status Bar

<img src="./docs/images/status_bar.png">

The status bar on the bottom displays information on the current application state.
On the left hand side, the current interaction mode (selection, connection, cut) is displayed and can also be switched via the three toggle buttons (see below).
On the right hand side, information about the total number of nodes in the graph, as well as the number of selected nodes is displayed.

| Icon | Function | Shortcut | Description |
| ---- | -------- | -------- | ----------- |
| <img src="./icons/mode_selection.svg"> | Selection Mode | S | In selection mode, nodes can be selected and moved without triggering other functionality. |
| <img src="./icons/mode_connection.svg"> | Connection Mode | C | In connection mode, connections between nodes can be created by first selecting the parent (source) node and then clicking on the child (sink) node. After clicking on the parent node, a dashed line indicates where the connection will goIn connection mode, connections between nodes can be created by first selecting the parent (source) node and then clicking on the child (sink) node. After clicking on the parent node, a dashed line indicates where the connection will go.. |
| <img src="./icons/mode_cut.svg"> | Cut Mode | X | In cut mode, connections can be deleted by cutting them with a mouse stroke. |

## Project File Structure

```
projects/
|
|-- project1/
|   |
|   |-- project1_nodes.csv
|   |-- project1_connections.csv
|   |-- topics.txt (optional)
|
|-- project2/
|
...
```

By default, projects are stored in a project directory within the "projects" subdirectory.
The project directory is named after the project, as are files within.
A project consists mainly of two CSV files: nodes and connections.
They are, again, named according to the project name as specified when first saving the project.

The *nodes* file has one line per node.
It has columns for the node ID, node label, node position, and color in hex format.

The *connections* file has one line per edge (connection between two nodes).
Connections have their own ID and store two node IDs:
the *source* node (parent), and the *sink* node (child, receiving the connection).
