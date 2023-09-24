import sys
sys.path.append('libs')
sys.path.append('config')
import os
import random
import time
import platform
import webbrowser
import locale
from config import *
import subprocess
import requests
import gzip
import base58, binascii
import json
try:
    from PyQt6.QtCore import *
    from PyQt6.QtWidgets import *
    from PyQt6.QtGui import *
    from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
    from bloomfilter import BloomFilter, ScalableBloomFilter, SizeGrowthRate
    import libs
    from libs import secp256k1 as ice
    from libs import team_brain
    from libs import team_word
    from libs import team_balance
    import qdarktheme
    import requests
    import datetime

except ImportError:
    print("Some required packages are missing. Please install them manually.")

version = "0.21"

# Set system locale
locale.setlocale(locale.LC_ALL, "")

def create_settings_file_if_not_exists():
    if not os.path.exists(CONFIG_FILE):
        config_data = {
            "Theme": {
                "theme": "dark"
            },
            "Telegram": {
                "token": "",
                "chatid": ""
            },
            "Discord": {
                "webhook_url": ""
            },
            "Addresses": {
                "START_ADDRESS": "",
                "END_ADDRESS": ""
            },
            "Paths": {
                "CSS_FOLDER": "css",
                "BLOOM_FOLDER": "bloom",
                "IMAGES_FOLDER": "images",
                "WINNER_FOLDER": "#WINNER",
                "GLOBAL_THEME": "global.css",
                "DARK_THEME": "dark.css",
                "LIGHT_THEME": "light.css",
                "WINNER_COMPRESSED": "foundcaddr.txt",
                "WINNER_UNCOMPRESSED": "founduaddr.txt",
                "WINNER_P2SH": "foundp2sh.txt",
                "WINNER_BECH32": "foundbech32.txt",
                "BTC_BF_FILE": "btc.bf",
                "BTC_TXT_FILE": "btc.txt"
            }
        }
        
        with open(CONFIG_FILE, "w") as file:
            json.dump(config_data, file, indent=4)

def initialize_application():
    app = QApplication(sys.argv)
    return app

def load_bloom_filter():
    try:
        with open(BTC_BF_FILE, "rb") as fp:
            addfind = BloomFilter.load(fp)
    except FileNotFoundError:
        try:
            with open(BTC_TXT_FILE) as file:
                addfind = file.read().split()
        except FileNotFoundError:
            addfind = []

    return addfind

def get_settings():
    settings_dict = {}
    try:
        with open(CONFIG_FILE, "r") as settings_file:
            for line in settings_file:
                line = line.strip()
                if "=" in line:
                    key, value = line.split("=", 1)
                    settings_dict[key] = value
    except FileNotFoundError:
        setting_message = "Settings file not found."
        QMessageBox.information(None, "File not found", setting_message)
    except Exception as e:
        error_message = f"An error occurred while reading settings: {e}"
        QMessageBox.critical(None, "Error", error_message)
    return settings_dict


# Main execution
if __name__ == "__main__":
    create_settings_file_if_not_exists()
    app = initialize_application()
    addfind = load_bloom_filter()
    settings = get_settings()

# Constants
INITIAL_WINDOW_X = 80
INITIAL_WINDOW_Y = 80
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 560

version = '0.21'

class UpdateBloomFilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Bloom Filter")
        self.setWindowIcon(QIcon('images/ico'))
        self.setMinimumSize(640, 440)
        self.url_edit = QLineEdit("http://addresses.loyce.club/Bitcoin_addresses_LATEST.txt.gz")
        self.url_edit.setPlaceholderText("Enter URL")
        self.update_button = QPushButton("Update")
        self.download_label = QLabel("Downloading:")
        self.extraction_label = QLabel("Extracting:")
        self.progress_bar = QProgressBar()
        self.extraction_progress_bar = QProgressBar()

        layout = QVBoxLayout()
        layout.addWidget(self.url_edit)
        layout.addWidget(self.update_button)
        layout.addWidget(self.download_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.extraction_label)
        layout.addWidget(self.extraction_progress_bar)
        self.setLayout(layout)

        self.update_button.clicked.connect(self.update_bloom_filter)

    def update_bloom_filter(self):
        url_str = self.url_edit.text()
        url = QUrl(url_str)
        self.filename = "Bitcoin_addresses_LATEST.txt.gz"
        
        # Check if the file already exists
        if os.path.exists(self.filename):
            confirm = QMessageBox.question(self, "File Exists", "The file already exists. Do you want to remove it?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                try:
                    os.remove(self.filename)
                except OSError as e:
                    QMessageBox.critical(self, "Error", f"Error removing existing file: {e}")
                    return
            else:
                return  # User chose not to remove the file

        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.download_finished)
        
        request = QNetworkRequest(url)
        self.reply = self.network_manager.get(request)
        self.reply.downloadProgress.connect(self.download_data_ready)  # Connect to downloadProgress

        self.progress_bar.setValue(0)

    def download_data_ready(self, bytes_received, bytes_total):
        if bytes_total > 0:
            progress = int(bytes_received / bytes_total * 100)
            self.progress_bar.setValue(progress)

    def download_finished(self):
        if self.reply.error() == QNetworkReply.NetworkError.NoError:
            with open(self.filename, "wb") as file:
                file.write(self.reply.readAll())

            txt_filename = self.filename.replace(".gz", ".txt")
            with gzip.open(self.filename, 'rb') as gz_file:
                with open(txt_filename, 'wb') as txt_file:
                    total_size = os.path.getsize(self.filename)  # Get the total size of the gzipped file
                    extracted_size = 0

                    while True:
                        chunk = gz_file.read(1024)
                        if not chunk:
                            break
                        txt_file.write(chunk)

                        extracted_size += len(chunk)
                        extraction_progress = int(extracted_size / total_size * 100)
                        self.extraction_progress_bar.setValue(extraction_progress)

            python_cmd = f'"{sys.executable}" Cbloom.py {txt_filename} btc.bf'
            subprocess.run(python_cmd, shell=True)

            QMessageBox.information(self, "Success", "Bloom filter updated successfully.")
        else:
            QMessageBox.critical(self, "Error", f"Download error: {self.reply.errorString()}")

        # Clean up downloaded file
        os.remove(self.filename)
        
