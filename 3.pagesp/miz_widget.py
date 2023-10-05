from PyQt6.QtWidgets import QWidget, QSizePolicy, QProgressBar, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QTableWidget, QAbstractItemView, QTableWidgetItem, QLineEdit, QMessageBox
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6.QtCore import QTimer, Qt, QRect, QUrl
from PyQt6.QtGui import QPainter, QColor, QFont, QIcon
import subprocess
import urllib.request
import os, sys
import gzip

class UpdateBloomFilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Bloom Filter")
        
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


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Telegram Settings")
        self.setWindowIcon(QIcon('images/miz.ico'))
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

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About My QT Hunter")
        self.setWindowIcon(QIcon('images/miz.ico'))
        # Create a layout for the "About" dialog
        layout = QVBoxLayout()

        # Add information about your application
        app_name_label = QLabel("Hunter QT")
        app_version_label = QLabel("Version: 0.2")
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