"""

@author: Team Mizogg
"""
import sys
import os
import signal
import platform
import subprocess
import locale
import base58, binascii
import webbrowser
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import qdarktheme
import libs
from libs import secp256k1 as ice, team_word, team_brain, team_balance

# Define constants
GLOBAL_THEME = "css/global.css"
DARK_THEME = "css/dark.css"
LIGHT_THEME = "css/light.css"
IMAGES_FOLDER = "images"
CUDA_INFO_EXE = "cudaInfo.exe"

# Set system locale
locale.setlocale(locale.LC_ALL, "")

version = '0.1'

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About My QT Hunter")
        self.setWindowIcon(QIcon(f"{IMAGES_FOLDER}/miz.ico"))
        self.setMinimumSize(640, 440)
        self.setStyleSheet("font-size: 14px; font-weight: bold; color: #E7481F;")
        # Create a layout for the "About" dialog

        layout = QVBoxLayout()
        pixmap = QPixmap(f"{IMAGES_FOLDER}/title.png")
        # Create a QLabel and set the pixmap as its content
        title_label = QLabel()
        title_label.setPixmap(pixmap)
        # Add information about your application
        app_name_label = QLabel("Hunter QT")
        app_version_label = QLabel(f"Version {version}")
        app_author_label = QLabel("Made by Team Mizogg")
        app_description_label = QLabel('''
        Description: QT Hunter for Bitcoin is a feature-rich application designed for Bitcoin enthusiasts and researchers.
        It provides a comprehensive suite of tools for Bitcoin address generation, key scanning, and analysis.
        Whether you're hunting for lost Bitcoin addresses, conducting research, or exploring the blockchain,
        QT Hunter empowers you with the tools you need to navigate the Bitcoin ecosystem efficiently.

        Recommended for 16GB of RAM: -b 104 -t 512 -p 2016
        Recommended for 8GB of RAM: -b 104 -t 512 -p 1024
        Recommended for 4GB of RAM: -b 52 -t 256 -p 256

        -b = Blocks
        -t = Threads
        -p = points
        ''')
        # Center-align text
        # Set the initial size and position for the QLabel
        title_label.setFixedSize(pixmap.size())
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        layout.addWidget(app_name_label)
        layout.addWidget(app_version_label)
        layout.addWidget(app_author_label)
        layout.addWidget(app_description_label)

        self.setLayout(layout)

class BalanceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("BTC Balance Check")
        self.setWindowIcon(QIcon(f"{IMAGES_FOLDER}/miz.ico"))
        self.setMinimumSize(640, 440)
        self.setStyleSheet("font-size: 14px; font-weight: bold; color: #E7481F;")
        pixmap = QPixmap(f"{IMAGES_FOLDER}/title.png")
        # Create a QLabel and set the pixmap as its content
        title_label = QLabel()
        title_label.setPixmap(pixmap)
        title_label.setFixedSize(pixmap.size())
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btc_label = QLabel("BTC Address:")
        self.address_input = QLineEdit()
        
        self.Check_button = QPushButton("Check Balance (1,3,bc1)")
        self.cancel_button = QPushButton("Cancel")
        
        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(self.btc_label)
        layout.addWidget(self.address_input)
        layout.addWidget(self.Check_button)
        layout.addWidget(self.cancel_button)
        
        # Create a QLabel for displaying balance information
        self.balance_label = QLabel()
        layout.addWidget(self.balance_label)
        self.setLayout(layout)
        
        self.Check_button.clicked.connect(self.get_balance)
        self.cancel_button.clicked.connect(self.reject)
        
    def get_balance(self):
        # Get the Bitcoin address from the input field
        address = self.address_input.text()
        confirmed_balance_btc, received_btc, unconfirmed_balance_btc, tx_count = team_balance.check_balance(address)
        # Create a formatted string with balance information
        BTCOUT = f"""               BTC Address: {address}
            >> Confirmed Balance: {confirmed_balance_btc:.8f} BTC     >> Unconfirmed Balance: {unconfirmed_balance_btc:.8f} BTC
            >> Total Received: {received_btc:.8f} BTC                 >> Transaction Count: {tx_count}"""

        # Display the balance information (you can show it in a label or text widget)
        self.balance_label.setText(
            BTCOUT
        )

class ConversionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Conversion Tools ")
        self.setWindowIcon(QIcon(f"{IMAGES_FOLDER}/miz.ico"))
        self.setMinimumSize(740, 440)
        self.setStyleSheet("font-size: 14px; font-weight: bold; color: #E7481F;")
        pixmap = QPixmap(f"{IMAGES_FOLDER}/title.png")
        # Create a QLabel and set the pixmap as its content
        title_label = QLabel()
        title_label.setPixmap(pixmap)
        title_label.setFixedSize(pixmap.size())
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hex_layout = QHBoxLayout()
        self.hex_label = QLabel("HEX TO DEC :")
        self.hex_input_edit = QLineEdit()
        self.hex_button = QPushButton("Check Hex")

        hex_layout.addWidget(self.hex_label)
        hex_layout.addWidget(self.hex_input_edit)
        hex_layout.addWidget(self.hex_button)

        dec_layout = QHBoxLayout()
        self.dec_label = QLabel("DEC TO HEX :")
        self.dec_input_edit = QLineEdit()
        self.dec_button = QPushButton("Check Dec")
        
        dec_layout.addWidget(self.dec_label)
        dec_layout.addWidget(self.dec_input_edit)
        dec_layout.addWidget(self.dec_button)

        wif_layout = QHBoxLayout()
        self.wif_label = QLabel("WIF :")
        self.wif_input_edit = QLineEdit()
        self.wif_button = QPushButton("Check WIF")

        wif_layout.addWidget(self.wif_label)
        wif_layout.addWidget(self.wif_input_edit)
        wif_layout.addWidget(self.wif_button)
        
        brain_layout = QHBoxLayout()
        self.brain_label = QLabel("Brain words :")
        self.brain_input_edit = QLineEdit()
        self.brain_button = QPushButton("Check Brain")
        
        brain_layout.addWidget(self.brain_label)
        brain_layout.addWidget(self.brain_input_edit)
        brain_layout.addWidget(self.brain_button)

        mnm_layout = QHBoxLayout()
        self.mnm_label = QLabel("Menmonics :")
        self.mnm_input_edit = QLineEdit()
        self.mnm_button = QPushButton("Check Words")
        
        mnm_layout.addWidget(self.mnm_label)
        mnm_layout.addWidget(self.mnm_input_edit)
        mnm_layout.addWidget(self.mnm_button)

        self.cancel_button = QPushButton("Cancel")
        
        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addLayout(hex_layout)
        layout.addLayout(dec_layout)
        layout.addLayout(wif_layout)
        layout.addLayout(brain_layout)
        layout.addLayout(mnm_layout)
        layout.addWidget(self.cancel_button)

        self.output_label = QPlainTextEdit()
        self.output_label.setReadOnly(True)
        self.output_label.setFont(QFont("Courier"))
        layout.addWidget(self.output_label)
        self.setLayout(layout)
        
        self.hex_button.clicked.connect(self.to_dec)
        self.dec_button.clicked.connect(self.to_hex)
        self.wif_button.clicked.connect(self.wif_in)
        self.brain_button.clicked.connect(self.brain_in)
        self.mnm_button.clicked.connect(self.word_in)
        self.cancel_button.clicked.connect(self.reject)

    def to_dec(self):
        num = self.hex_input_edit.text()
        try:
            dec_value = str(int(num, 16))
            caddr = ice.privatekey_to_address(0, True, int(dec_value))
            uaddr = ice.privatekey_to_address(0, False, int(dec_value))
            wifc = ice.btc_pvk_to_wif(num)
            wifu = ice.btc_pvk_to_wif(num, False)
            out_info = (f'\n HEX Input: {num} \n Private Key In Dec : {dec_value} \nBTC Address Compressed: {caddr} \nWIF Compressed: {wifc} \nBTC Address Uncompressed: {uaddr} \nWIF Uncompressed: {wifu}')
            self.output_label.appendPlainText(out_info)
        except ValueError:
            self.output_label.appendPlainText("Invalid input. Please enter a valid hexadecimal.")

    def to_hex(self):
        num = self.dec_input_edit.text()
        try:
            dec_value = int(num)
            caddr = ice.privatekey_to_address(0, True, dec_value)
            uaddr = ice.privatekey_to_address(0, False, dec_value)
            
            hex_value = hex(dec_value).upper()  # Convert to hexadecimal and make it uppercase
            wifc = ice.btc_pvk_to_wif(hex_value)
            wifu = ice.btc_pvk_to_wif(hex_value, False)
            out_info = (f'\n Dec Input: {num} \n Private Key In Hec : {hex_value} \nBTC Address Compressed: {caddr} \nWIF Compressed: {wifc} \nBTC Address Uncompressed: {uaddr} \nWIF Uncompressed: {wifu}')
            self.output_label.appendPlainText(out_info)
        except ValueError:
            self.output_label.appendPlainText("Invalid input. Please enter a valid decimal number.")

    def wif_in(self):
        wif = self.wif_input_edit.text()
        try:
            if wif.startswith('5H') or wif.startswith('5J') or wif.startswith('5K'):
                first_encode = base58.b58decode(wif)
                private_key_full = binascii.hexlify(first_encode)
                private_key = private_key_full[2:-8]
                private_key_hex = private_key.decode("utf-8")
                dec = int(private_key_hex, 16)
                uaddr = ice.privatekey_to_address(0, False, dec)
                out_info = (f'\n WIF Input: {wif} \n Private Key In Hec : {private_key_hex} \n Private Key In Dec : {dec} \n Bitcoin Uncompressed Adress : {uaddr}')
                self.output_label.appendPlainText(out_info)
            elif wif.startswith('K') or wif.startswith('L'):
                first_encode = base58.b58decode(wif)
                private_key_full = binascii.hexlify(first_encode)
                private_key = private_key_full[2:-8]
                private_key_hex = private_key.decode("utf-8")
                dec = int(private_key_hex[0:64], 16)
                caddr = ice.privatekey_to_address(0, True, dec)
                out_info = (f'\n WIF Input: {wif} \n Private Key In Hec : {private_key_hex} \n Private Key In Dec : {dec} \n Bitcoin Compressed Adress : {caddr}')
                self.output_label.appendPlainText(out_info)
        except ValueError:
            self.output_label.appendPlainText("Invalid input. Please enter a valid WIF Wallet.")

    def brain_in(self):
        passphrase = self.brain_input_edit.text()
        try:
            wallet = team_brain.BrainWallet()
            private_key, caddr = wallet.generate_address_from_passphrase(passphrase)
            brainvartext = (f'\n BrainWallet: {passphrase} \n Private Key In HEX : {private_key} \n Bitcoin Adress : {caddr}')
            self.output_label.appendPlainText(brainvartext)
        except ValueError:
            self.output_label.appendPlainText("Invalid input. Please enter a valid Brain Wallet.")

    def word_in(self):
        mnem = self.mnm_input_edit.text()
        try:
            seed = team_word.mnem_to_seed(mnem)
            for r in range (1,3):
                pvk = team_word.bip39seed_to_private_key(seed, r)
                pvk2 = team_word.bip39seed_to_private_key2(seed, r)
                pvk3 = team_word.bip39seed_to_private_key3(seed, r)
                dec = (int.from_bytes(pvk, "big"))
                HEX = "%064x" % dec
                dec2 = (int.from_bytes(pvk2, "big"))
                HEX2 = "%064x" % dec2
                dec3 = (int.from_bytes(pvk3, "big"))
                HEX3 = "%064x" % dec3
                cpath = f"m/44'/0'/0'/0/{r}"
                ppath = f"m/49'/0'/0'/0/{r}"
                bpath = f"m/84'/0'/0'/0/{r}"
                caddr = ice.privatekey_to_address(0, True, (int.from_bytes(pvk, "big")))
                p2sh = ice.privatekey_to_address(1, True, (int.from_bytes(pvk2, "big")))
                bech32 = ice.privatekey_to_address(2, True, (int.from_bytes(pvk3, "big")))
                wordvartext = (f'\n Bitcoin {cpath} :  {caddr} \n Dec : {dec} \n   Hex : {HEX}  \n Bitcoin {ppath} :  {p2sh}\n Dec : {dec2} \n  Hex : {HEX2} \n Bitcoin {bpath} : {bech32}\n  Dec : {dec3} \n  Hex : {HEX3} ')
                self.output_label.appendPlainText(wordvartext)
        except ValueError:
            self.output_label.appendPlainText("Invalid input. Please enter a valid Menmonics.")

class RangeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Range Divsion Tools ")
        self.setWindowIcon(QIcon(f"{IMAGES_FOLDER}/miz.ico"))
        self.setMinimumSize(640, 440)
        self.setStyleSheet("font-size: 14px; font-weight: bold; color: #E7481F;")
        pixmap = QPixmap(f"{IMAGES_FOLDER}/title.png")
        # Create a QLabel and set the pixmap as its content
        title_label = QLabel()
        title_label.setPixmap(pixmap)
        title_label.setFixedSize(pixmap.size())
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hex_label = QLabel("HEX  Start:")
        self.hex_input_edit = QLineEdit()
        self.hex_label_stop = QLabel("HEX  Stop:")
        self.hex_input_edit_stop = QLineEdit()
        
        power_label = QLabel("Show")
        power_label.setObjectName("powerLabel")
        self.format_combo_box_divs = QComboBox()
        self.format_combo_box_divs.addItems(
            ['2', '4', '8', '16', '32', '64', '128', '256', '512', '1024', '2048', '4096', '8192', '16384', '32768', '65536']
        )
        select_power_layout = QHBoxLayout()
        select_power_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        select_power_layout.addWidget(power_label)
        select_power_layout.addWidget(self.format_combo_box_divs)
        
        self.Check_button = QPushButton("Check")
        self.cancel_button = QPushButton("Cancel")
        
        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(self.hex_label)
        layout.addWidget(self.hex_input_edit)
        layout.addWidget(self.hex_label_stop)
        layout.addWidget(self.hex_input_edit_stop)
        layout.addLayout(select_power_layout)
        layout.addWidget(self.Check_button)
        layout.addWidget(self.cancel_button)

        self.output_label = QPlainTextEdit()
        self.output_label.setReadOnly(True)
        self.output_label.setFont(QFont("Courier"))
        layout.addWidget(self.output_label)
        self.setLayout(layout)

        self.Check_button.clicked.connect(self.div_range)
        self.cancel_button.clicked.connect(self.reject)

    def div_range(self):
        start_value = self.hex_input_edit.text()
        end_value = self.hex_input_edit_stop.text()
        num_divs = int(self.format_combo_box_divs.currentText())
        try:
            self.start_hex = int(start_value, 16)
            self.end_hex = int(end_value, 16)
            chunk_size = (self.end_hex - self.start_hex) // num_divs
            if self.end_hex < self.start_hex:
                error_range= (f'\n\n !!!!!  ERROR !!!!!! \n Your Start HEX {start_value} is MORE that your Stop HEX {end_value}')

            else:
                ranges = [(self.start_hex + i * chunk_size, self.start_hex + (i + 1) * chunk_size) for i in range(num_divs)]
                start_index = self.start_hex
                for i in range(num_divs - 1, -1, -1):
                    priv_start = ranges[i][0]
                    priv_end = ranges[i][1]
                    if start_index >= priv_start and start_index < priv_end:
                        displayprint = f' Range {i + 1}:\t{hex(priv_start)} - {hex(priv_end)}\t<<-- Current Range'
                        self.output_label.appendPlainText(displayprint)
                    else:
                        displayprint = f' Range {i + 1}:\t{hex(priv_start)} - {hex(priv_end)}'
                        self.output_label.appendPlainText(displayprint)
        except ValueError:
            self.output_label.appendPlainText("Invalid input. Please enter a Check Ranges.")


