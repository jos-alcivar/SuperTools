from PyQt5 import (
    QtCore,
    QtWidgets,
)

import Utils
from Katana import (
    UI4,
    NodegraphAPI,
)
from functools import partial
from . import ScriptActions as SA
from . import EditorResources as resources

class PassManagerEditor(QtWidgets.QWidget):
    def __init__(self, parent, node):
        super().__init__(parent)
        self.__node = node
        self.__showIncomeSceneChecked = False
        self.setLayout(QtWidgets.QVBoxLayout())

        # Toolbar layout
        self.__toolbarLayout = QtWidgets.QHBoxLayout()
        self.layout().setSpacing(0)
        self.layout().addItem(self.__toolbarLayout)

        # Left-aligned button
        self.__addButton = UI4.Widgets.ToolbarButton(
            toolTip='Add Pass', 
            parent=self,
            normalPixmap=UI4.Util.IconManager.GetPixmap(resources.Icons.plus_icon),
            rolloverPixmap=UI4.Util.IconManager.GetPixmap(resources.Icons.plus_icon_rollover)
        )
        self.__addButton.clicked.connect(self.__onAddButtonClicked)
        self.__toolbarLayout.addWidget(self.__addButton, alignment=QtCore.Qt.AlignLeft)

        # Spacer to separate buttons
        self.__toolbarLayout.addStretch()

        # Right-aligned button
        self.__showIncomeSceneButton = UI4.Widgets.ToolbarButton(
            toolTip="Show Income Scene",
            parent=self,
            normalPixmap=UI4.Util.IconManager.GetPixmap(resources.Icons.gear_icon),
            rolloverPixmap=UI4.Util.IconManager.GetPixmap(resources.Icons.gear_icon_rollover)
        )
        self.__showIncomeSceneButton.mousePressEvent = self.__onShowIncomeSceneButtonClicked
        self.__toolbarLayout.addWidget(self.__showIncomeSceneButton, alignment=QtCore.Qt.AlignRight)

        # Tree widget
        self.__treeWidget = QtWidgets.QTreeWidget(self)
        self.__treeWidget.setHeaderLabels(['Name', 'Enable'])
        self.__treeWidget.setSelectionMode(QtWidgets.QTreeWidget.SingleSelection)
        self.__treeWidget.setAllColumnsShowFocus(True)
        self.__treeWidget.setRootIsDecorated(True)
        self.__treeWidget.setSortingEnabled(True)

        # Set specific column widths
        self.__treeWidget.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Interactive)
        self.__treeWidget.header().resizeSection(0, 200)
        self.__treeWidget.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Interactive)
        self.__treeWidget.header().resizeSection(1, 50)

        # Connect the context menu event
        self.__treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.__treeWidget.customContextMenuRequested.connect(self.__onTreeItemContextMenu)

        self.layout().addWidget(self.__treeWidget)
        self.layout().addWidget(UI4.Widgets.VBoxLayoutResizer(self.__treeWidget, 120))
        self.layout().addSpacing(1)

        self.__parameterWidgetLayout = QtWidgets.QVBoxLayout()
        self.layout().addLayout(self.__parameterWidgetLayout)

        self.layout().addStretch()

    def __addRow(self, root_name, child_name=None, grandchild_name=None, enable_state=True):
        """Add a row to the tree widget with support for up to 3 levels of hierarchy."""
        # Ensure root_name is valid
        if not isinstance(root_name, str):
            raise TypeError("root_name must be a string")

        # Find or create the root item
        root_item = self.__findOrCreateItem(self.__treeWidget.invisibleRootItem(), root_name)
        root_item.setExpanded(True)
        if child_name:
            # Ensure child_name is valid
            if not isinstance(child_name, str):
                raise TypeError("child_name must be a string")
            # Find or create the child item under the root
            child_item = self.__findOrCreateItem(root_item, child_name)
            child_item.setExpanded(True)
            if grandchild_name:
                # Ensure grandchild_name is valid
                if not isinstance(grandchild_name, str):
                    raise TypeError("grandchild_name must be a string")
                # Create the grandchild item under the child
                grandchild_item = QtWidgets.QTreeWidgetItem(child_item, [grandchild_name])
                grandchild_item.setExpanded(True)
                self.__addCheckbox(grandchild_item, enable_state)
            else:
                # If only a child item is specified
                self.__addCheckbox(child_item, enable_state)
        else:
            # If only a root item is specified
            self.__addCheckbox(root_item, enable_state)

    def __findOrCreateItem(self, parent, name):
        """Find an existing item with the given name or create it."""
        for i in range(parent.childCount()):
            child = parent.child(i)
            if child.text(0) == name:
                return child
        # If the item doesn't exist, create it
        item = QtWidgets.QTreeWidgetItem(parent, [name])  # Ensure `name` is a string
        return item

    def __addCheckbox(self, item, enable_state):
        """Add a checkbox to the specified item."""
        checkbox = QtWidgets.QCheckBox()
        checkbox.setChecked(enable_state)
        checkbox.stateChanged.connect(partial(self.__onCheckboxChanged, item.text(0)))
        self.__treeWidget.setItemWidget(item, 1, checkbox)


    def __onCheckboxChanged(self, name, state):
        """Handle changes to the checkbox state."""
        print(f"Checkbox for '{name}' changed to {'Checked' if state == QtCore.Qt.Checked else 'Unchecked'}")

    def __onAddButtonClicked(self):
        """Handle the 'Add Pass' button click."""
        dialog = AddPassDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            name = dialog.getName()
            # Extract the hierarchy from the name (e.g., split by underscores)
            parts = name.split('_')  # Assuming format like "root_child_grandchild"
            root_name = parts[0]
            child_name = parts[1] if len(parts) > 1 else None
            grandchild_name = name

            # Add the row with the parsed hierarchy
            self.__addRow(root_name, child_name, grandchild_name, enable_state=True)
            print(f"Added new row: {name}")

    def __onShowIncomeSceneButtonClicked(self, event):
        """Show context menu with a checkbox for the 'Show Income Scene' button."""
        if event.button() == QtCore.Qt.LeftButton:
            menu = QtWidgets.QMenu(self)

            # Add checkbox action to the menu
            show_income_scene_action = QtWidgets.QAction("Show Income Scene", self)
            show_income_scene_action.setCheckable(True)
            show_income_scene_action.setChecked(False)  # Initial state
            show_income_scene_action.triggered.connect(self.__onShowIncomeSceneChecked)

            # Add the action to the menu and display it
            menu.addAction(show_income_scene_action)
            menu.exec_(self.__showIncomeSceneButton.mapToGlobal(event.pos()))

    def __onShowIncomeSceneChecked(self, checked):
        """Handle the 'Show Income Scene' checkbox toggle."""
        self.__showIncomeSceneChecked = checked
        print(f"'Show Income Scene' checkbox set to: {'Checked' if checked else 'Unchecked'}")

    def __onTreeItemContextMenu(self, position):
        """Display a context menu for the tree widget items."""
        item = self.__treeWidget.itemAt(position)
        if item is not None:
            menu = QtWidgets.QMenu(self)

            # Add "Adopt for Editing" option
            if self.__showIncomeSceneChecked:
                adopt_action = QtWidgets.QAction("Adopt for Editing", self)
                adopt_action.triggered.connect(lambda: self.__onAdoptForEditing(item))
                menu.addAction(adopt_action)

                # Add a separator
                menu.addSeparator()

            # Add "Rename" option
            rename_action = QtWidgets.QAction("Rename", self)
            rename_action.triggered.connect(lambda: self.__onRenameItem(item))
            menu.addAction(rename_action)

            # Add "Delete" option
            delete_action = QtWidgets.QAction("Delete", self)
            delete_action.triggered.connect(lambda: self.__onDeleteItem(item))
            menu.addAction(delete_action)

            # Add "Duplicate" option
            duplicate_action = QtWidgets.QAction("Duplicate", self)
            duplicate_action.triggered.connect(lambda: self.__onDuplicateItem(item))
            menu.addAction(duplicate_action)

            # Show the menu at the cursor's position
            menu.exec_(self.__treeWidget.viewport().mapToGlobal(position))

    def __onAdoptForEditing(self, item):
        """Handle the 'Adopt for Editing' action."""
        print(f"Adopted '{item.text(0)}' for editing.")

    def __onRenameItem(self, item):
        """Handle the 'Rename' action."""
        parent_item = item.parent()
        dialog = RenameDialog(self)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_name = dialog.getName()
            current_name = item.text(0)

            # Validate the new name format (must follow the format: type_name_iteration, e.g., 'bty_char_01')
            new_name_parts = new_name.split('_')
            if new_name_parts[-1].isdigit():
                root_name = new_name_parts[0]
                child_name = new_name_parts[1]
                iteration = int(new_name_parts[-1])

                # Check if the name is valid and follows the format: 'root_child_iteration'
                if root_name == current_name.split('_')[0] and child_name == current_name.split('_')[1]:
                    # Ensure the name is not already taken (check children and grandchildren)
                    name_taken = False
                    if parent_item is not None:
                        grandparent_item = parent_item.parent()  # Check if it's a grandchild under a child item
                        if grandparent_item is not None:
                            for i in range(grandparent_item.childCount()):
                                child_item = grandparent_item.child(i)
                                for j in range(child_item.childCount()):
                                    grandchild_item = child_item.child(j)
                                    grandchild_name = grandchild_item.text(0)
                                    if new_name == grandchild_name:
                                        name_taken = True
                                        break
                                if name_taken:
                                    break
                    
                    # If the name is not taken, rename the item
                    if not name_taken:
                        print(f"Renaming item: '{current_name}' to '{new_name}'")
                        item.setText(0, new_name)
                    else:
                        print("A pass with this name already exists.")
                else:
                    print("The new name doesn't match the correct format.")
            else:
                print("Invalid name format. Ensure it follows the pattern 'type_name_iteration'.")


    def __onDeleteItem(self, item):
        """Handle the 'Delete' action."""
        parent_item = item.parent()

        if parent_item is not None:
            grandparent_item = parent_item.parent()  # Check if it's a grandchild under a child item
            if grandparent_item is not None:
                # Delete the grandchild item first
                index = parent_item.indexOfChild(item)
                parent_item.takeChild(index)
                print(f"Deleted grandchild item: {item.text(0)}")

                # If the parent (child) has no more items, delete it too
                if parent_item.childCount() == 0:
                    grandparent_item.removeChild(parent_item)
                    print(f"Deleted child item: {parent_item.text(0)}")

                    # If the grandparent (root) has no more children, delete it
                    if grandparent_item.childCount() == 0:
                        index = self.__treeWidget.indexOfTopLevelItem(grandparent_item)
                        self.__treeWidget.takeTopLevelItem(index)
                        print(f"Deleted root item: {grandparent_item.text(0)}")

    def __onDuplicateItem(self, item):
        """Handle the 'Duplicate' action."""
        parent_item = item.parent()

        # Only allow duplication of a grandchild
        if parent_item is not None:
            grandparent_item = parent_item.parent()  # Check if it's a grandchild under a child item
            if grandparent_item is not None:
                # Duplicate grandchild item
                name = item.text(0)
                checkbox_widget = self.__treeWidget.itemWidget(item, 1)
                checkbox_state = checkbox_widget.isChecked() if checkbox_widget else False
                
                # Split the name to extract the iteration number
                name_split = name.split("_")
                iteration = int(name_split[-1])

                # Find the next available iteration number
                existing_iterations = []
                for i in range(grandparent_item.childCount()):
                    child_item = grandparent_item.child(i)
                    for j in range(child_item.childCount()):
                        grandchild_item = child_item.child(j)
                        grandchild_name = grandchild_item.text(0)
                        grandchild_parts = grandchild_name.split("_")
                        if len(grandchild_parts) >= 3 and grandchild_parts[-1].isdigit():
                            existing_iterations.append(int(grandchild_parts[-1]))

                # Find the next available iteration
                next_iteration = iteration + 1
                while next_iteration in existing_iterations:
                    next_iteration += 1

                # Create the new name with the next available iteration
                name_split[-1] = f"{next_iteration:02}"
                grandchild_name = "_".join(name_split)

                # Add the new duplicated item with the next available iteration
                self.__addRow(grandparent_item.text(0), parent_item.text(0), grandchild_name, enable_state=checkbox_state)
                print(f"Duplicated item: {name} -> {grandchild_name}")


class AddPassDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Pass")
        self.setLayout(QtWidgets.QHBoxLayout())

        # Type ComboBox
        self.typeComboBox = QtWidgets.QComboBox()
        self.typeComboBox.addItems(['bty', 'rfl', 'shdw', 'util'])
        self.layout().addWidget(QtWidgets.QLabel("Type:"))
        self.layout().addWidget(self.typeComboBox)

        # Name ComboBox
        self.nameComboBox = QtWidgets.QComboBox()
        self.nameComboBox.addItems(['char', 'crowd', 'env', 'fx', 'prop', 'vhcl', 'custom'])
        self.nameComboBox.currentIndexChanged.connect(self.__onNameChanged)
        self.layout().addWidget(QtWidgets.QLabel("Name:"))
        self.layout().addWidget(self.nameComboBox)

        # Custom Name Input
        self.customNameInput = QtWidgets.QLineEdit()
        self.customNameInput.setPlaceholderText("Enter custom name")
        self.customNameInput.setVisible(False)
        self.layout().addWidget(self.customNameInput)

        # Iteration ComboBox
        self.iterationComboBox = QtWidgets.QComboBox()
        self.iterationComboBox.addItems([f"{i:02}" for i in range(1, 10)])
        self.layout().addWidget(QtWidgets.QLabel("Iteration:"))
        self.layout().addWidget(self.iterationComboBox)

        # Buttons
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.layout().addWidget(buttonBox)

    def __onNameChanged(self, index):
        """Show or hide the custom name input field."""
        is_custom = self.nameComboBox.currentText() == "custom"
        self.customNameInput.setVisible(is_custom)

    def getName(self):
        """Construct the full name based on the selections."""
        pass_type = self.typeComboBox.currentText()
        name = self.customNameInput.text() if self.nameComboBox.currentText() == "custom" else self.nameComboBox.currentText()
        iteration = self.iterationComboBox.currentText()
        return f"{pass_type}_{name}_{iteration}"

class RenameDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rename")
        self.setLayout(QtWidgets.QHBoxLayout())

        # Custom Name Input
        self.customNameInput = QtWidgets.QLineEdit()
        self.customNameInput.setPlaceholderText("Enter new name")
        self.layout().addWidget(self.customNameInput)

        # Buttons
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.layout().addWidget(buttonBox)

    def getName(self):
         return self.customNameInput.text()
