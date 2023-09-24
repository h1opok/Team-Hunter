from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import sys
sys.path.append('libs')
import libs
from libs import secp256k1 as ice
from libs import team_balance


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
