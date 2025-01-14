import json

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor, QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QCheckBox, QPushButton, QListWidget, QScrollArea, QGroupBox, QListWidgetItem, QRadioButton, QComboBox,
    QTableWidget, QHeaderView
)

from pynichon.io.io_manager import get_io_manager
from pynichon.utils.spell_manager import get_spell_manager


class MainWindow(QWidget):
    _instance = None

    def __init__(self):
        super().__init__()

        self.io_manager = get_io_manager()
        self.spell_manager = get_spell_manager()

        self.current_spell = None

        self.setWindowTitle("PyNiChon")
        self.resize(1000, 600)
        self.setWindowIcon(QIcon('.\pynichon.png'))
        self.setAcceptDrops(True)

        with open("PyNiChon.qss", "r") as fh:
            self.setStyleSheet(fh.read())

        self.tb_input_dir = QLineEdit()
        self.tb_output_dir = QLineEdit()
        self.tb_filter = QLineEdit()
        self.tb_rename = QLineEdit()

        self.cb_include_subdirs = QCheckBox("Include Subdirectories")
        self.cb_skip_errors = QCheckBox("Skip Files With Errors")
        self.cb_filter = QCheckBox("Filter File Names")
        self.cb_rename = QCheckBox("Rename Files")
        self.cb_only_modified = QCheckBox("Output Only Modified Files")

        self.l_spells = QListWidget()

        self.gb_spell_options = QGroupBox("Spell Options")
        self.options_layout = QGridLayout()
        self.gb_spell_options.setLayout(self.options_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.gb_spell_options)

        self.b_run = QPushButton("Run")

        self.create_layout()

        # Map parent checkboxes to child widgets
        self.checkbox_to_widgets = {
            self.cb_filter: [self.tb_filter],
            self.cb_rename: [self.tb_rename],
        }

        self.populate_spells_list()
        self.l_spells.currentItemChanged.connect(self.update_spell_options)
        self.b_run.clicked.connect(self.run_spell)

        for parent_checkbox in self.checkbox_to_widgets.keys():
            parent_checkbox.stateChanged.connect(self.toggle_widgets)
        self.toggle_widgets()

        if self.l_spells.count() > 0:
            first_item = self.l_spells.item(0)
            if first_item and first_item.flags() != Qt.NoItemFlags:  # Ensure not a category separator
                self.l_spells.setCurrentItem(first_item)
                self.update_spell_options(first_item)

    def create_layout(self):
        """
        Create layout of main window.
        """
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(self.create_top_layout())
        main_layout.addLayout(self.create_center_layout())
        main_layout.addLayout(self.create_bottom_layout())

    def create_top_layout(self):
        """
        Create top layout of main window.
        """
        top_layout = QGridLayout()

        # ROW 0
        top_layout.addWidget(QLabel("Input Directory:"), 0, 0)
        top_layout.addWidget(self.tb_input_dir, 0, 1)

        top_layout.addWidget(self.cb_include_subdirs, 0, 2)

        top_layout.addWidget(self.cb_skip_errors, 0, 4)

        top_layout.addWidget(self.tb_filter, 0, 5)
        top_layout.addWidget(self.cb_filter, 0, 6)

        # ROW 1
        top_layout.addWidget(QLabel("Output Directory:"), 1, 0)
        top_layout.addWidget(self.tb_output_dir, 1, 1)

        top_layout.addWidget(self.cb_only_modified, 1, 2)

        top_layout.addWidget(self.tb_rename, 1, 5)

        top_layout.addWidget(self.cb_rename, 1, 6)

        return top_layout

    def create_center_layout(self):
        """
        Create center layout of main window.
        """
        center_layout = QHBoxLayout()

        # LEFT: Spell list
        center_layout.addWidget(self.l_spells, 0, Qt.AlignLeft)

        # RIGHT: Scroll area for spell options
        self.scroll_area.setWidget(self.gb_spell_options)
        center_layout.addWidget(self.scroll_area)

        return center_layout

    def create_bottom_layout(self):
        """
        Create bottom layout of main window.
        """
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.b_run)
        return bottom_layout

    def toggle_widgets(self):
        """
        Toggle interaction with widgets based on parent checkbox state.
        """
        for parent_checkbox, child_widgets in self.checkbox_to_widgets.items():
            enabled = parent_checkbox.isChecked()
            for widget in child_widgets:
                widget.setEnabled(enabled)

    def populate_spells_list(self):
        """Populate the spell list dynamically, grouping by categories."""
        self.l_spells.clear()

        spell_manager = get_spell_manager()
        spell_categories = {}

        # Organize spells by category
        for spell_name, spell in spell_manager.spells.items():
            category = spell.category
            spell_categories.setdefault(category, []).append(spell_name)

        # Add categories and spells to the list widget
        for category, spells in sorted(spell_categories.items()):
            self.add_category_separator(category)
            for spell_name in sorted(spells):
                self.l_spells.addItem(spell_name)

    def add_category_separator(self, category_name):
        """Add a category separator item to the spell list."""
        item = QListWidgetItem(category_name)
        item.setFont(QFont("Arial", 12, QFont.Bold))
        item.setForeground(QColor(128, 128, 128))
        item.setFlags(Qt.NoItemFlags)
        self.l_spells.addItem(item)

    def populate_spell_options(self, options):
        """Populate spell options from JSON."""
        # Clear existing layout
        while self.options_layout.count():
            child = self.options_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for option in options:
            widget = None
            row = option.get("Style", {}).get("Row", 0)
            col = option.get("Style", {}).get("Column", 0)
            row_span = option.get("Style", {}).get("Height", 1)
            col_span = option.get("Style", {}).get("Width", 1)

            if option["Type"] == "Checkbox":
                widget = QCheckBox(option["Label"])
                widget.setChecked(option.get("Default", False))

            elif option["Type"] == "Textbox":
                widget = QLineEdit()
                widget.setPlaceholderText(option.get("Placeholder", ""))
                widget.setText(option.get("Default", ""))
                self.options_layout.addWidget(widget, row, col, row_span, col_span)

            elif option["Type"] == "Dropdown":
                widget = QComboBox()
                widget.addItems(option.get("Options", []))
                widget.setCurrentText(option.get("Default", ""))

            elif option["Type"] == "Radio Buttons":
                group = QGroupBox(option["Label"])
                layout = QVBoxLayout()
                for btn_label in option.get("Options", []):
                    btn = QRadioButton(btn_label)
                    if btn_label == option.get("Default"):
                        btn.setChecked(True)
                    layout.addWidget(btn)
                group.setLayout(layout)
                widget = group

            elif option["Type"] == "Paragraph":
                widget = QLabel(option["Text"])
                widget.setWordWrap(True)
                style = option.get("Style", {})
                if "FontSize" in style:
                    widget.setStyleSheet(f"font-size: {style['FontSize']}px; color: {style.get('Color', '#000000')};")

            elif option["Type"] == "Table":
                # Create a table dynamically based on the column widget definitions
                columns = option.get("Columns", [])
                initial_rows = option.get("Initial Rows", 1)
                allow_add_rows = option.get("Allow Add Rows", False)
                allow_delete_rows = option.get("Allow Delete Rows", False)

                table = QTableWidget(initial_rows, len(columns))
                table.setHorizontalHeaderLabels([col["Label"] for col in columns])

                # Populate table rows with appropriate widgets
                for r in range(initial_rows):
                    for c, col_data in enumerate(columns):
                        widget_type = col_data["Widget"]
                        if widget_type == "Textbox":
                            editor = QLineEdit()
                            editor.setPlaceholderText(col_data.get("Hint", ""))
                            table.setCellWidget(r, c, editor)
                        elif widget_type == "Checkbox":
                            checkbox = QCheckBox()
                            table.setCellWidget(r, c, checkbox)

                def add_row():
                    row_pos = table.rowCount()
                    table.insertRow(row_pos)
                    for c, col_data in enumerate(columns):
                        widget_type = col_data["Widget"]
                        if widget_type == "Textbox":
                            editor = QLineEdit()
                            editor.setPlaceholderText(col_data.get("Hint", ""))
                            table.setCellWidget(row_pos, c, editor)
                        elif widget_type == "Checkbox":
                            checkbox = QCheckBox()
                            table.setCellWidget(row_pos, c, checkbox)

                def remove_row():
                    if table.rowCount() > 1:  # Prevent removing the last row
                        table.removeRow(table.rowCount() - 1)

                layout = QVBoxLayout()
                layout.addWidget(table)

                if allow_add_rows:
                    add_button = QPushButton("Add Row")
                    add_button.clicked.connect(add_row)
                    layout.addWidget(add_button)

                if allow_delete_rows:
                    delete_button = QPushButton("Delete Row")
                    delete_button.clicked.connect(remove_row)
                    layout.addWidget(delete_button)

                table_group = QGroupBox(option.get("Label", "Table"))
                table_group.setLayout(layout)
                widget = table_group
                table.setAlternatingRowColors(True)
                table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

                # Add row and column span for tables
                self.options_layout.addWidget(widget, row, col, row_span, col_span)

            if widget:
                alignment = Qt.AlignCenter if option.get("Style", {}).get("Align") == "Center" else Qt.AlignLeft
                # If it's not a textbox or table, just add the widget without row/column span
                if option["Type"] not in ["Textbox", "Table"]:
                    self.options_layout.addWidget(widget, row, col, alignment)

    def update_spell_options(self, current_item):
        """Update the options panel for the selected spell."""
        self.current_spell = self.l_spells.currentItem().text()

        json_path = self.spell_manager.spells[self.current_spell].json_path
        if json_path:
            with open(json_path, "r") as f:
                spell_config = json.load(f)
                self.populate_spell_options(spell_config.get("Options", {}))

    def run_spell(self):
        if not self.l_spells.currentItem():
            print("No valid spell selected.")
            return

        self.io_manager.set_settings_from_window(self)
        self.io_manager.process_files(self.current_spell)

    def dragEnterEvent(self, event):
        """Allow drag-and-drop for files and folders."""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Drag-and-drop event handler for files and folders."""
        if not self.l_spells.currentItem():
            print("No valid spell selected.")
            return

        paths = [url.toLocalFile() for url in event.mimeData().urls()]

        self.io_manager.set_settings_from_window(self)
        self.io_manager.input_dirs = paths
        self.io_manager.process_files(self.current_spell)


main_window = None


def get_main_window():
    global main_window
    if main_window is None:
        main_window = MainWindow()
    return main_window
