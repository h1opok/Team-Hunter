from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

version = '0.21'

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