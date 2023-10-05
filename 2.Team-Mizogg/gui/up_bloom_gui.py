from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import gzip
import os

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
