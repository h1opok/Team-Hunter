"""

@author: Team Mizogg
"""
import os
import random
import time
import platform
import webbrowser
import locale
import subprocess
import requests
import json
import datetime

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from bloomfilter import BloomFilter
from libs import secp256k1 as ice, team_balance, create_setting, set_settings, load_bloom
from gui import (knightrider_gui, bar_gui, win_gui, up_bloom_gui, balance_gui, show_ranges_gui,
                 range_div_gui, conversion_gui, telegram_gui, discord_gui, about_gui)

import sys
sys.path.extend(['libs', 'config', 'gui'])

from config import *

import qdarktheme

version = "0.22"

# Set system locale
locale.setlocale(locale.LC_ALL, "")

def initialize_application():
    app = QApplication(sys.argv)
    return app

# Main execution
if __name__ == "__main__":
    create_setting.create_settings_file_if_not_exists()
    app = initialize_application()
    addfind = load_bloom.load_bloom_filter()
    settings = set_settings.get_settings()

# Constants
INITIAL_WINDOW_X = 80
INITIAL_WINDOW_Y = 80
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 560

# GUIInstance: QWidget class for the main GUI interface.
class GUIInstance(QMainWindow):

    def __init__(self):
        super().__init__()

        # Set window geometry
        self.setGeometry(INITIAL_WINDOW_X, INITIAL_WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Create settings file if it doesn't exist
        create_setting.create_settings_file_if_not_exists()

        # Initialize skip_ranges as an empty list and create an instance of ShowRangesDialog.
        self.skip_ranges = []
        self.ranges_dialog = show_ranges_gui.ShowRangesDialog(self.skip_ranges)

        # Load skip ranges when the GUI starts.
        self.load_skip_ranges()

        self.initUI()

        self.theme_preference = self.get_theme_preference()
        if self.theme_preference == "dark":
            self.dark_mode_button.setText("🌞")
            self.load_dark_mode()
            self.dark_mode = True
        elif self.theme_preference == "light":
            self.dark_mode_button.setText("🌙")
            self.load_light_mode()
            self.dark_mode = False
    
    def load_global_styles(self):
        with open(f"{GLOBAL_THEME}", 'r') as css_file:
            global_qss = css_file.read()
        return global_qss

    def load_dark_mode(self):
        dark_stylesheet = self.load_global_styles()
        with open(f"{DARK_THEME}", "r") as dark_file:
            dark_stylesheet += dark_file.read()

        self.setStyleSheet(dark_stylesheet)
        qdarktheme.setup_theme("dark")

    def load_light_mode(self):
        light_stylesheet = self.load_global_styles()
        with open(f"{LIGHT_THEME}", "r") as light_file:
            light_stylesheet += light_file.read()

        self.setStyleSheet(light_stylesheet)
        qdarktheme.setup_theme("light")

    def in_skip_range(self, position):
        def is_hex(value):
            return isinstance(value, str) and all(c in '0123456789abcdefABCDEF' for c in value)

        position = str(position)

        for start, end in self.skip_ranges:
            if is_hex(start) and is_hex(end) and start <= position <= end:
                return True
        return False

    # Function to display skip ranges dialog.

    def read_ranges_from_file(file_path):
        with open(file_path, "r") as f:
            return f.read()

    def write_ranges_to_file(file_path, ranges_text):
        with open(file_path, "a") as f:
            f.write(ranges_text)

    def save_ranges(self, ranges_textedit, ranges_dialog):
        new_ranges_text = ranges_textedit.toPlainText()
        write_ranges_to_file(SKIPPED_FILE, new_ranges_text)
        ranges_dialog.accept()

    def show_ranges(self):
        ranges_text = read_ranges_from_file(SKIPPED_FILE)

        ranges_dialog = show_ranges_gui.ShowRangesDialog(self)
        ranges_dialog.setWindowTitle("Show Ranges")

        ranges_textedit = QPlainTextEdit(ranges_text)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        layout = QVBoxLayout(ranges_dialog)
        layout.addWidget(ranges_textedit)
        layout.addWidget(buttons)

        buttons.accepted.connect(lambda: self.save_ranges(ranges_textedit, ranges_dialog))
        buttons.rejected.connect(ranges_dialog.reject)

        result = ranges_dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            self.load_skip_ranges()

    # Function to load skip ranges from SKIPPED_FILE.
    def load_skip_ranges(self):
        try:
            with open(SKIPPED_FILE, "r") as f:
                self.skip_ranges = [tuple(line.strip().split(":")) for line in f]

        except FileNotFoundError:
            # Handle the case when the SKIPPED_FILE doesn't exist
            pass

    def initUI(self):
        self.setWindowIcon(QIcon(f"{IMAGES_FOLDER}/ico"))

        # Create the menu bar
        menubar = self.menuBar()

        # Define a function to create and add actions
        def add_menu_action(menu, text, function):
            action = QAction(text, self)
            action.triggered.connect(function)
            menu.addAction(action)

        # Create File menu
        file_menu = menubar.addMenu("File")
        add_menu_action(file_menu, "New Window", self.onNew)
        file_menu.addSeparator()
        add_menu_action(file_menu, "Load New Database", self.onOpen)
        add_menu_action(file_menu, "Update Database", self.update_action_run)
        file_menu.addSeparator()
        add_menu_action(file_menu, "Quit", self.exit_app)

        # Create Settings menu
        settings_menu = menubar.addMenu("Settings")
        add_menu_action(settings_menu, "Telegram", self.open_telegram_settings)
        add_menu_action(settings_menu, "Discord", self.open_discord_settings)

        # Create Tools menu
        tools_menu = menubar.addMenu("Tools")
        add_menu_action(tools_menu, "Check Balance", self.balcheck)
        add_menu_action(tools_menu, "Conversion Tools", self.conv_check)
        add_menu_action(tools_menu, "Range Divsion", self.range_check)
        add_menu_action(tools_menu, "16x16", self.load_16x16)

        # Create Help menu
        help_menu = menubar.addMenu("Help")
        add_menu_action(help_menu, "Mizogg Website", self.open_website)
        add_menu_action(help_menu, "Help Telegram Group", self.open_telegram)
        add_menu_action(help_menu, "About", self.about)

        # Set up the main content area
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)
        self.setWindowTitle("Hunter QT")

        labels_info = [
            {"text": f"Made by Mizogg & Firehawk52", "object_name": "madeby"},
            {"text": f"Version {version}", "object_name": "version"},
            {"text": "© mizogg.co.uk 2018 - 2023", "object_name": "copyright"},
            {
                "text": f"Running Python {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}",
                "object_name": "versionpy",
            },
        ]

        dot_labels = [QLabel("●", objectName=f"dot{i}") for i in range(1, 4)]

        credit_label = QHBoxLayout()
        credit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for info in labels_info:
            label = QLabel(info["text"])
            label.setObjectName(info["object_name"])
            credit_label.addWidget(label)
            if dot_labels:
                dot_label = dot_labels.pop(0)
                credit_label.addWidget(dot_label)

        labels_layout = QHBoxLayout()

        
        # Create the self.add_count_label
        self.add_count_label = QLabel(self.count_addresses(), objectName="count_addlabel", alignment=Qt.AlignmentFlag.AlignLeft)

        # Create title_label
        title_label = QLabel("🌟 Hunter QT 🌟", objectName="titlelabel", alignment=Qt.AlignmentFlag.AlignCenter)

        # Add labels to the labels_layout
        labels_layout.addWidget(title_label)

        # Create a QPushButton for dark mode toggle
        self.dark_mode_button = QPushButton(self)
        self.dark_mode_button.setFixedSize(30, 30)
        self.dark_mode_button.clicked.connect(self.toggle_theme)
        self.dark_mode_button.setChecked(True if self.get_theme_preference() == "dark" else False)

        self.dark_mode = self.get_theme_preference() == "dark"
        self.load_dark_mode() if self.dark_mode else self.load_light_mode()
        self.toggle_theme()

        dark_mode_layout = QHBoxLayout()
        dark_mode_layout.addWidget(self.add_count_label)
        dark_mode_layout.addStretch()
        dark_mode_layout.addWidget(self.dark_mode_button)

        # Create start and stop buttons
        start_button = QPushButton("Start", self)
        start_button.setObjectName("startButton")
        start_button.clicked.connect(self.start)
        start_button.setFixedWidth(100)

        stop_button = QPushButton("Stop", self)
        stop_button.setObjectName("stopButton")
        stop_button.clicked.connect(self.stop)
        stop_button.setFixedWidth(100)

        # Add buttons and stretchable space to the layout
        start_stop_layout = QHBoxLayout()
        start_stop_layout.addStretch(1)
        start_stop_layout.addWidget(start_button)
        start_stop_layout.addWidget(stop_button)
        start_stop_layout.addStretch(1)

        # Show power menu
        power_label = QLabel("Show", self)
        power_label.setObjectName("powerLabel")

        self.format_combo_box_POWER = QComboBox(self)
        self.format_combo_box_POWER.addItems(
            ["1", "128", "256", "512", "1024", "2048", "4096", "8192", "16384"]
        )

        select_power_layout = QHBoxLayout()
        select_power_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        select_power_layout.addWidget(power_label)
        select_power_layout.addWidget(self.format_combo_box_POWER)

        # Create input fields and buttons for skip range
        self.add_range_button = QPushButton("➕ Skip Current Range in Scan", self)
        self.add_range_button.setObjectName("addRange")
        self.add_range_button.clicked.connect(self.add_range_from_input)

        self.show_ranges_button = QPushButton("👀 Show Skipped Ranges", self)
        self.show_ranges_button.setObjectName("showRange")
        self.show_ranges_button.clicked.connect(self.show_ranges)

        skip_range_layout = QHBoxLayout()
        skip_range_layout.addWidget(self.add_range_button)
        skip_range_layout.addWidget(self.show_ranges_button)

        options_layout2 = QHBoxLayout()

        #Key Space Range
        self.keyspaceLabel = QLabel("Key Space:", self)
        options_layout2.addWidget(self.keyspaceLabel)

        self.start_edit = QLineEdit("20000000000000000")
        self.end_edit = QLineEdit("3ffffffffffffffff")

        self.keyspace_slider = QSlider(Qt.Orientation.Horizontal)
        self.keyspace_slider.setMinimum(1)
        self.keyspace_slider.setMaximum(256)
        self.keyspace_slider.setValue(66)

        keyspacerange_layout = QVBoxLayout()
        keyspacerange_layout.addWidget(self.start_edit)
        keyspacerange_layout.addWidget(self.end_edit)
        keyspacerange_layout.addWidget(self.keyspace_slider)

        options_layout2.addLayout(keyspacerange_layout)
        options_layout2.setStretchFactor(keyspacerange_layout, 5)

        self.keyspace_slider.valueChanged.connect(self.update_keyspace_range)
        
        # Bits
        self.bitsLabel = QLabel("Bits:", self)
        options_layout2.addWidget(self.bitsLabel)

        self.bitsLineEdit = QLineEdit(self)
        self.bitsLineEdit.setText("66")
        self.bitsLineEdit.textChanged.connect(self.updateSliderAndRanges)
        options_layout2.addWidget(self.bitsLineEdit)
        options_layout2.setStretchFactor(self.bitsLineEdit, 1)

        dec_label = QLabel(" Dec value :")
        self.value_edit_dec = QLineEdit()
        self.value_edit_dec.setReadOnly(True)

        hex_label = QLabel(" HEX value :")
        self.value_edit_hex = QLineEdit()
        self.value_edit_hex.setReadOnly(True)

        current_scan_layout = QHBoxLayout()
        current_scan_layout.addWidget(dec_label)
        current_scan_layout.addWidget(self.value_edit_dec)
        current_scan_layout.addWidget(hex_label)
        current_scan_layout.addWidget(self.value_edit_hex)

        # Create radio buttons for selection
        button_labels = ["Random", "Sequence", "Reverse"]
        button_objects = []

        for label in button_labels:
            button = QRadioButton(label)
            button_objects.append(button)

        button_objects[0].setChecked(True)

        # Assign these buttons to self attributes
        self.random_button = button_objects[0]
        self.sequence_button = button_objects[1]
        self.reverse_button = button_objects[2]

        # Create checkboxes for view settings
        checkbox_labels = ["DEC", "HEX", "Compressed", "Uncompressed", "P2SH", "Bech32", "Stop if winner found", "Balance Check (Compressed Only)"]
        checkbox_objects = []

        checkbox_width = 200

        for label in checkbox_labels:
            checkbox = QCheckBox(label)
            checkbox.setFixedWidth(checkbox_width)
            checkbox_objects.append(checkbox)

        self.dec_checkbox, self.hex_checkbox, self.compressed_checkbox, self.uncompressed_checkbox, self.p2sh_checkbox, self.bech32_checkbox, self.win_checkbox, self.balance_check_checkbox = checkbox_objects[0:]

        self.balance_check_checkbox.setChecked(False)  # Set the initial state
        self.balance_check_checkbox.stateChanged.connect(self.handle_balance_check_toggle)

        # Set checkboxes to be checked by default
        checkboxes_to_check = [self.dec_checkbox, self.hex_checkbox, self.compressed_checkbox, self.uncompressed_checkbox, self.p2sh_checkbox, self.bech32_checkbox]
        for checkbox in checkboxes_to_check:
            checkbox.setChecked(True)

        self.win_checkbox.setChecked(False)

        # Create a vertical line as a divider
        divider = QFrame(frameShape=QFrame.Shape.VLine, frameShadow=QFrame.Shadow.Sunken)

        # Create a layout for the radio buttons and checkboxes on the same line
        radio_and_checkbox_layout = QHBoxLayout()

        widgets = [
            self.random_button, self.sequence_button, self.reverse_button, divider,
            self.dec_checkbox, self.hex_checkbox, self.compressed_checkbox,
            self.uncompressed_checkbox, self.p2sh_checkbox, self.bech32_checkbox,
            self.win_checkbox, self.balance_check_checkbox
        ]

        for widget in widgets:
            radio_and_checkbox_layout.addWidget(widget)

        # Set up the main layout
        layouts = [
            dark_mode_layout, labels_layout, start_stop_layout, select_power_layout,
            radio_and_checkbox_layout, options_layout2, skip_range_layout, current_scan_layout
        ]

        for l in layouts:
            layout.addLayout(l)

        # Create layout for displaying key statistics
        
        # Create QLineEdit widgets with common properties
        def create_line_edit(read_only=True, text="0"):
            line_edit = QLineEdit()
            line_edit.setReadOnly(read_only)
            line_edit.setText(text)
            return line_edit

        # Initialize line edit widgets
        self.found_keys_scanned_edit = create_line_edit()
        self.total_keys_scanned_edit = create_line_edit()
        self.keys_per_sec_edit = create_line_edit(False, "")

        # Define labels and corresponding QLineEdit widgets
        labels_and_edits = [
            ("Found", self.found_keys_scanned_edit),
            ("Total keys scanned:", self.total_keys_scanned_edit),
            ("Keys per second:", self.keys_per_sec_edit)
        ]

        keys_layout = QHBoxLayout()

        for label_text, edit_widget in labels_and_edits:
            label = QLabel(label_text)
            keys_layout.addWidget(label)
            keys_layout.addWidget(edit_widget)

        layout.addLayout(keys_layout)

        # Create progress bar
        progress_layout_text = QHBoxLayout()
        progress_layout_text.setObjectName("progressbar")
        progress_label = QLabel("progress %")

        self.progress_bar = bar_gui.CustomProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)

        progress_layout_text.addWidget(progress_label)
        progress_layout_text.addWidget(self.progress_bar)

        layout.addLayout(progress_layout_text)

        # Create layout for displaying addresses
        self.address_layout_ = QGridLayout()
        self.priv_label = QLabel("DEC Keys: ")
        self.priv_text = QTextEdit(self)
        self.HEX_label = QLabel("HEX Keys: ")
        self.HEX_text = QTextEdit(self)
        self.comp_label = QLabel("Compressed Address: ")
        self.comp_text = QTextEdit(self)
        self.uncomp_label = QLabel("Uncompressed Address: ")
        self.uncomp_text = QTextEdit(self)
        self.p2sh_label = QLabel("p2sh Address: ")
        self.p2sh_text = QTextEdit(self)
        self.bech32_label = QLabel("bech32 Address: ")
        self.bech32_text = QTextEdit(self)
        self.address_layout_.addWidget(self.priv_label, 1, 0)
        self.address_layout_.addWidget(self.priv_text, 2, 0)
        self.address_layout_.addWidget(self.HEX_label, 1, 1)
        self.address_layout_.addWidget(self.HEX_text, 2, 1)
        self.address_layout_.addWidget(self.comp_label, 1, 2)
        self.address_layout_.addWidget(self.comp_text, 2, 2)
        self.address_layout_.addWidget(self.uncomp_label, 1, 3)
        self.address_layout_.addWidget(self.uncomp_text, 2, 3)
        self.address_layout_.addWidget(self.p2sh_label, 1, 4)
        self.address_layout_.addWidget(self.p2sh_text, 2, 4)
        self.address_layout_.addWidget(self.bech32_label, 1, 5)
        self.address_layout_.addWidget(self.bech32_text, 2, 5)

        layout.addLayout(self.address_layout_)

        # Connect the stateChanged signal of each checkbox to the toggle_visibility function
        self.dec_checkbox.stateChanged.connect(
            lambda: self.toggle_visibility(
                self.dec_checkbox, self.priv_label, self.priv_text
            )
        )
        self.hex_checkbox.stateChanged.connect(
            lambda: self.toggle_visibility(
                self.hex_checkbox, self.HEX_label, self.HEX_text
            )
        )
        self.compressed_checkbox.stateChanged.connect(
            lambda: self.toggle_visibility(
                self.compressed_checkbox, self.comp_label, self.comp_text
            )
        )
        self.uncompressed_checkbox.stateChanged.connect(
            lambda: self.toggle_visibility(
                self.uncompressed_checkbox, self.uncomp_label, self.uncomp_text
            )
        )
        self.p2sh_checkbox.stateChanged.connect(
            lambda: self.toggle_visibility(
                self.p2sh_checkbox, self.p2sh_label, self.p2sh_text
            )
        )
        self.bech32_checkbox.stateChanged.connect(
            lambda: self.toggle_visibility(
                self.bech32_checkbox, self.bech32_label, self.bech32_text
            )
        )

        # Initially, set the visibility based on the checkbox's initial state
        self.toggle_visibility(self.dec_checkbox, self.priv_label, self.priv_text)
        self.toggle_visibility(self.hex_checkbox, self.HEX_label, self.HEX_text)
        self.toggle_visibility(
            self.compressed_checkbox, self.comp_label, self.comp_text
        )
        self.toggle_visibility(
            self.uncompressed_checkbox, self.uncomp_label, self.uncomp_text
        )
        self.toggle_visibility(self.p2sh_checkbox, self.p2sh_label, self.p2sh_text)
        self.toggle_visibility(
            self.bech32_checkbox, self.bech32_label, self.bech32_text
        )

        # Create KnightRiderWidget for visual feedback
        self.knightRiderWidget = knightrider_gui.KnightRiderWidget(self)
        self.knightRiderWidget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.knightRiderWidget.setMinimumHeight(20)

        self.knightRiderLayout = QHBoxLayout()
        self.knightRiderLayout.setContentsMargins(10, 15, 10, 10)
        self.knightRiderLayout.addWidget(self.knightRiderWidget)

        self.knightRiderGroupBox = QGroupBox(self)
        self.knightRiderGroupBox.setObjectName("knightrider")
        self.knightRiderGroupBox.setLayout(self.knightRiderLayout)

        layout.addWidget(self.knightRiderGroupBox)

        # Create checkbox for custom Telegram credentials
        self.use_telegram_credentials_checkbox = QCheckBox("Use Custom Telegram Credentials (edit in settings menu)")
        self.use_telegram_credentials_checkbox.setChecked(False)
        self.use_discord_credentials_checkbox = QCheckBox("Use Custom Discord Credentials (edit in settings menu)")
        self.use_discord_credentials_checkbox.setChecked(False)

        custom_credentials_layout = QHBoxLayout()
        custom_credentials_layout.addWidget(self.use_telegram_credentials_checkbox)
        custom_credentials_layout.addWidget(self.use_discord_credentials_checkbox)
        layout.addLayout(custom_credentials_layout)
        layout.addLayout(credit_label)

        self.counter = 0
        self.timer = time.time()

        self.start_edit.setText(START_ADDRESS)
        self.end_edit.setText(END_ADDRESS)

    def handle_balance_check_toggle(self, state):
        if state == 2:
            # "Balance Check" checkbox is checked
            self.dec_checkbox.setChecked(False)
            self.hex_checkbox.setChecked(False)
            self.compressed_checkbox.setChecked(True)
            self.uncompressed_checkbox.setChecked(False)
            self.p2sh_checkbox.setChecked(False)
            self.bech32_checkbox.setChecked(False)
            self.format_combo_box_POWER.setCurrentIndex(0)
            self.format_combo_box_POWER.setEnabled(False)
        else:
            # "Balance Check" checkbox is unchecked
            self.dec_checkbox.setChecked(True)
            self.hex_checkbox.setChecked(True)
            self.compressed_checkbox.setChecked(True)
            self.uncompressed_checkbox.setChecked(True)
            self.p2sh_checkbox.setChecked(True)
            self.bech32_checkbox.setChecked(True)
            self.format_combo_box_POWER.setEnabled(True)

    def onNew(self):
        if platform.system() == "Windows":
            creation_flags = subprocess.CREATE_NO_WINDOW
        else:
            creation_flags = 0

        current_script = os.path.basename(__file__)
        python_cmd = [sys.executable, current_script]
        subprocess.run(python_cmd, creationflags=creation_flags)

    def onOpen(self):
        global addfind, BTC_BF_FILE
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "BF Files (*.bf);;Text Files (*.txt)"
        )

        if not filePath:  # If no file is selected, just return
            return

        try:
            if filePath.endswith(".bf"):
                with open(filePath, "rb") as fp:
                    addfind = BloomFilter.load(fp)
            elif filePath.endswith(".txt"):
                with open(filePath, "r") as file:
                    addfind = file.read().split()
            else:
                raise ValueError("Unsupported file type")
            
            BTC_BF_FILE = filePath
            
        except Exception as e:
            error_message = f"Error loading file: {str(e)}"
            QMessageBox.critical(self, "Error", error_message)
            return

        # Show a popup message to indicate that the file has been loaded
        success_message = f"File loaded: {filePath}"
        QMessageBox.information(self, "File Loaded", success_message)

        # Update the label with the total BTC addresses loaded
        self.add_count_label.setText(self.count_addresses(BTC_BF_FILE))

    def exit_app(self):
        QApplication.quit()

    def open_telegram_settings(self):
        settings_dialog = telegram_gui.Settings_telegram_Dialog(self)
        settings_dialog.exec()
    
    def open_discord_settings(self):
        settings_dialog = discord_gui.Settings_discord_Dialog(self)
        settings_dialog.exec()

    def balcheck(self):
        balance_dialog = balance_gui.BalanceDialog(self)
        balance_dialog.exec()
        
    def conv_check(self):
        conv_dialog = conversion_gui.ConversionDialog(self)
        conv_dialog.exec()
        
    def range_check(self):
        range_dialog = range_div_gui.RangeDialog(self)
        range_dialog.exec()
        
    def load_16x16(self):
        try:
            subprocess.run(['python', '16x16.py'], check=True)
        except subprocess.CalledProcessError:
            QMessageBox.critical(self, "Error", "Failed to run '16x16.py'")

    def update_action_run(self):
        update_dialog = up_bloom_gui.UpdateBloomFilterDialog(self)
        update_dialog.exec()

    def about(self):
        about_dialog = about_gui.AboutDialog(self)
        about_dialog.exec()

    def open_website(self):
        webbrowser.open("https://mizogg.co.uk")

    def open_telegram(self):
        webbrowser.open("https://t.me/CryptoCrackersUK")

    def count_addresses(self, btc_bf_file=None):
        if btc_bf_file is None:
            btc_bf_file = BTC_BF_FILE       
        try:
            last_updated = os.path.getmtime(BTC_BF_FILE)
            last_updated_datetime = datetime.datetime.fromtimestamp(last_updated)
            now = datetime.datetime.now()
            delta = now - last_updated_datetime

            if delta < datetime.timedelta(days=1):
                hours, remainder = divmod(delta.seconds, 3600)
                minutes = remainder // 60

                time_units = []

                if hours > 0:
                    time_units.append(f"{hours} {'hour' if hours == 1 else 'hours'}")

                if minutes > 0:
                    time_units.append(f"{minutes} {'minute' if minutes == 1 else 'minutes'}")

                time_str = ', '.join(time_units)

                if time_units:
                    message = f'Currently checking <b>{locale.format_string("%d", len(addfind), grouping=True)}</b> addresses. The database is <b>{time_str}</b> old.'
                else:
                    message = f'Currently checking <b>{locale.format_string("%d", len(addfind), grouping=True)}</b> addresses. The database is <b>less than a minute</b> old.'
            elif delta < datetime.timedelta(days=2):
                hours, remainder = divmod(delta.seconds, 3600)
                minutes = remainder // 60

                time_str = f'1 day'

                if hours > 0:
                    time_str += f', {hours} {"hour" if hours == 1 else "hours"}'

                if minutes > 0:
                    time_str += f', {minutes} {"minute" if minutes == 1 else "minutes"}'

                message = f'Currently checking <b>{locale.format_string("%d", len(addfind), grouping=True)}</b> addresses. The database is <b>{time_str}</b> old.'
            else:
                message = f'Currently checking <b>{locale.format_string("%d", len(addfind), grouping=True)}</b> addresses. The database is <b>{delta.days} days</b> old.'
        except FileNotFoundError:
            message = f'Currently checking <b>{locale.format_string("%d", len(addfind), grouping=True)}</b> addresses.'

        return message

    def toggle_visibility(self, checkbox, label_widget, text_widget):
        label_widget.setVisible(checkbox.isChecked())
        text_widget.setVisible(checkbox.isChecked())


    def get_theme_preference(self):
        return set_settings.get_settings().get("theme", "dark")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.load_dark_mode() if self.dark_mode else self.load_light_mode()
        self.dark_mode_button.setText("🌞" if self.dark_mode else "🌙")

    def add_range_from_input(self):
        start_str = self.start_edit.text()
        end_str = self.end_edit.text()

        if start_str and end_str:
            # Ensure the input values have the "0x" prefix
            start = "0x" + start_str if not start_str.startswith("0x") else start_str
            end = "0x" + end_str if not end_str.startswith("0x") else end_str

            # Check for duplicates
            if (start, end) in self.skip_ranges:
                QMessageBox.information(
                    self, "Duplicate Range", "Range is already added."
                )
                return

            # Add the range to the skip_ranges list
            self.skip_ranges.append((start, end))

            # Update SKIPPED_FILE
            with open(SKIPPED_FILE, "a") as f:
                f.write(f"{start}:{end}\n")

            # Clear the input fields
            self.start_edit.clear()
            self.end_edit.clear()
            self.add_range_button.setText(f"Range Added: {start} - {end}")
            QTimer.singleShot(
                5000,
                lambda: self.add_range_button.setText("➕ Skip Current Range in Scan"),
            )

    def update_keyspace_range(self, value):
        start_range = hex(2 ** (value - 1))[2:]
        end_range = hex(2 ** value - 1)[2:]
        self.start_edit.setText(start_range)
        self.end_edit.setText(end_range)
        self.bitsLineEdit.setText(str(value))


    def updateSliderAndRanges(self, text):
        try:
            bits = int(text)
            # Ensure bits is within the valid range
            bits = max(0, min(bits, 256))  # Adjust the range as needed
            start_range = hex(2 ** bits)
            end_range = hex(2 ** (bits + 1) - 1)
            
            self.keyspace_slider.setValue(bits)
            self.start_edit.setText(start_range)
            self.end_edit.setText(end_range)
        except ValueError:
            range_message = "Range should be in Bit 1-256 "
            QMessageBox.information(self, "Range Error", range_message)

    def send_to_discord(self, text):
        settings = set_settings.get_settings()
        webhook_url = settings.get("webhook_url", "").strip()
        print(f'Webhook URL: {webhook_url}')
        headers = {'Content-Type': 'application/json'}

        payload = {
            'content': text
        }

        try:
            response = requests.post(webhook_url, json=payload, headers=headers)

            if response.status_code == 204:
                print('Message sent to Discord successfully!')
            else:
                print(f'Failed to send message to Discord. Status Code: {response.status_code}')
        except Exception as e:
            print(f'Error sending message to Discord: {str(e)}')


    def send_to_telegram(self, text):
        settings = set_settings.get_settings()
        apiToken = settings.get("token", "").strip()
        chatID = settings.get("chatid", "").strip()

        if not apiToken or not chatID:
            token_message = "No token or ChatID found in CONFIG_FILE"
            QMessageBox.information(self, "No token or ChatID", token_message)
            return

        apiURL = f"https://api.telegram.org/bot{apiToken}/sendMessage"

        try:
            response = requests.post(apiURL, json={"chat_id": chatID, "text": text})
            response.raise_for_status()  # Raise an error for HTTP errors
        except requests.exceptions.HTTPError as errh:
            error_message = f"HTTP Error: {errh}"
            QMessageBox.critical(self, "Error", error_message)
        except Exception as e:
            error_message = f"Telegram error: {str(e)}"
            QMessageBox.critical(self, "Error", error_message)

    # Helper function to update the skipped ranges file
    
    def update_skipped_file(self):
        with open(SKIPPED_FILE, "w") as f:
            for start, end in self.skip_ranges:
                f.write(f"{start:016x}:{end:016x}\n")

    def show_ranges(self):
        try:
            # Open a dialog to show the list of skipped ranges
            ranges_dialog = show_ranges_gui.ShowRangesDialog(self.skip_ranges)
            result = ranges_dialog.exec()

            if result == QDialog.DialogCode.Accepted:
                # Update the skipped ranges list with any changes made in the dialog
                self.skip_ranges = ranges_dialog.get_ranges()
                self.update_skipped_file()

        except Exception as e:
            error_message = f"An error occurred while showing ranges: {str(e)}"
            QMessageBox.critical(self, "Error", error_message)

    def start(self):
        power_format = self.format_combo_box_POWER.currentText()
        try:
            self.power_format = int(power_format)
            start_value = int(self.start_edit.text(), 16)
            end_value = int(self.end_edit.text(), 16)
            self.total_steps = end_value - start_value
            self.scanning = True

            # Determine scanning mode (Random, Sequence, or Reverse)
            if self.random_button.isChecked():
                self.timer = QTimer(self)
                self.timer.timeout.connect(lambda: self.update_display_random(start_value, end_value))
            elif self.sequence_button.isChecked():
                self.current = start_value
                self.timer = QTimer(self)
                self.timer.timeout.connect(lambda: self.update_display_sequence(start_value, end_value))
            elif self.reverse_button.isChecked():
                self.current = end_value
                self.timer = QTimer(self)
                self.timer.timeout.connect(lambda: self.update_display_reverse(start_value, end_value))

            self.timer.start()
            self.start_time = time.time()
            self.timer.timeout.connect(self.update_keys_per_sec)
            self.knightRiderWidget.startAnimation()
        except Exception as e:
            error_message = f"Ranges empty please Type a Start and Stop: {str(e)}"
            QMessageBox.critical(self, "Error", error_message)

    def stop(self):
        if isinstance(self.timer, QTimer):
            self.timer.stop()
            self.worker_finished("Recovery Finished")

    # This function handles the completion of the recovery process
    def worker_finished(self, result):
        if self.scanning:
            QMessageBox.information(self, "Recovery Finished", "Done")
        self.scanning = False
        self.knightRiderWidget.stopAnimation()

    # This function generates cryptographic keys and addresses
    def generate_crypto(self):
        dec_keys, HEX_keys, uncomp_keys, comp_keys, p2sh_keys, bech32_keys = [], [], [], [], [], []
        found = int(self.found_keys_scanned_edit.text())
        startPrivKey = self.num

        for i in range(0, self.power_format):
            dec = int(startPrivKey)
            HEX = f"{dec:016x}"

            if self.balance_check_checkbox.isChecked():
                caddr = ice.privatekey_to_address(0, True, dec)
                confirmed_balance_btc, received_btc, unconfirmed_balance_btc, tx_count = team_balance.check_balance(caddr)
                BTCOUT = f"""
    Decimal Private Key: {dec}
    Hexadecimal Private Key: {HEX}
    BTC Address: {caddr}
    >> Confirmed Balance: {confirmed_balance_btc:.8f} BTC     >> Unconfirmed Balance: {unconfirmed_balance_btc:.8f} BTC
    >> Total Received: {received_btc:.8f} BTC                 >> Transaction Count: {tx_count}
    """

                self.value_edit_dec.setText(str(dec))
                self.value_edit_hex.setText(HEX)
                self.comp_text.setText(BTCOUT)

                if confirmed_balance_btc > 0:
                    found += 1
                    self.found_keys_scanned_edit.setText(str(found))
                    WINTEXT = f"""
    Decimal Private Key: {dec}
    Hexadecimal Private Key: {HEX}
    BTC Address: {caddr}
    >> Confirmed Balance: {confirmed_balance_btc:.8f} BTC     >> Unconfirmed Balance: {unconfirmed_balance_btc:.8f} BTC
    >> Total Received: {received_btc:.8f} BTC                 >> Transaction Count: {tx_count}
    """

                    try:
                        with open(WINNER_COMPRESSED, "a") as f:
                            f.write(WINTEXT)
                    except FileNotFoundError:
                        os.makedirs(os.path.dirname(WINNER_COMPRESSED), exist_ok=True)

                        # Then create the file and write WINTEXT to it
                        with open(WINNER_COMPRESSED, "w") as f:
                            f.write(WINTEXT)

                    if self.use_telegram_credentials_checkbox.isChecked():
                        self.send_to_telegram(WINTEXT)
                    if self.use_discord_credentials_checkbox.isChecked():
                        self.send_to_discord(WINTEXT)
                    if self.win_checkbox.isChecked():
                        winner_dialog = win_gui.WinnerDialog(WINTEXT, self)
                        winner_dialog.exec()

            else:
                dec_keys.append(dec)
                HEX_keys.append(HEX)

                if self.compressed_checkbox.isChecked():
                    caddr = ice.privatekey_to_address(0, True, dec)
                    comp_keys.append(caddr)

                    if caddr in addfind:
                        found += 1
                        self.found_keys_scanned_edit.setText(str(found))
                        WINTEXT = f"\n {caddr} \n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX}  \n"

                        try:
                            with open(WINNER_COMPRESSED, "a") as f:
                                f.write(WINTEXT)
                        except FileNotFoundError:
                            os.makedirs(os.path.dirname(WINNER_COMPRESSED), exist_ok=True)

                            # Then create the file and write WINTEXT to it
                            with open(WINNER_COMPRESSED, "w") as f:
                                f.write(WINTEXT)
                        if self.use_telegram_credentials_checkbox.isChecked():
                            self.send_to_telegram(WINTEXT)
                        if self.use_discord_credentials_checkbox.isChecked():
                            self.send_to_discord(WINTEXT)
                        if self.win_checkbox.isChecked():
                            winner_dialog = win_gui.WinnerDialog(WINTEXT, self)
                            winner_dialog.exec()

                if self.uncompressed_checkbox.isChecked():
                    uaddr = ice.privatekey_to_address(0, False, dec)
                    uncomp_keys.append(uaddr)

                    if uaddr in addfind:
                        found += 1
                        self.found_keys_scanned_edit.setText(str(found))
                        WINTEXT = f"\n {uaddr} \n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX}  \n"

                        try:
                            with open(WINNER_UNCOMPRESSED, "a") as f:
                                f.write(WINTEXT)
                        except FileNotFoundError:
                            os.makedirs(os.path.dirname(WINNER_UNCOMPRESSED), exist_ok=True)

                            # Then create the file and write WINTEXT to it
                            with open(WINNER_UNCOMPRESSED, "w") as f:
                                f.write(WINTEXT)

                        if self.use_telegram_credentials_checkbox.isChecked():
                            self.send_to_telegram(WINTEXT)
                        if self.use_discord_credentials_checkbox.isChecked():
                            self.send_to_discord(WINTEXT)
                        if self.win_checkbox.isChecked():
                            winner_dialog = win_gui.WinnerDialog(WINTEXT, self)
                            winner_dialog.exec()

                if self.p2sh_checkbox.isChecked():
                    p2sh = ice.privatekey_to_address(1, True, dec)
                    p2sh_keys.append(p2sh)

                    if p2sh in addfind:
                        found += 1
                        self.found_keys_scanned_edit.setText(str(found))
                        WINTEXT = f"\n {p2sh}\nDecimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX} \n"

                        try:
                            with open(WINNER_P2SH, "a") as f:
                                f.write(WINTEXT)
                        except FileNotFoundError:
                            os.makedirs(os.path.dirname(WINNER_P2SH), exist_ok=True)

                            # Then create the file and write WINTEXT to it
                            with open(WINNER_P2SH, "w") as f:
                                f.write(WINTEXT)

                        if self.use_telegram_credentials_checkbox.isChecked():
                            self.send_to_telegram(WINTEXT)
                        if self.use_discord_credentials_checkbox.isChecked():
                            self.send_to_discord(WINTEXT)
                        if self.win_checkbox.isChecked():
                            winner_dialog = win_gui.WinnerDialog(WINTEXT, self)
                            winner_dialog.exec()

                if self.bech32_checkbox.isChecked():
                    bech32 = ice.privatekey_to_address(2, True, dec)
                    bech32_keys.append(bech32)

                    if bech32 in addfind:
                        found += 1
                        self.found_keys_scanned_edit.setText(str(found))
                        WINTEXT = f"\n {bech32}\n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX} \n"

                        try:
                            with open(WINNER_BECH32, "a") as f:
                                f.write(WINTEXT)
                        except FileNotFoundError:
                            os.makedirs(os.path.dirname(WINNER_BECH32), exist_ok=True)

                            # Then create the file and write WINTEXT to it
                            with open(WINNER_BECH32, "w") as f:
                                f.write(WINTEXT)

                        if self.use_telegram_credentials_checkbox.isChecked():
                            self.send_to_telegram(WINTEXT)
                        if self.use_discord_credentials_checkbox.isChecked():
                            self.send_to_discord(WINTEXT)
                        if self.win_checkbox.isChecked():
                            winner_dialog = win_gui.WinnerDialog(WINTEXT, self)
                            winner_dialog.exec()

            startPrivKey += 1

        if not self.balance_check_checkbox.isChecked():
            self.value_edit_dec.setText(str(dec))
            self.value_edit_hex.setText(HEX)
            self.priv_text.setText("\n".join(map(str, dec_keys)))
            self.HEX_text.setText("\n".join(HEX_keys))
            self.uncomp_text.setText("\n".join(uncomp_keys))
            self.comp_text.setText("\n".join(comp_keys))
            self.p2sh_text.setText("\n".join(p2sh_keys))
            self.bech32_text.setText("\n".join(bech32_keys))

        def load_config():
            try:
                with open(CONFIG_FILE, "r") as file:
                    return json.load(file)
            except FileNotFoundError:
                return {}

        def save_config(config_data):
            with open(CONFIG_FILE, "w") as file:
                json.dump(config_data, file, indent=4)

        def update_config_address(start_address, end_address):
            config_data = load_config()
            config_data["Addresses"] = {
                "START_ADDRESS": start_address,
                "END_ADDRESS": end_address
            }
            save_config(config_data)

        # Update START_ADDRESS or END_ADDRESS based on button checked
        if self.sequence_button.isChecked():
            update_config_address(HEX, None)
        elif self.reverse_button.isChecked():
            update_config_address(None, HEX)

    def update_display_random(self, start, end):
        if not self.scanning:
            self.timer.stop()
            return

        def is_address_in_skip(address, skip_ranges):
            address = int(address, 16) if isinstance(address, str) else address
            for s, e in skip_ranges:
                if int(s, 16) <= address <= int(e, 16):
                    return True
            return False

        def find_valid_key():
            rng = random.SystemRandom()
            for _ in range(100):
                self.num = rng.randint(start, end)
                if not is_address_in_skip(self.num, self.skip_ranges):
                    return True
            return False

        # Continue until a valid key is found
        while not find_valid_key():
            pass

        max_value = 10000
        scaled_current_step = min(
            max_value, max(0, int(self.num * max_value / (end - start)))
        )

        self.progress_bar.setMaximum(max_value)
        self.progress_bar.setValue(scaled_current_step)
        self.generate_crypto()
        self.counter += self.power_format

    # Modify update_display_sequence function
    def update_display_sequence(self, start, end):
        self.num = self.current
        if self.current > int(self.end_edit.text(), 16):
            self.timer.stop()
            self.scanning = False
            return

        def is_address_in_skip(address, skip_ranges):
            if isinstance(address, str):
                address = int(address, 16)

            for start, end in skip_ranges:
                if int(start, 16) <= address <= int(end, 16):
                    return True
            return False

        total_steps = end - start
        max_value = 10000
        update_interval = 1  # Update every 1 addresses

        while self.num < end and self.scanning:
            if not is_address_in_skip(self.num, self.skip_ranges):
                current_step = self.num - start
                scaled_current_step = (current_step / total_steps) * max_value
                self.progress_bar.setMaximum(max_value)
                self.progress_bar.setValue(int(scaled_current_step))
                self.generate_crypto()
                self.update_keys_per_sec()
                self.current += self.power_format
                self.counter += self.power_format

            # Increment self.num to move to the next address
            self.num += self.power_format

            # Check if it's time to update the UI
            if self.num % update_interval == 0:
                # Update the UI and allow it to process events
                QApplication.processEvents()

        # Ensure self.num doesn't exceed end
        self.num = end

        # Make sure to set self.scanning to False when the scan is completed
        self.scanning = False

    # Modify update_display_reverse function
    def update_display_reverse(self, start, end):
        self.num = self.current
        if self.current < int(self.start_edit.text(), 16):
            self.timer.stop()
            self.scanning = False
            return

        def is_address_in_skip(address, skip_ranges):
            if isinstance(address, str):
                address = int(address, 16)

            for start, end in skip_ranges:
                if int(start, 16) <= address <= int(end, 16):
                    return True
            return False

        total_steps = end - start
        max_value = 10000
        update_interval = 1  # Update every 1 addresses

        # Initialize a counter to keep track of processed addresses
        processed_count = 0

        while self.num >= start:
            if not is_address_in_skip(self.num, self.skip_ranges):
                current_step = end - self.num
                scaled_current_step = (current_step / total_steps) * max_value
                self.progress_bar.setMaximum(max_value)
                self.progress_bar.setValue(int(scaled_current_step))
                self.generate_crypto()
                self.update_keys_per_sec()
                self.current -= self.power_format
                self.counter += self.power_format

            # Increment self.num to move to the previous address
            self.num -= self.power_format
            processed_count += 1

            # Check if the stop button is pressed
            if not self.scanning:
                break

            # Check if it's time to update the UI
            if processed_count >= update_interval:
                processed_count = 0
                # Update the UI and allow it to process events
                QApplication.processEvents()

        # Ensure self.num doesn't go below start
        self.num = start

        # Make sure to set self.scanning to False when the scan is completed
        self.scanning = False

    # This function updates the keys per second display
    def update_keys_per_sec(self):
        elapsed_time = time.time() - self.start_time

        if elapsed_time == 0:
            keys_per_sec = 0
        else:
            keys_per_sec = self.counter / elapsed_time

        keys_per_sec = round(keys_per_sec, 2)

        total_keys_scanned_text = self.total_keys_scanned_edit.text()
        total_keys_scanned = locale.atoi(total_keys_scanned_text) + self.counter

        total_keys_scanned_formatted = locale.format_string("%d", total_keys_scanned, grouping=True)
        keys_per_sec_formatted = locale.format_string("%.2f", keys_per_sec, grouping=True)

        self.total_keys_scanned_edit.setText(total_keys_scanned_formatted)
        self.keys_per_sec_edit.setText(keys_per_sec_formatted)
        self.start_time = time.time()
        self.counter = 0


# Entry point for the application
if __name__ == "__main__":
    # Create an instance of the GUI and start the application
    gui_instance = GUIInstance()
    gui_instance.show()
    sys.exit(app.exec())
