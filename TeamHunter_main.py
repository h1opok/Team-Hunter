"""
@author: Team Mizogg
"""
import os
import signal
import platform
import subprocess
import webbrowser
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
import qdarktheme
from libs import set_settings, create_setting
from funct import (range_div_gui, about_gui, ice_gui, bitcrack_gui, keyhunt_gui, vanbit_gui, up_bloom_gui, grid_16x16, mnemonic_gui, rotacuda_gui)
import sys
sys.path.extend(['libs', 'config', 'funct', 'found', 'input'])

from config import *

GLOBAL_THEME = "webfiles/css/global.css"
DARK_THEME = "webfiles/css/dark.css"
LIGHT_THEME = "webfiles/css/light.css"
ICO_ICON = "webfiles/css/images/main/miz.ico"
TITLE_ICON = "webfiles/css/images/main/titlebig.png"
PK_ICON = "webfiles/css/images/main/logopk.png"
PKF_ICON = "webfiles/css/images/main/logopkf.png"
BC_ICON = "webfiles/css/images/main/logobc.png"
MIZ_ICON = "webfiles/css/images/main/mizogg-eyes.png"
LOYCE_ICON = "webfiles/css/images/main/loyce.png"
ALBERTO_ICON = "webfiles/css/images/main/alberto.jpeg"
BLACK_ICON = "webfiles/css/images/main/python-snake-black.png"
RED_ICON = "webfiles/css/images/main/python-snake-red.png"
image_folder = "webfiles/css/images"
image_files = [os.path.join(image_folder, filename) for filename in os.listdir(image_folder) if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

version = '0.4'

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Team Hunter GUI")
        self.setWindowIcon(QIcon(f"{ICO_ICON}"))
        self.setGeometry(50, 50, 680, 680)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setObjectName("QTabWidget")
        self.setCentralWidget(self.tab_widget)

        self.tabmain = QWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tab5 = QWidget()
        self.tab6 = QWidget()
        self.tab7 = QWidget()
        self.tab8 = QWidget()
        self.tab9 = QWidget()
        self.tab10 = QWidget()

        self.tab_widget.addTab(self.tabmain, "Welcome")
        self.tab_widget.addTab(self.tab1, "BitCrack")
        self.tab_widget.addTab(self.tab2, "KeyHunt")
        self.tab_widget.addTab(self.tab3, "Vanbitcracken")
        self.tab_widget.addTab(self.tab4, "Iceland2k14 Secp256k1")
        self.tab_widget.addTab(self.tab5, "Conversion Tools / BrainWallet")
        self.tab_widget.addTab(self.tab6, "Menmonics Tools")
        self.tab_widget.addTab(self.tab7, "Art Work")
        self.tab_widget.addTab(self.tab8, "Mizogg's Tools")
        self.tab_widget.addTab(self.tab9, "C-Sharp-Mnemonic")
        self.tab_widget.addTab(self.tab10, "Rota Cuda")
        self.process = None
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
        self.init_webviews()
        menubar = self.menuBar()
        def add_menu_action(menu, text, function):
            action = QAction(text, self)
            action.triggered.connect(function)
            menu.addAction(action)

        file_menu = menubar.addMenu("File")
        add_menu_action(file_menu, "New Window", self.new_window)
        file_menu.addSeparator()

        file_menu.addSeparator()
        add_menu_action(file_menu, "Quit", self.exit_app)

        help_menu = menubar.addMenu("Help")
        add_menu_action(help_menu, "Help Telegram Group", self.open_telegram)
        add_menu_action(help_menu, "About", self.about)
        self.timer = QTimer(self)

        main_layout = QVBoxLayout()
        self.dark_mode_button = QPushButton(self)
        self.dark_mode_button.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;">Switch Between Dark and Light Theme</span>')
        self.dark_mode_button.setStyleSheet("font-size: 16pt;")
        self.dark_mode_button.clicked.connect(self.toggle_theme)
        self.dark_mode_button.setChecked(True if self.get_theme_preference() == "dark" else False)

        self.grid_mode_button = QPushButton(self)
        self.grid_mode_button.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;">Run 16x16 Grid Hunter</span>')
        self.grid_mode_button.setStyleSheet("font-size: 16pt;")
        self.grid_mode_button.setText("🏁")
        self.grid_mode_button.clicked.connect(self.load_16x16)

        self.div_mode_button = QPushButton(self)
        self.div_mode_button.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;">Range Divsion in HEX </span>')
        self.div_mode_button.setStyleSheet("font-size: 16pt;")
        self.div_mode_button.setText("📊")
        self.div_mode_button.clicked.connect(self.range_check)

        icon_size = QSize(32, 32)
        iconpk = QIcon(QPixmap(PK_ICON))
        iconpkf = QIcon(QPixmap(PKF_ICON))
        iconbc = QIcon(QPixmap(BC_ICON))
        iconmiz = QIcon(QPixmap(MIZ_ICON))
        iconloyce = QIcon(QPixmap(LOYCE_ICON))
        iconalberto = QIcon(QPixmap(ALBERTO_ICON))
        iconblack = QIcon(QPixmap(BLACK_ICON))
        iconred = QIcon(QPixmap(RED_ICON))

        self.pkeys_mode_button = QPushButton(self)
        self.pkeys_mode_button.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;">Private Keys PW (Private Keys Database)</span>')
        self.pkeys_mode_button.setStyleSheet("font-size: 16pt;")
        self.pkeys_mode_button.setIconSize(icon_size)
        self.pkeys_mode_button.setIcon(iconpk)
        self.pkeys_mode_button.clicked.connect(self.privatekeys_check)

        self.pkeysfinder_mode_button = QPushButton(self)
        self.pkeysfinder_mode_button.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;">PrivateKeyFinder.io (Private Keys Database)</span>')
        self.pkeysfinder_mode_button.setStyleSheet("font-size: 16pt;")
        self.pkeysfinder_mode_button.setIconSize(icon_size)
        self.pkeysfinder_mode_button.setIcon(iconpkf)
        self.pkeysfinder_mode_button.clicked.connect(self.privatekeyfinder_check)

        self.blockchain_mode_button = QPushButton(self)
        self.blockchain_mode_button.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;">Blockchain.com (Relentlessly building the future of finance since 2011)</span>')
        self.blockchain_mode_button.setStyleSheet("font-size: 16pt;")
        self.blockchain_mode_button.setIconSize(icon_size)
        self.blockchain_mode_button.setIcon(iconbc)
        self.blockchain_mode_button.clicked.connect(self.blockchain_check)

        self.mizogg_mode_button = QPushButton(self)
        self.mizogg_mode_button.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;">Mizogg.co.uk (Come Meet Mizogg Check out my Website and other programs)</span>')
        self.mizogg_mode_button.setStyleSheet("font-size: 16pt;")
        self.mizogg_mode_button.setIconSize(icon_size)
        self.mizogg_mode_button.setIcon(iconmiz)
        self.mizogg_mode_button.clicked.connect(self.open_website)

        self.loyce_mode_button = QPushButton(self)
        self.loyce_mode_button.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;">LOYCE.CLUB (Bitcoin Data)</span>')
        self.loyce_mode_button.setStyleSheet("font-size: 16pt;")
        self.loyce_mode_button.setIconSize(icon_size)
        self.loyce_mode_button.setIcon(iconloyce)
        self.loyce_mode_button.clicked.connect(self.loyce_check)

        self.alberto_mode_button = QPushButton(self)
        self.alberto_mode_button.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;">GitHub Alertobsd Keyhunt About</span>')
        self.alberto_mode_button.setStyleSheet("font-size: 16pt;")
        self.alberto_mode_button.setIconSize(icon_size)
        self.alberto_mode_button.setIcon(iconblack)
        self.alberto_mode_button.clicked.connect(self.alberto_git)

        self.XopMC_mode_button = QPushButton(self)
        self.XopMC_mode_button.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;">GitHub Михаил Х. XopMC C#-Mnemonic About</span>')
        self.XopMC_mode_button.setStyleSheet("font-size: 16pt;")
        self.XopMC_mode_button.setIconSize(icon_size)
        self.XopMC_mode_button.setIcon(iconred)
        self.XopMC_mode_button.clicked.connect(self.XopMC_git)

        self.bitcrack_mode_button = QPushButton(self)
        self.bitcrack_mode_button.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;">GitHub brichard19 BitCrack About</span>')
        self.bitcrack_mode_button.setStyleSheet("font-size: 16pt;")
        self.bitcrack_mode_button.setIconSize(icon_size)
        self.bitcrack_mode_button.setIcon(iconblack)
        self.bitcrack_mode_button.clicked.connect(self.bitcrack_git)

        self.vanbit_mode_button = QPushButton(self)
        self.vanbit_mode_button.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;">GitHub WanderingPhilosopher VanBitCracken Random About</span>')
        self.vanbit_mode_button.setStyleSheet("font-size: 16pt;")
        self.vanbit_mode_button.setIconSize(icon_size)
        self.vanbit_mode_button.setIcon(iconred)
        self.vanbit_mode_button.clicked.connect(self.vanbit_git)

        self.iceland_mode_button = QPushButton(self)
        self.iceland_mode_button.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;">GitHub Iceland iceland2k14 Python Secp256k1 About</span>')
        self.iceland_mode_button.setStyleSheet("font-size: 16pt;")
        self.iceland_mode_button.setIconSize(icon_size)
        self.iceland_mode_button.setIcon(iconblack)
        self.iceland_mode_button.clicked.connect(self.iceland_git)

        self.miz_git_mode_button = QPushButton(self)
        self.miz_git_mode_button.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;">GitHub Mizogg About</span>')
        self.miz_git_mode_button.setStyleSheet("font-size: 16pt;")
        self.miz_git_mode_button.setIconSize(icon_size)
        self.miz_git_mode_button.setIcon(iconred)
        self.miz_git_mode_button.clicked.connect(self.miz_git)

        self.dark_mode = self.get_theme_preference() == "dark"
        self.load_dark_mode() if self.dark_mode else self.load_light_mode()
        self.toggle_theme()

        dark_mode_layout = QHBoxLayout()
        dark_mode_layout.addWidget(self.pkeys_mode_button)
        dark_mode_layout.addWidget(self.pkeysfinder_mode_button)
        dark_mode_layout.addWidget(self.blockchain_mode_button)
        dark_mode_layout.addWidget(self.mizogg_mode_button)
        dark_mode_layout.addWidget(self.loyce_mode_button)
        dark_mode_layout.addStretch()

        dark_mode_layout.addWidget(self.alberto_mode_button)
        dark_mode_layout.addWidget(self.XopMC_mode_button)
        dark_mode_layout.addWidget(self.bitcrack_mode_button)
        dark_mode_layout.addWidget(self.vanbit_mode_button)
        dark_mode_layout.addWidget(self.iceland_mode_button)
        dark_mode_layout.addWidget(self.miz_git_mode_button)

        dark_mode_layout.addStretch()
        dark_mode_layout.addWidget(self.grid_mode_button)
        dark_mode_layout.addWidget(self.div_mode_button)
        dark_mode_layout.addWidget(self.dark_mode_button)

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

        main_layout.addWidget(self.tab_widget)
        
        self.tabmain_layout = QVBoxLayout()
        self.tab1_layout = QVBoxLayout()
        self.tab2_layout = QVBoxLayout()
        self.tab3_layout = QVBoxLayout()
        self.tab4_layout = QVBoxLayout()
        self.tab5_layout = QVBoxLayout()
        self.tab6_layout = QVBoxLayout()
        self.tab7_layout = QVBoxLayout()
        self.tab8_layout = QVBoxLayout()
        self.tab9_layout = QVBoxLayout()
        self.tab10_layout = QVBoxLayout()

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout(self.centralWidget)

        bitcrack_tool = bitcrack_gui.BitcrackFrame()
        keyhunt_tool = keyhunt_gui.KeyHuntFrame()
        vanbit_tool = vanbit_gui.VanbitFrame()
        ice_tool = ice_gui.GUIInstance()
        XopMC_tool = mnemonic_gui.MnemonicFrame()
        rota_tool = rotacuda_gui.RotacudaFrame()
        
        self.tabmain_layout = self.main_tab()
        self.tab1_layout.addWidget(bitcrack_tool)
        self.tab2_layout.addWidget(keyhunt_tool)
        self.tab3_layout.addWidget(vanbit_tool)
        self.tab4_layout.addWidget(ice_tool)
        self.tab5_layout.addWidget(self.webview_con)
        self.tab6_layout.addWidget(self.webview_bip39)
        self.tab7_layout = self.picture_tab()
        self.tab8_layout.addWidget(self.webview_miz)
        self.tab9_layout.addWidget(XopMC_tool)
        self.tab10_layout.addWidget(rota_tool)

        self.tabmain.setLayout(self.tabmain_layout)
        self.tab1.setLayout(self.tab1_layout)
        self.tab2.setLayout(self.tab2_layout)
        self.tab3.setLayout(self.tab3_layout)
        self.tab4.setLayout(self.tab4_layout)
        self.tab5.setLayout(self.tab5_layout)
        self.tab6.setLayout(self.tab6_layout)
        self.tab7.setLayout(self.tab7_layout)
        self.tab8.setLayout(self.tab8_layout)
        self.tab9.setLayout(self.tab9_layout)
        self.tab10.setLayout(self.tab10_layout)
        self.setCentralWidget(self.centralWidget)

        self.layout.addLayout(main_layout)
        main_layout.addLayout(dark_mode_layout)
        self.layout.addLayout(credit_label)

    def create_tab_buttons(self):
        buttons_layout = QGridLayout()

        tabs = ["BitCrack", "KeyHunt", "Vanbitcracken", "Iceland2k14 Secp256k1", "Conversion Tools / BrainWallet",
                "Menmonics Tools", "Art Work", "Mizogg's Tools", "C-Sharp-Mnemonic"]

        for i, tab_name in enumerate(tabs):
            row = i // 3
            col = i % 3

            button = QPushButton(tab_name)
            button.setObjectName("startButton")
            button.clicked.connect(self.switch_to_tab(i + 1))
            buttons_layout.addWidget(button, row, col)

        return buttons_layout

    def main_tab(self):
        pixmap = QPixmap(f"{TITLE_ICON}")
        title_label = QLabel(self)
        title_label.setPixmap(pixmap)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layoutmain = QVBoxLayout()
        labels_layout = QHBoxLayout()
        combined_text = """
        <html><center>
        <font size="18" color="#E7481F">❤️ Welcome to TeamHunter ₿itcoin Scanner ❤️</font>
        <br><br><font size="8" color="#E7481F">
        Good Luck and Happy Hunting Mizogg<br>
        ⭐ https://mizogg.co.uk ⭐
        </font><br>
        <br>
        <br><font size="4">
        This Python application, named "Team Hunter GUI," provides a user-friendly interface for various cryptocurrency-related tools and functions.<br>
        Users can access tools for Bitcoin-related operations, including BitCrack, KeyHunt, Vanbitcracken, Iceland2k14 Secp256k1, and conversion tools.<br>
        The application supports both dark and light themes and offers a convenient way to switch between them.<br>
        It also features a 16x16 grid tool, a range division tool in hexadecimal format, and allows users to open external websites.<br>
        This application is built using PyQt6 and is designed to assist cryptocurrency enthusiasts in their endeavors.</font>
        </center><br><br><br></html>
        """

        welcome_label = QLabel(combined_text)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        buttons_layout = self.create_tab_buttons()
        layoutmain.addWidget(title_label)
        layoutmain.addWidget(welcome_label)
        layoutmain.addLayout(buttons_layout)
        return layoutmain
    
    def switch_to_tab(self, tab_index):
        def switch():
            self.tab_widget.setCurrentIndex(tab_index)
        return switch

    def init_webviews(self):
        self.webview_con = self.setup_webview("/webfiles/conversion.html")
        self.webview_bip39 = self.setup_webview("/webfiles/bip39.html")
        self.webview_miz = self.setup_webview("http://109.205.181.6/")

    def setup_webview(self, url):
        webview = QWebEngineView(self)
        if url.startswith("http:") or url.startswith("https:"):
            webview.setUrl(QUrl(url))
        else:
            local_url = QUrl.fromLocalFile(url)
            webview.setUrl(QUrl(local_url))
        return webview

    def picture_tab(self):
        picture_layout = QHBoxLayout()
        for image_path in image_files:
            pixmap = QPixmap(image_path)
            pic_label = QLabel()
            pic_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tab_size = self.tab_widget.widget(0).size()
            scaled_pixmap = pixmap.scaled(tab_size, Qt.AspectRatioMode.KeepAspectRatio)
            pic_label.setPixmap(scaled_pixmap)
            pic_label.setFixedSize(scaled_pixmap.size())
            picture_layout.addWidget(pic_label)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(QWidget())
        scroll_area.widget().setLayout(picture_layout)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        next_button = QPushButton("Next")
        prev_button = QPushButton("Previous")
        current_index = 0

        def next_picture():
            nonlocal current_index
            current_index = (current_index + 1) % len(image_files)
            scroll_area.horizontalScrollBar().setValue(current_index * tab_size.width())

        def prev_picture():
            nonlocal current_index
            current_index = (current_index - 1 + len(image_files)) % len(image_files)
            scroll_area.horizontalScrollBar().setValue(current_index * tab_size.width())

        next_button.clicked.connect(next_picture)
        prev_button.clicked.connect(prev_picture)
        button_layout = QVBoxLayout()
        button_layout.addWidget(prev_button)
        button_layout.addWidget(next_button)
        pic_layout = QVBoxLayout()
        pic_layout.addWidget(scroll_area)
        pic_layout.addLayout(button_layout)
        return pic_layout

    def range_check(self):
        range_dialog = range_div_gui.RangeDialog(self)
        range_dialog.show()
        
    def get_theme_preference(self):
        return ("theme", "dark")

    def load_16x16(self):
        self.frame_16x16 = grid_16x16.GridFrame()
        self.frame_16x16.show()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.load_dark_mode() if self.dark_mode else self.load_light_mode()
        self.dark_mode_button.setText("🌞" if self.dark_mode else "🌙")

    def exit_app(self):
        QApplication.quit()

    def about(self):
        about_dialog = about_gui.AboutDialog(self)
        about_dialog.exec()

    def open_website(self):
        webbrowser.open("https://mizogg.co.uk")

    def open_telegram(self):
        webbrowser.open("https://t.me/CryptoCrackersUK")

    def privatekeys_check(self):
        webbrowser.open("https://privatekeys.pw")

    def privatekeyfinder_check(self):
        webbrowser.open("https://privatekeyfinder.io/")

    def blockchain_check(self):
        webbrowser.open("https://www.blockchain.com/")

    def loyce_check(self):
        webbrowser.open("http://addresses.loyce.club/")

    def alberto_git(self):
        webbrowser.open("https://github.com/albertobsd/keyhunt")

    def XopMC_git(self):
        webbrowser.open("https://github.com/XopMC/C-Sharp-Mnemonic")

    def bitcrack_git(self):
        webbrowser.open("https://github.com/brichard19/BitCrack")

    def vanbit_git(self):
        webbrowser.open("https://github.com/WanderingPhilosopher/VanBitCrackenRandom#vanbitcrackenrandom")

    def iceland_git(self):
        webbrowser.open("https://github.com/iceland2k14/secp256k1")

    def miz_git(self):
        webbrowser.open("https://github.com/Mizogg")

    @pyqtSlot()
    def new_window(self):
        python_cmd = f'start cmd /c "{sys.executable}" TeamHunter_main.py'
        subprocess.Popen(python_cmd, shell=True)

if __name__ == "__main__":
    create_setting.create_settings_file_if_not_exists()
    settings = set_settings.get_settings()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())