class CommandThread(QThread):
    commandOutput = pyqtSignal(str)
    commandFinished = pyqtSignal(int)

    def __init__(self, command):
        super().__init__()
        self.command = command
        self.process = None

    def run(self):
        self.commandOutput.emit(self.command)
        self.process = subprocess.Popen(
            self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )
        for line in self.process.stdout:
            output = line.strip()
            self.commandOutput.emit(output)
        self.process.stdout.close()
        self.commandFinished.emit(self.process.wait())

# Define ConsoleWindow class
class ConsoleWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.consoleOutput = QPlainTextEdit(self)
        self.consoleOutput.setReadOnly(True)
        self.consoleOutput.setStyleSheet("font-size: 14px; font-weight: bold; color: #E7481F;")
        self.layout.addWidget(self.consoleOutput)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.consoleOutput.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    @pyqtSlot(str)
    def append_output(self, output):
        self.consoleOutput.appendPlainText(output)

# Define MainWindow class
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Team Hunter GUI")
        self.setGeometry(50, 50, 960, 820)
        self.setStyleSheet("font-size: 14px; font-weight: bold; color: #E7481F;")
        # Create a QPixmap from the image file
        pixmap = QPixmap(f"{IMAGES_FOLDER}/title.png")
        # Create a QLabel and set the pixmap as its content
        self.title_label = QLabel(self)
        self.title_label.setPixmap(pixmap)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set the initial size and position for the QLabel
        self.title_label.setFixedSize(pixmap.size())
        self.process = None
        self.commandThread = None
        self.scanning = False
        self.initUI()

        self.theme_preference = self.get_theme_preference()
        self.dark_mode = self.theme_preference == "dark"
        self.toggle_theme()
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

    def initUI(self):
        self.setWindowIcon(QIcon(f"{IMAGES_FOLDER}/miz.ico"))
         # Create a spacer item to evenly space widgets
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        # Create the menu bar
        menubar = self.menuBar()

        # Define a function to create and add actions
        def add_menu_action(menu, text, function):
            action = QAction(text, self)
            action.triggered.connect(function)
            menu.addAction(action)

        # Create File menu
        file_menu = menubar.addMenu("File")
        add_menu_action(file_menu, "New Window", self.new_window)
        file_menu.addSeparator()

        file_menu.addSeparator()
        add_menu_action(file_menu, "Quit", self.exit_app)

        # Create Tools menu
        tools_menu = menubar.addMenu("Tools")
        add_menu_action(tools_menu, "Check Balance", self.balcheck)
        add_menu_action(tools_menu, "Conversion Tools", self.conv_check)
        add_menu_action(tools_menu, "Range Divsion", self.range_check)

        # Create Help menu
        help_menu = menubar.addMenu("Help")
        add_menu_action(help_menu, "Mizogg Website", self.open_website)
        add_menu_action(help_menu, "Help Telegram Group", self.open_telegram)
        add_menu_action(help_menu, "About", self.about)
        self.timer = QTimer(self)

        main_layout = QVBoxLayout()
        # Welcome Label
        self.dark_mode_button = QPushButton(self)
        self.dark_mode_button.setFixedSize(30, 30)
        self.dark_mode_button.clicked.connect(self.toggle_theme)
        self.dark_mode_button.setChecked(True if self.get_theme_preference() == "dark" else False)

        self.dark_mode = self.get_theme_preference() == "dark"
        self.load_dark_mode() if self.dark_mode else self.load_light_mode()
        self.toggle_theme()

        dark_mode_layout = QHBoxLayout()
        dark_mode_layout.addStretch()
        dark_mode_layout.addWidget(self.dark_mode_button)

        main_layout.addLayout(dark_mode_layout)
        # Create a QPixmap from the background image file

        labels_info = [
            {"text": f"Made by Team Mizogg", "object_name": "madeby"},
            {"text": f"Version {version}", "object_name": "version"},
            {"text": "© mizogg.com 2018 - 2023", "object_name": "copyright"},
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

        # Add labels to the labels_layout
        labels_layout.addWidget(self.title_label)
        main_layout.addLayout(labels_layout)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.layout = QHBoxLayout(self.centralWidget)

        left_layout = QVBoxLayout()
        self.layout.addLayout(left_layout)
        left_layout.addLayout(main_layout)

        # GPU Configuration
        self.gpuGroupBox = QGroupBox(self)
        self.gpuGroupBox.setTitle("GPU Configuration")
        self.gpuGroupBox.setStyleSheet("QGroupBox { border: 3px solid #E7481F; padding: 5px; }")
        self.gpuLayout = QVBoxLayout(self.gpuGroupBox)

         # Create a vertical layout for buttons
        self.deviceLayout = QHBoxLayout()
        self.GPUButton = QPushButton("🔋 Check GPU 🪫", self.gpuGroupBox)
        self.GPUButton.clicked.connect(self.list_if_gpu)
        self.deviceLayout.addWidget(self.GPUButton)

        self.blocksSizeLabel = QLabel("Block Size:", self)
        self.deviceLayout.addWidget(self.blocksSizeLabel)

        self.blocksSize_choice = QComboBox()
        for i in range(8, 153, 8):
            self.blocksSize_choice.addItem(str(i))
        self.blocksSize_choice.setCurrentIndex(12)
        self.blocksSize_choice.setMinimumWidth(60)
        self.deviceLayout.addWidget(self.blocksSize_choice)

        self.threadLabel_n = QLabel("Number of Threads:", self)
        self.deviceLayout.addWidget(self.threadLabel_n)
        self.threadComboBox_n = QComboBox()
        self.threadComboBox_n.addItems(['32', '64', '96', '128', '256', '512'])
        self.threadComboBox_n.setCurrentIndex(4)
        self.deviceLayout.addWidget(self.threadComboBox_n)

        self.pointsSizeLabel = QLabel("Points Size:", self)
        self.deviceLayout.addWidget(self.pointsSizeLabel)

        self.pointsSize_choice = QComboBox()
        self.pointsSize_choice.addItems(['256', '512', '1024', '2048'])
        self.pointsSize_choice.setCurrentIndex(1)
        self.deviceLayout.addWidget(self.pointsSize_choice)

        self.gpuIdLabel = QLabel("CUDA ONLY List of GPU(s) to use:", self.gpuGroupBox)
        self.deviceLayout.addWidget(self.gpuIdLabel)

        self.gpuIdLineEdit = QLineEdit("0", self.gpuGroupBox)
        self.gpuIdLineEdit.setPlaceholderText('0, 1, 2')
        self.deviceLayout.addWidget(self.gpuIdLineEdit)

        # Add the vertical button layout to the main horizontal layout
        self.gpuLayout.addLayout(self.deviceLayout)

        # Create a vertical layout for buttons
        self.buttonLayout = QHBoxLayout()

        self.StartButton = QPushButton("Start OpenCL", self.gpuGroupBox)
        self.StartButton.setObjectName("startButton")
        self.StartButton.clicked.connect(self.run_gpu_open)
        self.buttonLayout.addWidget(self.StartButton)

        self.StartButtonc = QPushButton("Start Cuda", self.gpuGroupBox)
        self.StartButtonc.setObjectName("startButton")
        self.StartButtonc.clicked.connect(self.run_gpu_cuda)
        self.buttonLayout.addWidget(self.StartButtonc)

        self.stopButton = QPushButton("Stop", self.gpuGroupBox)
        self.stopButton.setObjectName("stopButton")
        self.stopButton.clicked.connect(self.stop_hunt)
        self.buttonLayout.addWidget(self.stopButton)

        self.new_winButton = QPushButton("New Window", self.gpuGroupBox)
        self.new_winButton.setObjectName("stopButton")
        self.new_winButton.clicked.connect(self.new_window)
        self.buttonLayout.addWidget(self.new_winButton)

        # Add the vertical button layout to the main horizontal layout
        self.gpuLayout.addLayout(self.buttonLayout)

        # Add the spacer item to evenly space widgets
        self.gpuLayout.addItem(spacer)

        left_layout.addWidget(self.gpuGroupBox)

        # Key Space Configuration
        self.keyspaceGroupBox = QGroupBox(self)
        self.keyspaceGroupBox.setTitle("Key Space Configuration")
        self.keyspaceGroupBox.setStyleSheet("QGroupBox { border: 3px solid #E7481F; padding: 5px; }")

        # Main vertical layout for the group box
        keyspaceMainLayout = QVBoxLayout(self.keyspaceGroupBox)

        # Horizontal layout for Key Space label and line edit
        keyspaceLayout = QHBoxLayout()
        self.keyspaceLabel = QLabel("Key Space:", self)
        keyspaceLayout.addWidget(self.keyspaceLabel)
        self.keyspaceLineEdit = QLineEdit("20000000000000000:3ffffffffffffffff", self)
        self.keyspaceLineEdit.setPlaceholderText('Example range for 66 = 20000000000000000:3ffffffffffffffff')
        keyspaceLayout.addWidget(self.keyspaceLineEdit)

        # Add keyspaceLayout to the main layout
        keyspaceMainLayout.addLayout(keyspaceLayout)

        # Horizontal layout for the slider and its display label
        keyspacerange_layout = QHBoxLayout()
        self.keyspace_slider = QSlider(Qt.Orientation.Horizontal)
        self.keyspace_slider.setMinimum(1)
        self.keyspace_slider.setMaximum(256)
        self.keyspace_slider.setValue(66)
        self.slider_value_display = QLabel(self)
        keyspacerange_layout.addWidget(self.keyspace_slider)
        keyspacerange_layout.addWidget(self.slider_value_display)

        # Add keyspacerange_layout to the main layout
        keyspaceMainLayout.addLayout(keyspacerange_layout)
        keyspaceMainLayout.addItem(spacer)
        self.keyspace_slider.valueChanged.connect(self.update_keyspace_range)
        left_layout.addWidget(self.keyspaceGroupBox)

        # File Configuration
        self.outputFileGroupBox = QGroupBox(self)
        self.outputFileGroupBox.setTitle("File Configuration and Look Type (Compressed/Uncompressed)")
        self.outputFileGroupBox.setStyleSheet("QGroupBox { border: 3px solid #E7481F; padding: 5px; }")
        outputFileLayout = QHBoxLayout(self.outputFileGroupBox)
        self.lookLabel = QLabel("Look Type:", self)
        outputFileLayout.addWidget(self.lookLabel)
        self.lookComboBox = QComboBox()
        self.lookComboBox.addItem("compress")
        self.lookComboBox.addItem("uncompress")
        outputFileLayout.addWidget(self.lookComboBox)
        self.inputFileLabel = QLabel("Input File:", self)
        outputFileLayout.addWidget(self.inputFileLabel)
        self.inputFileLineEdit = QLineEdit("btc.txt", self)
        self.inputFileLineEdit.setPlaceholderText('Click browse to find your BTC database')
        outputFileLayout.addWidget(self.inputFileLineEdit)
        self.inputFileButton = QPushButton("Browse", self)
        self.inputFileButton.setStyleSheet("color: #E7481F;")
        self.inputFileButton.clicked.connect(self.browse_input_file)
        outputFileLayout.addWidget(self.inputFileButton)

        self.save_prog = QCheckBox("💾 Save Progress 💾")
        self.save_prog.setStyleSheet("font-size: 14px; font-weight: bold; color: red;")
        self.save_prog.setChecked(True)
        outputFileLayout.addWidget(self.save_prog)
        self.save_progButton = QPushButton("💾 Check Progress 💾")
        self.save_progButton.clicked.connect(self.check_prog)
        outputFileLayout.addWidget(self.save_progButton)
        self.found_progButton = QPushButton("🔥 Check if Found 🔥")
        self.found_progButton.clicked.connect(self.found_prog)
        outputFileLayout.addWidget(self.found_progButton)
        left_layout.addWidget(self.outputFileGroupBox)

        # Console Window
        self.consoleWindow = ConsoleWindow(self)
        left_layout.addWidget(self.consoleWindow)

        self.setCentralWidget(self.centralWidget)
        left_layout.addLayout(credit_label)

    
    def get_theme_preference(self):
        return ("theme", "dark")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.load_dark_mode() if self.dark_mode else self.load_light_mode()
        self.dark_mode_button.setText("🌞" if self.dark_mode else "🌙")

    def exit_app(self):
        QApplication.quit()

    def balcheck(self):
        balance_dialog = BalanceDialog(self)
        balance_dialog.exec()
        
    def conv_check(self):
        conv_dialog = ConversionDialog(self)
        conv_dialog.exec()
        
    def range_check(self):
        range_dialog = RangeDialog(self)
        range_dialog.exec()

    def update_keyspace_range(self, value):
        if value == 256:
            start_range = hex(2**(value - 1))[2:]
            end_range = "fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141"
            self.keyspaceLineEdit.setText(f"{start_range}:{end_range}")
            self.slider_value_display.setText(str(value))
        else:
            start_range = hex(2**(value - 1))[2:]
            end_range = hex(2**value - 1)[2:]
            self.keyspaceLineEdit.setText(f"{start_range}:{end_range}")
            self.slider_value_display.setText(str(value))
    
    def read_and_display_file(self, file_path, success_message, error_message):
        try:
            with open(file_path, 'r') as file:
                output_from_text = file.read()
                self.consoleWindow.append_output(success_message)
                self.consoleWindow.append_output(output_from_text)
        except FileNotFoundError:
            self.consoleWindow.append_output(f"⚠️ {error_message} File not found. Please check the file path.")
        except Exception as e:
            self.consoleWindow.append_output(f"An error occurred: {str(e)}")

    def check_prog(self):
        self.read_and_display_file('progress.txt', "Progress file found.", "Progress")

    def found_prog(self):
        self.read_and_display_file('found.txt', "File found. Check of Winners 😀 .", "No Winners Yet 😞")
    
    def browse_input_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Text Files (*.txt);;Binary Files (*.bin);;All Files (*.*)")
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            file_name = os.path.basename(file_path)
            self.inputFileLineEdit.setText(file_name)

    def about(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    def open_website(self):
        webbrowser.open("https://mizogg.co.uk")

    def open_telegram(self):
        webbrowser.open("https://t.me/CryptoCrackersUK")

    def list_if_gpu(self):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        cuda_info_exe_path = os.path.join(script_directory, CUDA_INFO_EXE)
        if os.path.isfile(cuda_info_exe_path):
            command = cuda_info_exe_path
            self.run(command)
        else:
            self.consoleWindow.append_output("cudaInfo.exe not found in the script's directory.")

    def run(self, command):
        self.process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
        for line in self.process.stdout:
            output = line.strip()
            self.consoleWindow.append_output(output)
        self.process.stdout.close()

    def run_gpu_open(self):
        command = self.construct_command("clBitcrack")
        self.execute_command(command)

    def run_gpu_cuda(self):
        command = self.construct_command("cuBitcrack")
        self.execute_command(command)

    def construct_command(self, mode):
        gpu_ids = self.gpuIdLineEdit.text().strip()
        gpu_blocks = self.blocksSize_choice.currentText()
        gpu_points = self.pointsSize_choice.currentText()
        thread_count_n = int(self.threadComboBox_n.currentText())
        command = f"{mode} -d {gpu_ids}  -b {gpu_blocks} -p {gpu_points} -t {thread_count_n}"
        look = self.lookComboBox.currentText().strip()
        if look == 'compress':
            command += " -c"
        elif look == 'uncompress':
            command += " -u"

        output_file = "found.txt"
        command += f" -o {output_file}"

        keyspace = self.keyspaceLineEdit.text().strip()
        if keyspace:
            command += f" --keyspace {keyspace}"

        input_file = self.inputFileLineEdit.text().strip()
        if input_file:
            command += f" -i {input_file}"

        if self.save_prog.isChecked():
            command += " --continue progress.txt"
        return command

    def stop_hunt(self):
        if self.commandThread and self.commandThread.isRunning():
            if platform.system() == "Windows":
                subprocess.Popen(["taskkill", "/F", "/T", "/PID", str(self.commandThread.process.pid)])
            else:
                os.killpg(os.getpgid(self.commandThread.process.pid), signal.SIGTERM)
            
            self.timer.stop()
            self.scanning = False
            returncode = 'Closed'
            self.command_finished(returncode)

    @pyqtSlot()
    def new_window(self):
        python_cmd = f'start cmd /c "{sys.executable}" TeamHunter.py'
        subprocess.Popen(python_cmd, shell=True)

    @pyqtSlot()
    def execute_command(self, command):
        if self.scanning:
            return

        self.scanning = True

        if self.commandThread and self.commandThread.isRunning():
            self.commandThread.terminate()

        self.commandThread = CommandThread(command)
        self.commandThread.commandOutput.connect(self.consoleWindow.append_output)
        self.commandThread.commandFinished.connect(self.command_finished)
        self.commandThread.start()
        self.timer.start(100)
    
    @pyqtSlot(int)
    def command_finished(self, returncode):
        self.timer.stop()
        self.scanning = False
        if returncode == 0:
            finish_scan = "Command execution finished successfully"
            self.consoleWindow.append_output(finish_scan)
        elif returncode == 'Closed':
            finish_scan = "Process has been stopped by the user"
            self.consoleWindow.append_output(finish_scan)
        else:
            error_scan = "Command execution failed"
            self.consoleWindow.append_output(error_scan)

    def closeEvent(self, event):
        self.stop_hunt()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())