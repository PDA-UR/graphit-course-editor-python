# GraphIT Course Creator


## GUI

<img src="./docs/images/overview.png">

### Toolbar

| Icon | Function | Shortcut | Description |
| ---- | -------- | -------- | ----------- |
| <img src="./icons/save.svg"> | Save Graph | Ctrl + S | Saves the graph to the "projects" directory. If the project name is not yet set, a project name can be entered via a popup prompt. |
| <img src="./icons/open.svg"> | Ctrl + O | Open Graph |  |
| <img src="./icons/open_list.svg"> |  | Load Node List |  |
| <img src="./icons/select_all.svg"> | Ctrl + A | Select All |  |
| <img src="./icons/select_children_simple.svg"> |  | Select Children |  |
| <img src="./icons/select_parents_simple.svg"> |  | Select Parents |  |
| <img src="./icons/delete.svg"> | del | Delete Nodes |  |
| <img src="./icons/delete_connections.svg"> |  | Delete Connections |  |
| <img src="./icons/merge.svg"> |  | Merge Nodes |  |
| <img src="./icons/lock.svg"> |  | Lock Selection |  |
| <img src="./icons/unlock.svg"> |  | Unlock Selection |  |
| <img src="./icons/arrange_square.svg"> |  | Arrange in Square |  |
| <img src="./icons/arrange_by_parent_count.svg"> |  | Arrange by Parent Count |  |
| <img src="./icons/align_vertical.svg"> |  | Align Vertical |  |
| <img src="./icons/align_horizontal.svg"> |  | Align Horizontal |  |
| <img src="./icons/distribute_horizontal.svg"> |  | Distribute Horizontal |  |
| <img src="./icons/distribute_vertical.svg"> |  | Distribute Vertical |  |

### Side Bar

**Node Palette**

| <img src="./docs/images/node_palette.png"> | List of nodes that can be dragged into the canvas. The node list can be loaded with the "Load Node List" button. A node list is a plain text file with one node name per line. |

**Style Palette**

| <img src="./docs/images/style_palette.png"> | Color palette that can be used to assign colors to nodes. There is a small standard palette, but custom colors can be added with the corresponding button. |

**Node Manager**

| <img src="./docs/images/node_manager.png"> | Tabular overview of all nodes in the graph. Displays the number of children and parents for each node. Double clicking a list entry focuses the viewport on the corresponding node. Can be useful to identify unconnected nodes (nodes without children and parents). |

**Selection Manager**

| <img src="./docs/images/selection_manager.png"> | Clicking the "Store Selection" button allows for saving and later restorig the current node selection. Selections are named via a text input prompt. Double clicking a list item restores the corresponding selection. Useful to quickly select sub-graphs. |
