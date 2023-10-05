import sys
import random
import platform
import subprocess
try:
    from PyQt6.QtCore import *
    from PyQt6.QtWidgets import *
    from PyQt6.QtGui import *
    from bloomfilter import BloomFilter, ScalableBloomFilter, SizeGrowthRate
    import secp256k1 as ice
    import miz_widget as miz
    import time
    import locale
    import qdarktheme
    import requests
    import os
    import webbrowser

except ImportError:
    import subprocess
    subprocess.check_call(["python", '-m', 'pip', 'install', 'PyQt6', 'simplebloomfilter', 'bitarray==1.9.2', 'pyqtdarktheme', 'requests'])

version = '0.2'

qss = """ 
    QCheckBox::hover {
    border-width: 0px;    
}

QRadioButton {
    max-width: 100px;
}

QRadioButton::hover {
    border-width: 0px;
}

QLabel#powerLabel {
    font-size: 14px;
    padding: 0px 0px 0px 10px;
}

QComboBox {
    border: 0px;
    max-width: 100px;
    font-weight: bold;
    margin: 0px;
}

QComboBox::down-arrow {
    width: 0;
}
    """

# Global CSS styles for light mode
light_mode_stylesheet = """
GUIInstance {
    background-color: #DBDBDB;
}

QComboBox {
    background-color: #DBDBDB;
    color: #000000;    
}

QPushButton#startButton, 
QPushButton#stopButton, 
QPushButton#addRange, 
QPushButton#showRange {
    color: #FFFFFF;
    font-weight: bold;
    padding: 10px 20px;
}

QPushButton#startButton {
    background-color: #4CAF50;
    border: none;
}

QPushButton#startButton:hover {
    background-color: #3A863D;
}

QPushButton#stopButton {
    background-color: #FF5722;
    border: none;
}

QPushButton#stopButton:hover {
    background-color: #993414;
}

QPushButton#addRange,
QPushButton#showRange {
    background-color: #1A73E8;
}

QPushButton#addRange:hover,
QPushButton#showRange:hover {
    background-color: #1662C6;
}

QRadioButton,
QCheckBox {
    color: #000000;
    font-size: 16px;
    padding: 8px;
    margin: 4px;
}

QRadioButton::checked,
QCheckBox::checked {
    color: #000000;
    background-color: #C6C6C6;
    border-radius: 20px;
    font-size: 16px;
    padding: 8px;
    margin: 4px;
}

QRadioButton::indicator,
QCheckBox::indicator {
    width: 16px;
    height: 16px;
}

QRadioButton::indicator:checked,
QCheckBox::indicator:checked {
    background-color: #C6C6C6;
    border-radius: 8px;
}

QRadioButton::indicator:unchecked,
QCheckBox::indicator:unchecked {
    background-color: #DBDBDB;
    border-radius: 8px;
}

QProgressBar {
    color: #000000;
    background: #DBDBDB;
    border: 1px solid #7D7D7D;
}

QProgressBar::chunk {
    color: #000000;
    background-color: #1A73E8;
}

QLabel#madeby,
QLabel#version,
QLabel#copyright,
QLabel#versionpy,
QLabel#dot1,
QLabel#dot2,
QLabel#dot3,
QLabel#count_addlabel,
QLabel#titlelabel,
QLabel#titlelabel1 {
    font-weight: bold;
    font-size: 16px;
}

QLabel#dot1,
QLabel#dot2,
QLabel#dot3 {
    color: #1A73E8;
}

QLabel#count_addlabel {
    color: #333333;
    font-size: 20px;
}

QLabel#titlelabel {
    color: #333333;
    font-size: 22px;
}

QLabel#titlelabel1 {
    color: #555555;
    font-size: 18px;
}

QGroupBox#knightrider {
    border: 2px solid #FF0000;
    background-color: #DBDBDB;
    border-radius: 5px;
}

"""

# Global CSS styles for dark mode
dark_mode_stylesheet = """

QComboBox {
    background-color: #202124;
    color: #FFFFFF;
}

QPushButton#startButton,
QPushButton#stopButton,
QPushButton#addRange,
QPushButton#showRange {
    color: white;
    font-weight: bold;
    padding: 10px 20px;
    border: none;
}

QPushButton#startButton {
    background-color: #4CAF50;
}

QPushButton#startButton:hover {
    background-color: #3A863D;
}

QPushButton#stopButton {
    background-color: #FF5722;
}

QPushButton#stopButton:hover {
    background-color: #993414;
}

QPushButton#addRange,
QPushButton#showRange {
    background-color: #8AB4F7;
    color: #000000;
}

QPushButton#addRange:hover,
QPushButton#showRange:hover {
    background-color: #769AD3;
}

QRadioButton,
QCheckBox {
    color: #FFFFFF;
    font-size: 16px;
    padding: 8px;
    margin: 4px;
}

QRadioButton::checked,
QCheckBox::checked {
    color: #FFFFFF;
    background-color: #1B1C1E;
    border-radius: 20px;
    font-size: 16px;
    padding: 8px;
    margin: 4px;
}

QRadioButton::indicator,
QCheckBox::indicator {
    width: 16px;
    height: 16px;
}

QRadioButton::indicator:checked,
QCheckBox::indicator:checked {
    background-color: #000000;
    border-radius: 8px;
}

QRadioButton::indicator:unchecked,
QCheckBox::indicator:unchecked {
    background-color: #202124;
    border-radius: 8px;
}

QProgressBar {
    color: #FFFFFF;
    background: #202124;
    border: 1px solid #323338;
}

QProgressBar::chunk {
    color: #000000;
    background-color: #8AB4F7;
}

QLabel#madeby,
QLabel#version,
QLabel#copyright,
QLabel#versionpy {
    font-weight: bold;
    font-size: 16px;
}

QLabel#dot1,
QLabel#dot2,
QLabel#dot3 {
    color: #8AB4F7;
}

QLabel#count_addlabel {
    color: #8AB4F7;
    font-size: 20px;
}

QLabel#titlelabel {
    color: #777777;
    font-size: 22px;
}

QLabel#titlelabel1 {
    color: #888888;
    font-size: 18px;
}

QGroupBox#knightrider {
    border: 2px solid #FF0000;
    background-color: #202124;
    border-radius: 5px;
}

"""