# KnightRiderWidget: Custom QWidget for a Knight Rider-style animation of moving lights.
class KnightRiderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set up timer for animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        # Initialize position and direction
        self.position = 0
        self.direction = 1
        # Define light dimensions and spacing
        self.lightWidth = 35
        self.lightHeight = 12
        self.lightSpacing = 10
        # Set light color
        self.lightColor = QColor('#FF0000')
        # Configure widget properties
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
    def startAnimation(self):
        # Start the animation timer
        self.timer.start(5)

    def stopAnimation(self):
        # Stop the animation timer
        self.timer.stop()

    def paintEvent(self, event):
        # Override paint event to draw lights
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        for i in range(12):
            # Calculate position of each light
            lightX = self.position + i * (self.lightWidth + self.lightSpacing)
            lightRect = QRect(lightX, 0, self.lightWidth, self.lightHeight)
            # Draw rounded rectangle for each light
            painter.setBrush(self.lightColor)
            painter.drawRoundedRect(lightRect, 5, 5)

    def update(self):
        # Update position for animation
        self.position += self.direction
        # Reverse direction at edges
        if self.position <= 0 or self.position >= self.width() - self.lightWidth - self.lightSpacing:
            self.direction *= -1
        self.repaint()

class CustomProgressBar(QProgressBar):
    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        progress_str = f"Progress: {self.value() / self.maximum() * 100:.5f}%"

        font = QFont("Courier", 10)
        font.setBold(True)
        painter.setFont(font)
        
        if self.value() > 0:
            painter.setPen(QColor("#000000"))

        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, progress_str)
        
# WinnerDialog: Custom QDialog for displaying winner information.
class WinnerDialog(QDialog):
    def __init__(self, WINTEXT, parent=None):
        super().__init__(parent)
        self.setWindowTitle("QTMizICE_Display.py  WINNER")
        self.setWindowIcon(QIcon('images/ico'))
        self.setMinimumSize(640, 440)
        layout = QVBoxLayout(self)
        title_label = QLabel("!!!! 🎉 🥳CONGRATULATIONS🥳 🎉 !!!!")
        layout.addWidget(title_label)
        informative_label = QLabel("© MIZOGG 2018 - 2023")
        layout.addWidget(informative_label)
        detail_label = QPlainTextEdit(WINTEXT)
        layout.addWidget(detail_label)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)
        self.setMinimumSize(640, 440)

