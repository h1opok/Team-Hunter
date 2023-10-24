"""

@author: Team Mizogg
"""
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import os
import datetime
import time
import random
import requests
import json
import base58, binascii
from bloomfilter import BloomFilter
from libs import secp256k1 as ice, load_bloom
from funct import (bar_gui, win_gui, up_bloom_gui, show_ranges_gui, telegram_gui, discord_gui)
import sys
sys.path.extend(['libs', 'config', 'funct'])

from config import *
import locale

addfind = load_bloom.load_bloom_filter()

class GUIInstance(QMainWindow):

    def __init__(self):
        super().__init__()
        self.skip_ranges = []
        self.ranges_dialog = show_ranges_gui.ShowRangesDialog(self.skip_ranges)
        self.load_skip_ranges()
        self.initUI()

    def in_skip_range(self, position):
        def is_hex(value):
            return isinstance(value, str) and all(c in '0123456789abcdefABCDEF' for c in value)

        position = str(position)

        for start, end in self.skip_ranges:
            if is_hex(start) and is_hex(end) and start <= position <= end:
                return True
        return False

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
    def load_skip_ranges(self):
        try:
            with open(SKIPPED_FILE, "r") as f:
                self.skip_ranges = [tuple(line.strip().split(":")) for line in f]

        except FileNotFoundError:
            pass

    def initUI(self):
        menubar = self.menuBar()
        def add_menu_action(menu, text, function):
            action = QAction(text, self)
            action.triggered.connect(function)
            menu.addAction(action)

        file_menu = menubar.addMenu("Database Option Load/Update")
        file_menu.addSeparator()
        add_menu_action(file_menu, "Load New Database", self.onOpen)
        add_menu_action(file_menu, "Update Database", self.update_action_run)
        file_menu.addSeparator()

        settings_menu = menubar.addMenu("Reporting Setting Telegram/Discord")
        add_menu_action(settings_menu, "Telegram", self.open_telegram_settings)
        add_menu_action(settings_menu, "Discord", self.open_discord_settings)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        self.add_count_label = QLabel(self.count_addresses(), objectName="count_addlabel", alignment=Qt.AlignmentFlag.AlignLeft)

        power_label = QLabel("Amount Of Addresses Per Page to Show", self)
        power_label.setObjectName("powerLabel")

        self.format_combo_box_POWER = QComboBox(self)
        self.format_combo_box_POWER.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;"> Amount it Address to Check per scan. Ajust for best speed have to stop to change amount </span>')
        self.format_combo_box_POWER.addItems(
            ["1", "128", "256", "512", "1024", "2048", "4096", "8192", "16384"]
        )

        select_power_layout = QHBoxLayout()
        select_power_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        select_power_layout.addWidget(power_label)
        select_power_layout.addWidget(self.format_combo_box_POWER)

        start_button = QPushButton("Start", self)
        start_button.setObjectName("startButton")
        start_button.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;"> Start scanning (Make sure Range is set) </span>')
        start_button.clicked.connect(self.start)
        start_button.setFixedWidth(100)

        stop_button = QPushButton("Stop", self)
        stop_button.setObjectName("stopButton")
        stop_button.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;"> Stop scanning </span>')
        stop_button.clicked.connect(self.stop)
        stop_button.setFixedWidth(100)

        start_stop_layout = QHBoxLayout()
        start_stop_layout.addLayout(select_power_layout)
        start_stop_layout.addStretch(1)
        start_stop_layout.addWidget(start_button)
        start_stop_layout.addWidget(stop_button)
        start_stop_layout.addStretch(1)

        start_stop_layout.addWidget(self.add_count_label)

        # Create input fields and buttons for skip range
        self.add_range_button = QPushButton("➕ Skip Current Range in Scan", self)
        self.add_range_button.setObjectName("addRange")
        self.add_range_button.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;"> Here you can add ranges from the Key Space box to exclude from scanning </span>')
        self.add_range_button.clicked.connect(self.add_range_from_input)

        self.show_ranges_button = QPushButton("👀 Show Skipped Ranges", self)
        self.show_ranges_button.setObjectName("showRange")
        self.show_ranges_button.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;"> Show excluded ranges (Edit add and remove) </span>')
        self.show_ranges_button.clicked.connect(self.show_ranges)

        skip_range_layout = QHBoxLayout()
        skip_range_layout.addWidget(self.add_range_button)
        skip_range_layout.addWidget(self.show_ranges_button)

        options_layout2 = QHBoxLayout()

        self.keyspaceLabel = QLabel("Key Space:", self)
        options_layout2.addWidget(self.keyspaceLabel)

        self.start_edit = QLineEdit("20000000000000000")
        self.start_edit.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;"> Type in Starting HEX or Use Slider to update</span>')

        self.end_edit = QLineEdit("3ffffffffffffffff")
        self.end_edit.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;"> Type in Ending HEX or Use Slider to update</span>')

        self.keyspace_slider = QSlider(Qt.Orientation.Horizontal)
        self.keyspace_slider.setMinimum(1)
        self.keyspace_slider.setMaximum(256)
        self.keyspace_slider.setValue(66)
        self.keyspace_slider.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;"> Drag Left to Right to Adjust Range </span>')
        keyspacerange_layout = QVBoxLayout()
        keyspacerange_layout.addWidget(self.start_edit)
        keyspacerange_layout.addWidget(self.end_edit)
        keyspacerange_layout.addWidget(self.keyspace_slider)

        options_layout2.addLayout(keyspacerange_layout)


        self.keyspace_slider.valueChanged.connect(self.update_keyspace_range)
        self.bitsLabel = QLabel("Bits:", self)
        options_layout2.addWidget(self.bitsLabel)

        self.bitsLineEdit = QLineEdit(self)
        self.bitsLineEdit.setText("66")
        self.bitsLineEdit.textChanged.connect(self.updateSliderAndRanges)
        options_layout2.addWidget(self.bitsLineEdit)


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
        button_labels = ["Random", "Sequence", "Reverse"]
        button_objects = []

        for label in button_labels:
            button = QRadioButton(label)
            button.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;"> Pick Type of scan Random Sequence/Forward or Reverse/Backwards </span>')
            button_objects.append(button)

        button_objects[0].setChecked(True)
        self.random_button = button_objects[0]
        self.sequence_button = button_objects[1]
        self.reverse_button = button_objects[2]
        checkbox_labels = ["DEC", "HEX", "Compressed", "Uncompressed", "P2SH", "Bech32", "Stop if found"]
        checkbox_objects = []
        checkbox_width = 140
        for label in checkbox_labels:
            checkbox = QCheckBox(label)
            checkbox.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;"> Ticks can be removed to sreach for single type or mutiple types of Bitcoin Address. Removing some will increase speed. Address not selected we not be searched </span>')
            checkbox.setFixedWidth(checkbox_width)
            checkbox_objects.append(checkbox)
        self.dec_checkbox, self.hex_checkbox, self.compressed_checkbox, self.uncompressed_checkbox, self.p2sh_checkbox, self.bech32_checkbox, self.win_checkbox = checkbox_objects[0:]
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
            self.win_checkbox
        ]

        for widget in widgets:
            radio_and_checkbox_layout.addWidget(widget)

        # Set up the main layout
        layouts = [
            start_stop_layout, 
            radio_and_checkbox_layout, options_layout2, skip_range_layout, current_scan_layout
        ]

        for l in layouts:
            layout.addLayout(l)

        def create_line_edit(read_only=True, text="0"):
            line_edit = QLineEdit()
            line_edit.setReadOnly(read_only)
            line_edit.setText(text)
            return line_edit

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

        progress_layout_text = QHBoxLayout()
        progress_layout_text.setObjectName("progressbar")
        progress_label = QLabel("progress %")

        self.progress_bar = bar_gui.CustomProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)

        progress_layout_text.addWidget(progress_label)
        progress_layout_text.addWidget(self.progress_bar)

        layout.addLayout(progress_layout_text)

        self.address_layout_ = QGridLayout()
        self.priv_label = QLabel("DEC Keys: ")
        self.priv_text = QTextEdit(self)
        self.priv_text.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;"> Decimal Key Output</span>')
        self.HEX_label = QLabel("HEX Keys: ")
        self.HEX_text = QTextEdit(self)
        self.HEX_text.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;"> HEX Key Output</span>')
        self.comp_label = QLabel("Compressed Address: ")
        self.comp_text = QTextEdit(self)
        self.comp_text.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;"> Compressed Address Output</span>')
        self.uncomp_label = QLabel("Uncompressed Address: ")
        self.uncomp_text = QTextEdit(self)
        self.uncomp_text.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;"> Uncompressed Address Output</span>')
        self.p2sh_label = QLabel("p2sh Address: ")
        self.p2sh_text = QTextEdit(self)
        self.p2sh_text.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;"> P2SH 3 Address Output</span>')
        self.bech32_label = QLabel("bech32 Address: ")
        self.bech32_text = QTextEdit(self)
        self.bech32_text.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;"> bech32 BC1 Address Output</span>')
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

        # Create checkbox for custom Telegram credentials
        self.use_telegram_credentials_checkbox = QCheckBox("Use Custom Telegram Credentials (edit in settings menu)")
        self.use_telegram_credentials_checkbox.setChecked(False)
        self.use_discord_credentials_checkbox = QCheckBox("Use Custom Discord Credentials (edit in settings menu)")
        self.use_discord_credentials_checkbox.setChecked(False)

        custom_credentials_layout = QHBoxLayout()
        custom_credentials_layout.addWidget(self.use_telegram_credentials_checkbox)
        custom_credentials_layout.addWidget(self.use_discord_credentials_checkbox)
        layout.addLayout(custom_credentials_layout)
        self.counter = 0
        self.timer = time.time()

        self.start_edit.setText('20000000000000000')
        self.end_edit.setText('3ffffffffffffffff')

    def onOpen(self):
        global addfind, BTC_BF_FILE
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "BF Files (*.bf);;Text Files (*.txt)"
        )

        if not filePath:
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

        success_message = f"File loaded: {filePath}"
        QMessageBox.information(self, "File Loaded", success_message)

        self.add_count_label.setText(self.count_addresses(BTC_BF_FILE))

    def exit_app(self):
        QApplication.quit()

    def open_telegram_settings(self):
        settings_dialog = telegram_gui.Settings_telegram_Dialog(self)
        settings_dialog.exec()
    
    def open_discord_settings(self):
        settings_dialog = discord_gui.Settings_discord_Dialog(self)
        settings_dialog.exec()

    def update_action_run(self):
        update_dialog = up_bloom_gui.UpdateBloomFilterDialog(self)
        update_dialog.exec()

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

    def add_range_from_input(self):
        start_str = self.start_edit.text()
        end_str = self.end_edit.text()

        if start_str and end_str:
            start = "0x" + start_str if not start_str.startswith("0x") else start_str
            end = "0x" + end_str if not end_str.startswith("0x") else end_str

            if (start, end) in self.skip_ranges:
                QMessageBox.information(
                    self, "Duplicate Range", "Range is already added."
                )
                return
            self.skip_ranges.append((start, end))
            with open(SKIPPED_FILE, "a") as f:
                f.write(f"{start}:{end}\n")
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
            bits = max(0, min(bits, 256))
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
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            error_message = f"HTTP Error: {errh}"
            QMessageBox.critical(self, "Error", error_message)
        except Exception as e:
            error_message = f"Telegram error: {str(e)}"
            QMessageBox.critical(self, "Error", error_message)

    def update_skipped_file(self):
        with open(SKIPPED_FILE, "w") as f:
            for start, end in self.skip_ranges:
                f.write(f"{start:016x}:{end:016x}\n")

    def show_ranges(self):
        try:
            ranges_dialog = show_ranges_gui.ShowRangesDialog(self.skip_ranges)
            result = ranges_dialog.exec()

            if result == QDialog.DialogCode.Accepted:
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
        except Exception as e:
            error_message = f"Ranges empty please Type a Start and Stop: {str(e)}"
            QMessageBox.critical(self, "Error", error_message)

    def stop(self):
        if isinstance(self.timer, QTimer):
            self.timer.stop()
            self.worker_finished("Recovery Finished")

    def worker_finished(self, result):
        if self.scanning:
            QMessageBox.information(self, "Recovery Finished", "Done")
        self.scanning = False

    def generate_crypto(self):
        dec_keys, HEX_keys, uncomp_keys, comp_keys, p2sh_keys, bech32_keys = [], [], [], [], [], []
        found = int(self.found_keys_scanned_edit.text())
        startPrivKey = self.num

        for i in range(0, self.power_format):
            dec = int(startPrivKey)
            HEX = f"{dec:016x}"
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
        update_interval = 1

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

            self.num += self.power_format

            if self.num % update_interval == 0:
                QApplication.processEvents()

        self.num = end
        self.scanning = False

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
        update_interval = 1
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

            self.num -= self.power_format
            processed_count += 1
            if not self.scanning:
                break
            if processed_count >= update_interval:
                processed_count = 0
                QApplication.processEvents()
        self.num = start
        self.scanning = False

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