def create_settings_file_if_not_exists():
    if not os.path.exists('settings.txt'):
        with open('settings.txt', 'w') as file:
            file.write(
'''// Choose default theme [light] / [dark]
theme=dark

// Telegram Settings
token=
chatid='''
            )

# Set system locale
locale.setlocale(locale.LC_ALL, '')

# Load Bitcoin Bloom filter
try:
    with open('btc.bf', "rb") as fp:
        addfind = BloomFilter.load(fp)
except FileNotFoundError:
    filename = 'btc.txt'
    with open(filename) as file:
        addfind = file.read().split()
    
# Initialize QApplication
app = QApplication(sys.argv)

def get_settings():
    settings_dict = {}
    
    try:
        with open('settings.txt', 'r') as settings_file:
            for line in settings_file:
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)  # Use split with maxsplit=1 to handle lines with multiple '=' signs
                    settings_dict[key] = value
                
    except FileNotFoundError:
        setting_message = "Settings file not found."
        QMessageBox.information(self, "File not found", setting_message)
    except Exception as e:
        error_message = f"An error occurred while reading settings: {e}"
        QMessageBox.critical(self, "Error", error_message)
    
    return settings_dict

# Define the function to get the balance of an address
def get_balance(addr):
    try:
        response = requests.get(f'https://api.haskoin.com/btc/address/{addr}/balance')
        if response.status_code == 200:
            return response.json()
        else:
            print(f'Error getting balance for address {addr}: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'Error sending request for address {addr}: {str(e)}')
        
# GUIInstance: QWidget class for the main GUI interface.
class GUIInstance(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(80, 80, 1400, 560)
        create_settings_file_if_not_exists()
        
        # Initialize skip_ranges as an empty list and create an instance of ShowRangesDialog.
        self.skip_ranges = []
        self.ranges_dialog = miz.ShowRangesDialog(self.skip_ranges)
        
        # Load skip ranges when the GUI starts.
        self.load_skip_ranges()

        self.initUI()
        
    # Load theme preference from settings.txt
        self.theme_preference = self.get_theme_preference()
        if self.theme_preference == 'dark':
            self.dark_mode_button.setText("🌞")
            self.load_dark_mode()
            self.dark_mode = True
        elif self.theme_preference == 'light':
            self.dark_mode_button.setText("🌙")
            self.load_light_mode()
            self.dark_mode = False
                        
    def load_dark_mode(self):
        # Set dark mode stylesheet
        self.setStyleSheet(dark_mode_stylesheet)

        # Load qdarktheme in dark mode
        qdarktheme.setup_theme("dark", additional_qss=qss)

    def load_light_mode(self):
        # Set light mode stylesheet
        self.setStyleSheet(light_mode_stylesheet)

        # Load qdarktheme in light mode
        qdarktheme.setup_theme("light", additional_qss=qss)
    
    def in_skip_range(self, position):
        def check_hex_format(value):
            if isinstance(value, str):
                try:
                    int(value, 16)
                    return True
                except ValueError:
                    pass
            return False

        position = str(position)

        for start, end in self.skip_ranges:
            if check_hex_format(start) and check_hex_format(end):
                if str(start) <= str(position) <= str(end):
                    return True
        return False

    # Function to display skip ranges dialog.
    def show_ranges(self):
        # Read skip ranges from 'skipped.txt'.
        with open('skipped.txt', 'r') as f:
            ranges = f.readlines()

        ranges_text = ''.join(ranges)
        
        # Create a dialog for showing the ranges.
        ranges_dialog = miz.ShowRangesDialog(self)
        ranges_dialog.setWindowTitle("Show Ranges")
        layout = QVBoxLayout(ranges_dialog)

        ranges_textedit = QPlainTextEdit(ranges_text)
        layout.addWidget(ranges_textedit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        
        # Connect accept and reject actions for the dialog buttons.
        buttons.accepted.connect(ranges_dialog.accept)
        buttons.rejected.connect(ranges_dialog.reject)
        
        layout.addWidget(buttons)

        result = ranges_dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            # If user clicks 'OK', update the skip ranges.
            new_ranges_text = ranges_textedit.toPlainText()
            with open('skipped.txt', 'a') as f:
                f.write(new_ranges_text)

            self.load_skip_ranges()

    # Function to load skip ranges from 'skipped.txt' file.
    def load_skip_ranges(self):
        try:
            with open('skipped.txt', 'r') as f:
                ranges = f.readlines()

            self.skip_ranges.clear()

            for range_str in ranges:
                parts = range_str.strip().split(':')
                if len(parts) == 2:
                    start_str, end_str = parts
                    self.skip_ranges.append((start_str, end_str))
        except FileNotFoundError:
            # Handle the case when the skipped.txt file doesn't exist
            pass

    def initUI(self):
        self.setWindowIcon(QIcon('images/miz.ico'))
        # Create the menu bar
        menubar = self.menuBar()

        # Create File menu
        fileMenu = menubar.addMenu('File')

        # Create New action
        newAction = QAction('New Window QT', self)
        newAction.triggered.connect(self.onNew)
        fileMenu.addAction(newAction)

        # Create Open action
        openAction = QAction('Load New Database', self)
        openAction.triggered.connect(self.onOpen)
        fileMenu.addAction(openAction)
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_app)
        fileMenu.addAction(exit_action)

        # Create Settings menu
        settings_menu = menubar.addMenu("Settings")

        open_settings_action = QAction("Telegram Settings", self)
        open_settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(open_settings_action)
        
        update_action = QAction("Update BTC Database", self)
        update_action.triggered.connect(self.update_action_run)
        settings_menu.addAction(update_action)
        
        # Create Help menu
        helpMenu = menubar.addMenu('Help')
        
        MizoggAction = QAction('Mizogg Website', self)
        MizoggAction.triggered.connect(self.open_web)
        helpMenu.addAction(MizoggAction)
        
        HelpAction = QAction('Help Telegram Group', self)
        HelpAction.triggered.connect(self.open_telegram)
        helpMenu.addAction(HelpAction)
        aboutAction = QAction('About', self)
        aboutAction.triggered.connect(self.onAbout)
        helpMenu.addAction(aboutAction)

        # Set up the main content area
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)
        self.setWindowTitle('Hunter QT')
        madeby_label = QLabel(f'Made by Mizogg & Firehawk52')
        madeby_label.setObjectName('madeby')
        version_label = QLabel(f'Version {version}')
        version_label.setObjectName('version')
        copyright_label = QLabel('© mizogg.co.uk 2018 - 2023')
        copyright_label.setObjectName('copyright')
        versionpy_label = QLabel(f'Running Python {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}')
        versionpy_label.setObjectName('versionpy')
        dot1_label = QLabel('●')
        dot1_label.setObjectName('dot1')
        dot2_label = QLabel('●')
        dot2_label.setObjectName('dot2')
        dot3_label = QLabel('●')
        dot3_label.setObjectName('dot3')

        credit_label = QHBoxLayout()
        credit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credit_label.addWidget(madeby_label)
        credit_label.addWidget(dot1_label)
        credit_label.addWidget(version_label)
        credit_label.addWidget(dot2_label)
        credit_label.addWidget(copyright_label)
        credit_label.addWidget(dot3_label)
        credit_label.addWidget(versionpy_label)
        
        labels_layout = QHBoxLayout()

        # Create the self.add_count_label
        self.add_count_label = QLabel(self.count_add())
        self.add_count_label.setObjectName('count_addlabel')
        self.add_count_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Create title_label
        title_label = QLabel('🌟 Hunter QT 🌟')
        title_label.setObjectName('titlelabel')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create title_label1
        title_label1 = QLabel('Good Luck and Happy Hunting')
        title_label1.setObjectName('titlelabel1')
        title_label1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add labels to the labels_layout
        labels_layout.addWidget(self.add_count_label)
        labels_layout.addWidget(title_label)
        labels_layout.addWidget(title_label1)
       
        # Create a QPushButton for dark mode toggle
        self.dark_mode_button = QPushButton()
        self.dark_mode_button.setFixedSize(30, 30)
        self.dark_mode_button.clicked.connect(self.toggle_theme)

        if self.get_theme_preference == 'dark':            
            self.load_dark_mode()
            self.dark_mode = True
        else:
            self.load_light_mode()
            self.dark_mode = False
            
        self.toggle_theme()
        self.dark_mode_button.setChecked(True)
            
        dark_mode_layout = QHBoxLayout()
        dark_mode_layout.addStretch()
        dark_mode_layout.addWidget(self.dark_mode_button)
        
        # Create start and stop buttons
        start_stop_layout = QHBoxLayout()
        start_stop_layout.addStretch()

        start_button = QPushButton('Start')
        start_button.setObjectName('startButton')
        start_button.clicked.connect(self.start)
        start_button.setFixedWidth(100)

        stop_button = QPushButton('Stop')
        stop_button.setObjectName('stopButton')
        stop_button.clicked.connect(self.stop)
        stop_button.setFixedWidth(100)

        # Add buttons to the layout
        start_stop_layout.addWidget(start_button)
        start_stop_layout.addWidget(stop_button)

        # Add a stretchable space to the right
        start_stop_layout.addStretch()

        power_label = QLabel('Show')
        power_label.setObjectName('powerLabel')
        self.format_combo_box_POWER = QComboBox()
        self.format_combo_box_POWER.addItems(["1", "128", "256", "512", "1024", "2048", "4096", "8192", "16384"])

        select_power_layout = QHBoxLayout()
        select_power_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        select_power_layout.addWidget(power_label)
        select_power_layout.addWidget(self.format_combo_box_POWER)

        # Create input fields and buttons for skip range
        self.add_range_button = QPushButton('➕ Skip Current Range in Scan')
        self.add_range_button.setObjectName('addRange')
        self.add_range_button.clicked.connect(self.add_range_from_input)

        self.show_ranges_button = QPushButton('👀 Show Skipped Ranges')
        self.show_ranges_button.setObjectName('showRange')
        self.show_ranges_button.clicked.connect(self.show_ranges)

        skip_range_layout = QHBoxLayout()
        skip_range_layout.addWidget(self.add_range_button)
        skip_range_layout.addWidget(self.show_ranges_button)

        options_layout2 = QHBoxLayout()
        self.keyspaceLabel = QLabel("Key Space:", self)
        options_layout2.addWidget(self.keyspaceLabel)
        self.start_edit = QLineEdit("20000000000000000")
        self.end_edit = QLineEdit("3ffffffffffffffff")        
        keyspacerange_layout = QVBoxLayout()
        self.keyspace_slider = QSlider(Qt.Orientation.Horizontal)
        self.keyspace_slider.setMinimum(1)
        self.keyspace_slider.setMaximum(256)
        self.keyspace_slider.setValue(66)
        keyspacerange_layout.addWidget(self.start_edit)
        keyspacerange_layout.addWidget(self.end_edit)
        keyspacerange_layout.addWidget(self.keyspace_slider)
        options_layout2.addLayout(keyspacerange_layout)
        options_layout2.setStretchFactor(keyspacerange_layout, 5)
        self.keyspace_slider.valueChanged.connect(self.update_keyspace_range)
        
        self.bitsLabel = QLabel("Bits:", self)
        options_layout2.addWidget(self.bitsLabel)
        self.bitsLineEdit = QLineEdit(self)
        self.bitsLineEdit.setText("66")
        self.bitsLineEdit.textChanged.connect(self.updateSliderAndRanges)
        options_layout2.addWidget(self.bitsLineEdit)
        options_layout2.setStretchFactor(self.bitsLineEdit, 1)
        dec_label = QLabel(' Dec value :')
        self.value_edit_dec = QLineEdit()
        self.value_edit_dec.setReadOnly(True)

        hex_label = QLabel(' HEX value :')
        self.value_edit_hex = QLineEdit()
        self.value_edit_hex.setReadOnly(True)
        
        current_scan_layout = QHBoxLayout()
        current_scan_layout.addWidget(dec_label)
        current_scan_layout.addWidget(self.value_edit_dec)
        current_scan_layout.addWidget(hex_label)
        current_scan_layout.addWidget(self.value_edit_hex)

        # Create radio buttons for selection
        self.random_button = QRadioButton('Random')
        self.sequence_button = QRadioButton('Sequence')
        self.reverse_button = QRadioButton('Reverse')
        self.random_button.setChecked(True)

        # Create checkboxes for each address format
        checkbox_width = 200
        self.dec_checkbox = QCheckBox("DEC")
        self.hex_checkbox = QCheckBox("HEX")
        self.compressed_checkbox = QCheckBox("Compressed")
        self.uncompressed_checkbox = QCheckBox("Uncompressed")
        self.p2sh_checkbox = QCheckBox("P2SH")
        self.bech32_checkbox = QCheckBox("Bech32")
        self.win_checkbox = QCheckBox("Stop if winner found")
        self.compressed_checkbox.setFixedWidth(checkbox_width)
        self.uncompressed_checkbox.setFixedWidth(checkbox_width)
        self.p2sh_checkbox.setFixedWidth(checkbox_width)
        self.bech32_checkbox.setFixedWidth(checkbox_width)
        self.win_checkbox.setFixedWidth(checkbox_width)
        
        self.balance_check_checkbox = QCheckBox("Balance Check (Compressed Only)")
        self.balance_check_checkbox.setChecked(False)  # Set the initial state
        self.balance_check_checkbox.setFixedWidth(checkbox_width)
        self.balance_check_checkbox.stateChanged.connect(self.handle_balance_check_toggle)
        

        # Set checkboxes to be checked by default
        self.dec_checkbox.setChecked(True)
        self.hex_checkbox.setChecked(True)
        self.compressed_checkbox.setChecked(True)
        self.uncompressed_checkbox.setChecked(True)
        self.p2sh_checkbox.setChecked(True)
        self.bech32_checkbox.setChecked(True)
        self.win_checkbox.setChecked(False)
        
        # Create a vertical line as a divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        
        # Create a layout for the radio buttons and checkboxes on the same line
        radio_and_checkbox_layout = QHBoxLayout()
        radio_and_checkbox_layout.addWidget(self.random_button)
        radio_and_checkbox_layout.addWidget(self.sequence_button)
        radio_and_checkbox_layout.addWidget(self.reverse_button)
        radio_and_checkbox_layout.addWidget(divider)
        radio_and_checkbox_layout.addWidget(self.dec_checkbox)
        radio_and_checkbox_layout.addWidget(self.hex_checkbox)
        radio_and_checkbox_layout.addWidget(self.compressed_checkbox)
        radio_and_checkbox_layout.addWidget(self.uncompressed_checkbox)
        radio_and_checkbox_layout.addWidget(self.p2sh_checkbox)
        radio_and_checkbox_layout.addWidget(self.bech32_checkbox)
        radio_and_checkbox_layout.addWidget(self.win_checkbox)
        radio_and_checkbox_layout.addWidget(self.balance_check_checkbox)
                
        # Set up the main layout
        layout.addLayout(dark_mode_layout)
        layout.addLayout(labels_layout) 
        layout.addLayout(start_stop_layout)
        layout.addLayout(select_power_layout)
        layout.addLayout(radio_and_checkbox_layout)
        layout.addLayout(options_layout2)
        layout.addLayout(skip_range_layout)
        layout.addLayout(current_scan_layout)

        # Create layout for displaying key statistics
        keys_layout = QHBoxLayout()
        found_keys_scanned_label = QLabel('Found')
        self.found_keys_scanned_edit = QLineEdit()
        self.found_keys_scanned_edit.setReadOnly(True)
        self.found_keys_scanned_edit.setText('0')
        keys_layout.addWidget(found_keys_scanned_label)
        keys_layout.addWidget(self.found_keys_scanned_edit)

        total_keys_scanned_label = QLabel('Total keys scanned:')
        self.total_keys_scanned_edit = QLineEdit()
        self.total_keys_scanned_edit.setReadOnly(True)
        self.total_keys_scanned_edit.setText('0')
        keys_layout.addWidget(total_keys_scanned_label)
        keys_layout.addWidget(self.total_keys_scanned_edit)
        
        keys_per_sec_label = QLabel('Keys per second:')
        self.keys_per_sec_edit = QLineEdit()
        self.keys_per_sec_edit.setReadOnly(True)
        keys_layout.addWidget(keys_per_sec_label)
        keys_layout.addWidget(self.keys_per_sec_edit)

        layout.addLayout(keys_layout)

        # Create progress bar
        progress_layout_text = QHBoxLayout()
        progress_layout_text.setObjectName('progressbar')
        progress_label = QLabel('progress %')
        self.progress_bar = miz.CustomProgressBar()
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
        self.dec_checkbox.stateChanged.connect(lambda: self.toggle_visibility(self.dec_checkbox, self.priv_label, self.priv_text))
        self.hex_checkbox.stateChanged.connect(lambda: self.toggle_visibility(self.hex_checkbox, self.HEX_label, self.HEX_text))
        self.compressed_checkbox.stateChanged.connect(lambda: self.toggle_visibility(self.compressed_checkbox, self.comp_label, self.comp_text))
        self.uncompressed_checkbox.stateChanged.connect(lambda: self.toggle_visibility(self.uncompressed_checkbox, self.uncomp_label, self.uncomp_text))
        self.p2sh_checkbox.stateChanged.connect(lambda: self.toggle_visibility(self.p2sh_checkbox, self.p2sh_label, self.p2sh_text))
        self.bech32_checkbox.stateChanged.connect(lambda: self.toggle_visibility(self.bech32_checkbox, self.bech32_label, self.bech32_text))

        # Initially, set the visibility based on the checkbox's initial state
        self.toggle_visibility(self.dec_checkbox, self.priv_label, self.priv_text)
        self.toggle_visibility(self.hex_checkbox, self.HEX_label, self.HEX_text)
        self.toggle_visibility(self.compressed_checkbox, self.comp_label, self.comp_text)
        self.toggle_visibility(self.uncompressed_checkbox, self.uncomp_label, self.uncomp_text)
        self.toggle_visibility(self.p2sh_checkbox, self.p2sh_label, self.p2sh_text)
        self.toggle_visibility(self.bech32_checkbox, self.bech32_label, self.bech32_text)

        # Create KnightRiderWidget for visual feedback
        self.knightRiderWidget = miz.KnightRiderWidget(self)
        self.knightRiderWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.knightRiderWidget.setMinimumHeight(20)
        
        self.knightRiderLayout = QHBoxLayout()
        self.knightRiderLayout.setContentsMargins(10, 15, 10, 10)
        self.knightRiderLayout.addWidget(self.knightRiderWidget)

        self.knightRiderGroupBox = QGroupBox(self)
        self.knightRiderGroupBox.setObjectName('knightrider')
        self.knightRiderGroupBox.setLayout(self.knightRiderLayout)
        
        layout.addWidget(self.knightRiderGroupBox)

        self.use_custom_credentials_checkbox = QCheckBox("Use Custom Telegram Credentials (edit in settings menu)")
        self.use_custom_credentials_checkbox.setChecked(False)
        
        custom_credentials_layout = QHBoxLayout()
        custom_credentials_layout.addWidget(self.use_custom_credentials_checkbox)
        layout.addLayout(custom_credentials_layout)
        layout.addLayout(credit_label)
        
        # Create a QHBoxLayout for the address input and check button
        address_input_layout = QHBoxLayout()

        # Add a QLineEdit widget for address input
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Enter Bitcoin Address")
        address_input_layout.addWidget(self.address_input)

        # Add a QPushButton widget for the check button
        self.check_button = QPushButton("Check Balance (1,3,bc1)")
        self.check_button.clicked.connect(self.check_balance)
        address_input_layout.addWidget(self.check_button)

        # Add the address_input_layout (QHBoxLayout) to the main layout (QVBoxLayout)
        layout.addLayout(address_input_layout)
        # Create a QLabel for displaying balance information
        self.balance_label = QLabel()
        layout.addWidget(self.balance_label)
        
        self.counter = 0
        self.timer = time.time()
        
        # Load saved start and end keys if available
        try:
            with open('start_scanned_key.txt', 'r') as f:
                saved_key_start = f.read()
            self.start_edit.setText(saved_key_start)
        except FileNotFoundError:
            pass
        
        try:
            with open('end_scanned_key.txt', 'r') as f:
                saved_key_end = f.read()
            self.end_edit.setText(saved_key_end)
        except FileNotFoundError:
            pass
    
    def check_balance(self):
        # Get the Bitcoin address from the input field
        address = self.address_input.text()

        # Check the balance for the entered address
        response_data = get_balance(address)
        
        if response_data:
            confirmed_balance = response_data.get("confirmed", 0)
            unconfirmed_balance = response_data.get("unconfirmed", 0)
            tx_count = response_data.get("txs", 0)
            received = response_data.get("received", 0)

            # Convert satoshis to BTC
            confirmed_balance_btc = confirmed_balance / 10**8
            unconfirmed_balance_btc = unconfirmed_balance / 10**8
            received_btc = received / 10**8

            # Create a formatted string with balance information
            BTCOUT = f'''               BTC Address: {address}
                >> Confirmed Balance: {confirmed_balance_btc:.8f} BTC     >> Unconfirmed Balance: {unconfirmed_balance_btc:.8f} BTC
                >> Total Received: {received_btc:.8f} BTC                 >> Transaction Count: {tx_count}'''

            # Display the balance information (you can show it in a label or text widget)
            self.balance_label.setText(BTCOUT)  # Assuming you have a label for displaying balance
        
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
        if platform.system() == 'Windows':
            creation_flags = subprocess.CREATE_NO_WINDOW
        else:
            creation_flags = 0

        python_cmd = f'"{sys.executable}" QT_main_ICE_Display.py'
        subprocess.Popen(python_cmd, creationflags=creation_flags, shell=True)

    def onOpen(self):
        global addfind
        filePath, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;BF Files (*.bf);;Text Files (*.txt)")
        
        if not filePath:  # If no file is selected, just return
            return

        if filePath.endswith('.bf'):
            try:
                with open(filePath, "rb") as fp:
                    addfind = BloomFilter.load(fp)
            except Exception as e:
                # Handle the exception (e.g., show an error message)
                error_message = f"Error loading file: {str(e)}"
                QMessageBox.critical(self, "Error", error_message)
        if filePath.endswith('.txt'):
            try:
                with open(filePath, "r") as file:
                    addfind = file.read().split()
            except Exception as e:
                error_message = f"Error loading file: {str(e)}"
                QMessageBox.critical(self, "Error", error_message)

        # Show a popup message to indicate that the file has been loaded
        success_message = f"File loaded: {filePath}"
        QMessageBox.information(self, "File Loaded", success_message)

        # Update the label with the total BTC addresses loaded
        self.add_count_label.setText(self.count_add())
        
    def exit_app(self):
        QApplication.quit()

    def open_settings(self):
        settings_dialog = miz.SettingsDialog(self)
        settings_dialog.exec()
       
    def update_action_run(self):
        update_dialog = miz.UpdateBloomFilterDialog(self)
        update_dialog.exec()
        
    def onAbout(self):
        about_dialog = miz.AboutDialog(self)
        about_dialog.exec()
    
    def open_web(self):
        webbrowser.open("https://mizogg.co.uk")

    def open_telegram(self):
        webbrowser.open("https://t.me/CryptoCrackersUK")
    
    def count_add(self):
        addr_data = len(addfind)
        addr_count_print = f'Total BTC Addresses Loaded and Checking : {addr_data}'
        return addr_count_print   
        
    def toggle_visibility(self, checkbox, label_widget, text_widget):
        state = checkbox.isChecked()
        label_widget.setVisible(state)
        text_widget.setVisible(state)
    
    def get_theme_preference(self):
        settings = get_settings()
        return settings.get('theme', 'dark')  # Default to 'dark' if not set in settings.txt
                
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode

        if self.dark_mode:
            self.load_dark_mode()
            self.dark_mode_button.setText("🌞")
        else:
            self.load_light_mode()
            self.dark_mode_button.setText("🌙")
    
    def add_range_from_input(self):
        start_str = self.start_edit.text()
        end_str = self.end_edit.text()

        if start_str and end_str:
            # Ensure the input values have the "0x" prefix
            if not start_str.startswith("0x"):
                start_str = "0x" + start_str
            if not end_str.startswith("0x"):
                end_str = "0x" + end_str

            start = str(start_str)
            end = str(end_str)

            # Check for duplicates
            if (start, end) in self.skip_ranges:
                QMessageBox.information(self, 'Duplicate Range', 'Range is already added.')
                return

            # Add the range to the skip_ranges list
            self.skip_ranges.append((start, end))

            # Update the skipped.txt file
            with open('skipped.txt', 'a') as f:
                f.write(f"{start}:{end}\n")

            # Clear the input fields
            self.start_edit.clear()
            self.end_edit.clear()
            self.add_range_button.setText(f'Range Added: {start} - {end}')
            QTimer.singleShot(5000, lambda: self.add_range_button.setText("➕ Skip Current Range in Scan"))
                
    def update_keyspace_range(self, value):
        start_range = hex(2**(value - 1))[2:]
        end_range = hex(2**value - 1)[2:]
        self.start_edit.setText(f"{start_range}")
        self.end_edit.setText(f"{end_range}")
        self.bitsLineEdit.setText(str(value))
    
    def updateSliderAndRanges(self, text):
        try:
            bits = int(text)
            # Ensure bits is within the valid range
            bits = max(0, min(bits, 256))  # Adjust the range as needed
            self.keyspace_slider.setValue(bits)
            self.start_edit.setText(hex(2 ** bits))
            self.end_edit.setText(hex(2 ** (bits + 1) - 1))
        except ValueError:
            range_message = "Range in Bit 1-256 "
            QMessageBox.information(self, "Range Error", range_message)
            pass
    
    def send_to_telegram(self, text):
        settings = get_settings()
        apiToken = settings.get('token', '').strip()
        chatID = settings.get('chatid', '').strip()

        if not apiToken or not chatID:
            token_message = "No token or ChatID found in settings.txt"
            QMessageBox.information(self, "No token or ChatID", token_message)
            return

        apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'
        try:
            response = requests.post(apiURL, json={'chat_id': chatID, 'text': text})
        except Exception as e:
            error_message = f"Telegram error: {str(e)}"
            QMessageBox.critical(self, "Error", error_message)

    # Helper function to update the skipped ranges file
    def update_skipped_file(self):
        with open('skipped.txt', 'w') as f:
            for start, end in self.skip_ranges:
                f.write(f"{start:016x}:{end:016x}\n")

    def show_ranges(self):
        # Open a dialog to show the list of skipped ranges
        ranges_dialog = miz.ShowRangesDialog(self.skip_ranges)
        result = ranges_dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            # Update the skipped ranges list with any changes made in the dialog
            self.skip_ranges = ranges_dialog.get_ranges()
            self.update_skipped_file()

    def start(self):
        # Get power format from combo box
        power_format = self.format_combo_box_POWER.currentText()
        self.power_format = int(power_format)

        # Get key format, start value, and end value
        start_value = self.start_edit.text()
        end_value = self.end_edit.text()
        start = int(start_value, 16)
        end = int(end_value, 16)

        self.total_steps = end - start
        self.scanning = True

        # Determine scanning mode (Random, Sequence, or Reverse)
        if self.random_button.isChecked():
            self.timer = QTimer(self)
            self.timer.timeout.connect(lambda: self.update_display(start, end))
        elif self.sequence_button.isChecked():
            self.current = start
            self.timer = QTimer(self)
            self.timer.timeout.connect(lambda: self.update_display_sequence(start, end))
        elif self.reverse_button.isChecked():
            self.current = end
            self.timer = QTimer(self)
            self.timer.timeout.connect(lambda: self.update_display_reverse(start, end))

        self.timer.start()
        self.start_time = time.time()
        self.timer.timeout.connect(self.update_keys_per_sec)
        self.knightRiderWidget.startAnimation()

    def stop(self):
        if isinstance(self.timer, QTimer):
            self.timer.stop()
            self.worker_finished('Recovery Finished')
    
    # This function handles the completion of the recovery process
    def worker_finished(self, result):
        # Check if scanning is still in progress
        if self.scanning:
            QMessageBox.information(self, 'Recovery Finished', 'Done')
        self.scanning = False
        # Stop the animation of the "knightRiderWidget"
        self.knightRiderWidget.stopAnimation()

    # This function generates cryptographic keys and addresses
    def generate_crypto(self):
        # Initialize lists to store different types of keys and addresses
        dec_keys = []
        HEX_keys = []
        uncomp_keys = []
        comp_keys = []
        p2sh_keys = []
        bech32_keys = []

        # Initialize a counter to track the number of found keys
        found = int(self.found_keys_scanned_edit.text())
        startPrivKey = self.num

        # Generate keys based on the specified power format
        for i in range(0, self.power_format):
            dec = int(startPrivKey)
            HEX = f"{dec:016x}"
            if self.balance_check_checkbox.isChecked():
                caddr = ice.privatekey_to_address(0, True, dec)
                response_data = get_balance(caddr)
                if response_data:
                    confirmed_balance = response_data.get("confirmed", 0)
                    unconfirmed_balance = response_data.get("unconfirmed", 0)
                    tx_count = response_data.get("txs", 0)
                    received = response_data.get("received", 0)

                    # Convert satoshis to BTC
                    confirmed_balance_btc = confirmed_balance / 10**8
                    unconfirmed_balance_btc = unconfirmed_balance / 10**8
                    received_btc = received / 10**8

                    # Create a formatted string with balance information
                    BTCOUT = f'''               BTC Address: {caddr}
                >> Confirmed Balance: {confirmed_balance_btc:.8f} BTC     >> Unconfirmed Balance: {unconfirmed_balance_btc:.8f} BTC
                >> Total Received: {received_btc:.8f} BTC                 >> Transaction Count: {tx_count}'''

                    # Display the balance information in the text widget
                    self.value_edit_dec.setText(str(dec))
                    self.value_edit_hex.setText(HEX)
                    self.comp_text.setText(BTCOUT)
                    if confirmed_balance > 0:
                        found += 1
                        self.found_keys_scanned_edit.setText(str(found))
                        WINTEXT = f'''
Decimal Private Key : {dec}
Hexadecimal Private Key : {HEX}
BTC Address: {caddr}
>> Confirmed Balance: {confirmed_balance_btc:.8f} BTC     >> Unconfirmed Balance: {unconfirmed_balance_btc:.8f} BTC
>> Total Received: {received_btc:.8f} BTC                 >> Transaction Count: {tx_count}'''
                        with open("foundcaddr.txt", "a") as f:
                            f.write(WINTEXT)
                        if self.use_custom_credentials_checkbox.isChecked():
                            self.send_to_telegram(WINTEXT)
                        if self.win_checkbox.isChecked():
                            winner_dialog = miz.WinnerDialog(WINTEXT, self)
                            winner_dialog.exec()
                        
            else:
                # Append keys to their respective lists
                dec_keys.append(dec)
                HEX_keys.append(HEX)

                # Check checkboxes for different key formats
                if self.compressed_checkbox.isChecked():
                    caddr = ice.privatekey_to_address(0, True, dec)
                    if caddr in addfind:
                        # If address is found in "addfind", update the found counter and save information
                        found += 1
                        self.found_keys_scanned_edit.setText(str(found))
                        WINTEXT = f'\n {caddr} \n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX}  \n'
                        with open("foundcaddr.txt", "a") as f:
                            f.write(WINTEXT)
                        if self.use_custom_credentials_checkbox.isChecked():
                            self.send_to_telegram(WINTEXT)
                        if self.win_checkbox.isChecked():
                            winner_dialog = miz.WinnerDialog(WINTEXT, self)
                            winner_dialog.exec()

                    comp_keys.append(caddr)

                if self.uncompressed_checkbox.isChecked():
                    uaddr = ice.privatekey_to_address(0, False, dec)
                    if uaddr in addfind:
                        found += 1
                        self.found_keys_scanned_edit.setText(str(found))
                        WINTEXT = f'\n {uaddr} \n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX}  \n'
                        with open("founduaddr.txt", "a") as f:
                            f.write(WINTEXT)
                        if self.use_custom_credentials_checkbox.isChecked():
                            self.send_to_telegram(WINTEXT)
                        if self.win_checkbox.isChecked():
                            winner_dialog = miz.WinnerDialog(WINTEXT, self)
                            winner_dialog.exec()

                    uncomp_keys.append(uaddr)

                if self.p2sh_checkbox.isChecked():
                    p2sh = ice.privatekey_to_address(1, True, dec)
                    if p2sh in addfind:
                        found += 1
                        self.found_keys_scanned_edit.setText(str(found))
                        WINTEXT = f'\n {p2sh}\nDecimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX} \n'
                        with open("foundp2sh.txt", "a") as f:
                            f.write(WINTEXT)
                        if self.use_custom_credentials_checkbox.isChecked():
                            self.send_to_telegram(WINTEXT)
                        if self.win_checkbox.isChecked():
                            winner_dialog = miz.WinnerDialog(WINTEXT, self)
                            winner_dialog.exec()

                    p2sh_keys.append(p2sh)

                if self.bech32_checkbox.isChecked():
                    bech32 = ice.privatekey_to_address(2, True, dec)
                    if bech32 in addfind:
                        found += 1
                        self.found_keys_scanned_edit.setText(str(found))
                        WINTEXT = f'\n {bech32}\n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX} \n'
                        with open("foundbech32.txt", "a") as f:
                            f.write(WINTEXT)
                        if self.use_custom_credentials_checkbox.isChecked():
                            self.send_to_telegram(WINTEXT)
                        if self.win_checkbox.isChecked():
                            winner_dialog = miz.WinnerDialog(WINTEXT, self)
                            winner_dialog.exec()

                    bech32_keys.append(bech32)

            startPrivKey += 1
        if not self.balance_check_checkbox.isChecked():
            # Update GUI elements with generated keys and addresses
            self.value_edit_dec.setText(str(dec))
            self.value_edit_hex.setText(HEX)
            self.priv_text.setText('\n'.join(map(str, dec_keys)))
            self.HEX_text.setText('\n'.join(HEX_keys))
            self.uncomp_text.setText('\n'.join(uncomp_keys))
            self.comp_text.setText('\n'.join(comp_keys))
            self.p2sh_text.setText('\n'.join(p2sh_keys))
            self.bech32_text.setText('\n'.join(bech32_keys))

        # Save the current key if in sequence or reverse mode
        if self.sequence_button.isChecked():
            with open('start_scanned_key.txt', 'w') as f:
                f.write(HEX)
        elif self.reverse_button.isChecked():
            with open('end_scanned_key.txt', 'w') as f:
                f.write(HEX)


    def update_display(self, start, end):
        if not self.scanning:
            self.timer.stop()
            return

        def is_address_in_skip(address, skip_ranges):
            if isinstance(address, str):
                address = int(address, 16)

            for start, end in skip_ranges:
                if int(start, 16) <= address <= int(end, 16):
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

        total_steps = end - start
        max_value = 10000
        scaled_current_step = min(max_value, max(0, int(self.num * max_value / total_steps)))
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
if __name__ == '__main__':
    # Create an instance of the GUI and start the application
    gui_instance = GUIInstance()
    gui_instance.show()
    sys.exit(app.exec())