# ShowRangesDialog: Custom QDialog for displaying and managing ranges.
class ShowRangesDialog(QDialog):
    def __init__(self, ranges):
        super().__init__()
        self.setWindowTitle("Show Ranges")
        self.setWindowIcon(QIcon('images/ico'))
        self.setMinimumSize(640, 440)
        self.ranges = ranges
        self.hex_mode = False
        self.initUI()     
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        width = self.table.horizontalHeader().length() + 200
        height = min(400, self.table.rowCount() * 200)
        self.setFixedSize(width, height)

    def initUI(self):
        # Initialize the user interface components.
        layout = QVBoxLayout(self)
        button_layout = QHBoxLayout()

        # Toggle Hex/Decimal button
        self.toggle_button = QPushButton("Switch to Hex" if not self.hex_mode else "Switch to Decimal")
        self.toggle_button.setFixedWidth(200)
        self.toggle_button.clicked.connect(self.toggle_view)
        button_layout.addWidget(self.toggle_button)

        # Copy to Clipboard button
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.setFixedWidth(200)
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(self.copy_button)
        
        layout.addLayout(button_layout)

        # Table for displaying ranges
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Start", "End", "Delete"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        # Populate table with ranges
        for i, (start, end) in enumerate(self.ranges):
            self.add_range_row(i, start, end)

        layout.addWidget(self.table)
        
    def copy_to_clipboard(self):
        # Copy ranges to clipboard
        with open('skipped.txt', 'r') as f:
            clipboard_text = f.read()

        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_text)
        
        self.copy_button.setText("Copied!")
        
        timer = QTimer(self)
        timer.timeout.connect(lambda: self.copy_button.setText("Copy to Clipboard"))
        timer.start(2000)

    def add_range_row(self, row, start, end):
        # Add a row to the table for a range
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(self.to_dec(start) if self.hex_mode else str(start)))
        self.table.setItem(row, 1, QTableWidgetItem(self.to_dec(end) if self.hex_mode else str(end)))

        delete_button = QPushButton("Delete")
        delete_button.setStyleSheet("color: red")
        delete_button.clicked.connect(lambda _, row=row: self.delete_row(row))
        self.table.setCellWidget(row, 2, delete_button)

    def toggle_view(self):
        # Toggle between Hex and Decimal view
        self.hex_mode = not self.hex_mode
        self.toggle_button.setText("Switch to Hex" if not self.hex_mode else "Switch to Decimal")

        for i in range(self.table.rowCount()):
            start, end = self.ranges[i]
            self.table.item(i, 0).setText(self.to_dec(start) if self.hex_mode else str(start))
            self.table.item(i, 1).setText(self.to_dec(end) if self.hex_mode else str(end))

    def delete_row(self, row):
        if row >= 0 and row < len(self.ranges):
            # Delete a row from the table and update ranges
            self.table.removeRow(row)
            del self.ranges[row]
            self.update_skipped_file()

    def to_dec(self, num):
        return str(int(num,16))


    def update_skipped_file(self):
        # Update the skipped.txt file with current ranges
        with open('skipped.txt', 'w') as f:
            for start, end in self.ranges:
                f.write(f"{start}:{end}\n")
                
    def get_ranges(self):
        # Get the ranges from the table
        ranges = []

        for row in range(self.table.rowCount()):
            start = int(self.table.item(row, 0).text())
            end = int(self.table.item(row, 1).text())
            ranges.append((start, end))  # Append as a tuple

        return ranges


class Settings_telegram_Dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Telegram Settings")
        self.setWindowIcon(QIcon('images/ico'))
        self.setMinimumSize(640, 440)
        self.token_label = QLabel("Token:")
        self.token_edit = QLineEdit()
        
        self.chatid_label = QLabel("Chat ID:")
        self.chatid_edit = QLineEdit()
        
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        
        layout = QVBoxLayout()
        layout.addWidget(self.token_label)
        layout.addWidget(self.token_edit)
        layout.addWidget(self.chatid_label)
        layout.addWidget(self.chatid_edit)
        layout.addWidget(self.save_button)
        layout.addWidget(self.cancel_button)
        
        self.setLayout(layout)
        
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.reject)
    
    def save_settings(self):
        # Get the entered token and chatid
        token = self.token_edit.text()
        chatid = self.chatid_edit.text()
        if self.parent().dark_mode == True:
            theme = "dark"
        else:
            theme = "light"
        # Write the settings to the settings.txt file
        with open('settings.txt', 'w') as file:
            file.write(
f'''// Choose default theme [light] / [dark]
theme={theme}

// Telegram Settings
token={token}
chatid={chatid}'''
            )
        self.accept()  # Close the dialog

class Settings_discord_Dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Discord Settings")
        self.setWindowIcon(QIcon('images/ico'))
        self.setMinimumSize(640, 440)
        self.webhook_url_label = QLabel("Discord webhook_url:")
        self.webhook_url_edit = QLineEdit()
        
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        
        layout = QVBoxLayout()
        layout.addWidget(self.webhook_url_label)
        layout.addWidget(self.webhook_url_edit)
        layout.addWidget(self.save_button)
        layout.addWidget(self.cancel_button)
        
        self.setLayout(layout)
        
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.reject)
    
    def save_settings(self):
        # Get the entered token and chatid
        webhook_url = self.webhook_url_edit.text()
        if self.parent().dark_mode == True:
            theme = "dark"
        else:
            theme = "light"
        # Write the settings to the settings.txt file
        with open('settings.txt', 'w') as file:
            file.write(
f'''// Choose default theme [light] / [dark]
theme={theme}

// Discord Settings
webhook_url={webhook_url}'''
            )
        self.accept()  # Close the dialog

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About My QT Hunter")
        self.setWindowIcon(QIcon('images/ico'))
        self.setMinimumSize(640, 440)
        # Create a layout for the "About" dialog
        layout = QVBoxLayout()

        # Add information about your application
        app_name_label = QLabel("Hunter QT")
        app_version_label = QLabel(f"Version {version}")
        app_author_label = QLabel("Made by Mizogg & Firehawk52")
        app_description_label = QLabel('''
        Description: QT Hunter for Bitcoin is a feature-rich application designed for Bitcoin enthusiasts and researchers.
        It provides a comprehensive suite of tools for Bitcoin address generation, key scanning, and analysis.
        Whether you're hunting for lost Bitcoin addresses, conducting research, or exploring the blockchain,
        QT Hunter empowers you with the tools you need to navigate the Bitcoin ecosystem efficiently.
        ''')
        # Center-align text
        app_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add labels to the layout
        layout.addWidget(app_name_label)
        layout.addWidget(app_version_label)
        layout.addWidget(app_author_label)
        layout.addWidget(app_description_label)

        self.setLayout(layout)

class BalanceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("BTC Balance Check")
        self.setWindowIcon(QIcon('images/ico'))
        self.setMinimumSize(640, 440)
        self.btc_label = QLabel("BTC Address:")
        self.address_input = QLineEdit()
        
        self.Check_button = QPushButton("Check Balance (1,3,bc1)")
        self.cancel_button = QPushButton("Cancel")
        
        layout = QVBoxLayout()
        layout.addWidget(self.btc_label)
        layout.addWidget(self.address_input)
        layout.addWidget(self.Check_button)
        layout.addWidget(self.cancel_button)
        
        # Create a QLabel for displaying balance information
        self.balance_label = QLabel()
        layout.addWidget(self.balance_label)
        self.setLayout(layout)
        
        self.Check_button.clicked.connect(self.check_balance)
        self.cancel_button.clicked.connect(self.reject)
        
    def check_balance(self):
        # Get the Bitcoin address from the input field
        address = self.address_input.text()

        # Check the balance for the entered address
        response_data = team_balance.get_balance(address)

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
        self.setWindowIcon(QIcon('images/ico'))
        self.setMinimumSize(740, 440)

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
        self.setWindowIcon(QIcon('images/ico'))
        self.setMinimumSize(640, 440)
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

# GUIInstance: QWidget class for the main GUI interface.
class GUIInstance(QMainWindow):

    def __init__(self):
        super().__init__()

        # Set window geometry
        self.setGeometry(INITIAL_WINDOW_X, INITIAL_WINDOW_Y, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Create settings file if it doesn't exist
        create_settings_file_if_not_exists()

        # Initialize skip_ranges as an empty list and create an instance of ShowRangesDialog.
        self.skip_ranges = []
        self.ranges_dialog = ShowRangesDialog(self.skip_ranges)

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

        ranges_dialog = ShowRangesDialog(self)
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

        self.progress_bar = CustomProgressBar()
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
        self.knightRiderWidget = KnightRiderWidget(self)
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
        settings_dialog = Settings_telegram_Dialog(self)
        settings_dialog.exec()
    
    def open_discord_settings(self):
        settings_dialog = Settings_discord_Dialog(self)
        settings_dialog.exec()

    def balcheck(self):
        balance_dialog = BalanceDialog(self)
        balance_dialog.exec()
        
    def conv_check(self):
        conv_dialog = ConversionDialog(self)
        conv_dialog.exec()
        
    def range_check(self):
        range_dialog = RangeDialog(self)
        range_dialog.exec()
        
    def update_action_run(self):
        update_dialog = UpdateBloomFilterDialog(self)
        update_dialog.exec()

    def about(self):
        about_dialog = AboutDialog(self)
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
        return get_settings().get("theme", "dark")

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
        settings = get_settings()
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
        settings = get_settings()
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
            ranges_dialog = ShowRangesDialog(self.skip_ranges)
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
                response_data = team_balance.get_balance(caddr)

                if response_data:
                    confirmed_balance = response_data.get("confirmed", 0)
                    unconfirmed_balance = response_data.get("unconfirmed", 0)
                    tx_count = response_data.get("txs", 0)
                    received = response_data.get("received", 0)

                    confirmed_balance_btc = confirmed_balance / 10**8
                    unconfirmed_balance_btc = unconfirmed_balance / 10**8
                    received_btc = received / 10**8

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

                    if confirmed_balance > 0:
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
                            winner_dialog = WinnerDialog(WINTEXT, self)
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
                            winner_dialog = WinnerDialog(WINTEXT, self)
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
                            winner_dialog = WinnerDialog(WINTEXT, self)
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
                            winner_dialog = WinnerDialog(WINTEXT, self)
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
                            winner_dialog = WinnerDialog(WINTEXT, self)
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
