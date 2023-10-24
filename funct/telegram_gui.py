"""

@author: Team Mizogg
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt

ICO_ICON = "webfiles/css/images/main/miz.ico"
TITLE_ICON = "webfiles/css/images/main/title.png"

class Settings_telegram_Dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Telegram Settings")
        self.setWindowIcon(QIcon(f"{ICO_ICON}"))
        self.setMinimumSize(640, 440)
        pixmap = QPixmap(f"{TITLE_ICON}")
        # Create a QLabel and set the pixmap as its content
        title_label = QLabel()
        title_label.setPixmap(pixmap)
        title_label.setFixedSize(pixmap.size())
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.token_label = QLabel("Token:")
        self.token_edit = QLineEdit()
        
        self.chatid_label = QLabel("Chat ID:")
        self.chatid_edit = QLineEdit()
        
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        
        layout = QVBoxLayout()
        layout.addWidget(title_label)
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