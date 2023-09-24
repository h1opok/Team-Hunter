from PyQt6.QtWidgets import *
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6.QtCore import QTimer, Qt, QRect, QUrl
from PyQt6.QtGui import QPainter, QColor, QFont, QIcon
import subprocess
import requests
import os, sys
import gzip
import team_brain
import team_word
import secp256k1 as ice
import base58, binascii
version = '0.21'

# Define the function to get the balance of an address
def get_balance(addr):
    try:
        response = requests.get(f"https://api.haskoin.com/btc/address/{addr}/balance")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting balance for address {addr}: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending request for address {addr}: {str(e)}")

class UpdateBloomFilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Bloom Filter")
        self.setWindowIcon(QIcon('images/miz.ico'))
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
        self.setWindowIcon(QIcon('images/miz.ico'))
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
        self.setWindowIcon(QIcon('images/miz.ico'))
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
        self.setWindowIcon(QIcon('images/miz.ico'))
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
        self.setWindowIcon(QIcon('images/miz.ico'))
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
        self.setWindowIcon(QIcon('images/miz.ico'))
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
        self.setWindowIcon(QIcon('images/miz.ico'))
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
        self.setWindowIcon(QIcon('images/miz.ico'))
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
        self.setWindowIcon(QIcon('images/miz.ico'))
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
