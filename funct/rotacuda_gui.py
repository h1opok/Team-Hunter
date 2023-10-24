"""
@author: Team Mizogg
"""
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import os
import subprocess
import multiprocessing
import platform
from console_gui import ConsoleWindow
from command_thread import CommandThread

class RotacudaFrame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cpu_count = multiprocessing.cpu_count()
        self.scanning = False
        self.timer = QTimer(self)
        self.commandThread = None
        
        main_layout = QVBoxLayout()

        bitcrack_config = self.create_rotacudaGroupBox()
        main_layout.addWidget(bitcrack_config)
        
        key_space_config = self.create_keyspaceGroupBox()
        main_layout.addWidget(key_space_config)

        output_file_config = self.create_outputFileGroupBox()
        main_layout.addWidget(output_file_config)

        buttonLayout = QHBoxLayout()
        start_button = self.create_start_button()
        stop_button = self.create_stop_button()

        buttonLayout.addWidget(start_button)
        buttonLayout.addWidget(stop_button)

        main_layout.addLayout(buttonLayout)

        self.consoleWindow = ConsoleWindow(self)
        main_layout.addWidget(self.consoleWindow)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    # Function to create the Key Space Configuration GUI
    def create_keyspaceGroupBox(self):
        keyspaceGroupBox = QGroupBox(self)
        keyspaceGroupBox.setTitle("Key Space Configuration")
        keyspaceGroupBox.setStyleSheet("QGroupBox { border: 3px solid #E7481F; padding: 5px; }")
        keyspaceMainLayout = QVBoxLayout(keyspaceGroupBox)

        keyspaceLayout = QHBoxLayout()
        keyspaceLabel = QLabel("Key Space:")
        keyspaceLayout.addWidget(keyspaceLabel)
        self.keyspaceLineEdit = QLineEdit("20000000000000000:3ffffffffffffffff")
        keyspaceLayout.addWidget(self.keyspaceLineEdit)
        keyspaceMainLayout.addLayout(keyspaceLayout)

        # Add slider for key space range
        keyspacerange_layout = QHBoxLayout()
        keyspace_slider = QSlider(Qt.Orientation.Horizontal)
        keyspace_slider.setMinimum(1)
        keyspace_slider.setMaximum(256)
        keyspace_slider.setValue(66)
        slider_value_display = QLabel(keyspaceGroupBox)
        keyspacerange_layout.addWidget(keyspace_slider)
        keyspacerange_layout.addWidget(slider_value_display)
        keyspaceMainLayout.addLayout(keyspacerange_layout)

        # Connect slider value change to update_keyspace_range method
        keyspace_slider.valueChanged.connect(lambda value, k=self.keyspaceLineEdit, s=slider_value_display: self.update_keyspace_range(value, k, s))
        return keyspaceGroupBox

    # Function to update key space range based on slider value
    def update_keyspace_range(self, value, keyspaceLineEdit, slider_value_display):
        if value == 256:
            start_range = hex(2**(value - 1))[2:]
            end_range = "fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141"
            self.keyspaceLineEdit.setText(f"{start_range}:{end_range}")
            slider_value_display.setText(str(value))
        else:
            start_range = hex(2**(value - 1))[2:]
            end_range = hex(2**value - 1)[2:]
            self.keyspaceLineEdit.setText(f"{start_range}:{end_range}")
            slider_value_display.setText(str(value))

    # Function to create the "Stop All" button
    def create_stop_button(self):
        stopButton = QPushButton("Stop ALL", self)
        stopButton.clicked.connect(self.stop_hunt)
        stopButton.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;"> Stop RotaCuda and All Running programs </span>')
        stopButton.setObjectName("stopButton")
        return stopButton

    def create_start_button(self):
        StartButton = QPushButton("Start RotaCuda", self)
        StartButton.setObjectName("startButton")
        StartButton.setToolTip('<span style="font-size: 12pt; font-weight: bold; color: black;"> Start RotaCuda (NOT WORKING) </span>')
        #StartButton.clicked.connect(self.run_gpu_cuda)
        return StartButton

    # Function to create the Output File Configuration GUI
    def create_outputFileGroupBox(self):
        outputFileGroupBox = QGroupBox(self)
        outputFileGroupBox.setTitle("File Configuration")
        outputFileGroupBox.setStyleSheet("QGroupBox { border: 3px solid #E7481F; padding: 5px; }")
        outputFileLayout = QHBoxLayout(outputFileGroupBox)

        self.inputFileLabel = QLabel("Input File:", self)
        outputFileLayout.addWidget(self.inputFileLabel)
        self.inputFileLineEdit = QLineEdit("hash16066_sort.bin", self)
        self.inputFileLineEdit.setPlaceholderText('Click browse to find your BTC hash160 bin ')
        outputFileLayout.addWidget(self.inputFileLineEdit)

        self.inputFileButton = QPushButton("Browse", self)
        self.inputFileButton.setStyleSheet("color: #E7481F;")
        self.inputFileButton.clicked.connect(self.browse_input_file)
        outputFileLayout.addWidget(self.inputFileButton)

        self.save_prog = QCheckBox("💾 Save Progress 💾")
        self.save_prog.setStyleSheet("color: #E7481F;")
        self.save_prog.setChecked(True)
        outputFileLayout.addWidget(self.save_prog)

        self.save_progButton = QPushButton("💾 Check Progress 💾")
        self.save_progButton.clicked.connect(self.check_prog)
        outputFileLayout.addWidget(self.save_progButton)

        self.found_progButton = QPushButton("🔥 Check if Found 🔥")
        self.found_progButton.clicked.connect(self.found_prog)
        outputFileLayout.addWidget(self.found_progButton)

        return outputFileGroupBox

    # Function to create the RotaCuda Configuration GUI
    def create_rotacudaGroupBox(self):
        rotacudaGroupBox = QGroupBox(self)
        rotacudaGroupBox.setTitle("RotaCuda Configuration")
        rotacudaGroupBox.setStyleSheet("QGroupBox { border: 3px solid #E7481F; padding: 5px; }")
        rotacudaLayout = QVBoxLayout(rotacudaGroupBox)

        deviceLayout = QHBoxLayout()

        InfoButton = QPushButton("🔋 Check GPU 🪫", rotacudaGroupBox)
        InfoButton.clicked.connect(self.list_info)
        deviceLayout.addWidget(InfoButton)

        self.threadLabel_n = QLabel("Number of Threads:", self)
        deviceLayout.addWidget(self.threadLabel_n)
        self.threadComboBox_n = QComboBox()
        for i in range(1, self.cpu_count + 1):
            self.threadComboBox_n.addItem(str(i))
        self.threadComboBox_n.setCurrentIndex(2)
        deviceLayout.addWidget(self.threadComboBox_n)

        self.gpuIdLabel = QLabel("CUDA List of GPU(s) to use:", rotacudaGroupBox)
        deviceLayout.addWidget(self.gpuIdLabel)

        self.gpuIdLineEdit = QLineEdit("0", rotacudaGroupBox)
        self.gpuIdLineEdit.setPlaceholderText('0, 1, 2')
        deviceLayout.addWidget(self.gpuIdLineEdit)

        self.gpugridLineEdit = QLineEdit("g0x,g0y", rotacudaGroupBox)
        self.gpugridLineEdit.setPlaceholderText('g0x,g0y,g1x,g1y')
        deviceLayout.addWidget(self.gpugridLineEdit)

        rotacudaLayout.addLayout(deviceLayout)

        # Create a new layout for additional options
        deviceLayout2 = QHBoxLayout()

        # GPU Calculation (Enabled GPU Calculation)
        self.gpuCheckBox = QCheckBox("Enable GPU Calculation:", rotacudaGroupBox)
        self.gpuCheckBox.setStyleSheet("color: #E7481F;")
        deviceLayout2.addWidget(self.gpuCheckBox)

        # Reload Key (Rkey) option
        self.reloadKeyLabel = QLabel("Reload Key (Rkey):", rotacudaGroupBox)
        deviceLayout2.addWidget(self.reloadKeyLabel)
        self.reloadKeyLineEdit = QLineEdit("", rotacudaGroupBox)
        self.reloadKeyLineEdit.setPlaceholderText('1-1000')
        deviceLayout2.addWidget(self.reloadKeyLineEdit)

        # Add deviceLayout2 to the main layout (rotacudaLayout)
        rotacudaLayout.addLayout(deviceLayout2)

        deviceLayout3 = QHBoxLayout()

        # Dropdown for search mode selection
        self.modeLabel = QLabel("Search Mode:", self)
        deviceLayout3.addWidget(self.modeLabel)
        self.modeComboBox = QComboBox()
        self.modeComboBox.addItem("ADDRESS")
        self.modeComboBox.addItem("ADDRESSES")
        self.modeComboBox.addItem("XPOINT")
        self.modeComboBox.addItem("XPOINTS")
        deviceLayout3.addWidget(self.modeComboBox)

        # Dropdown for coin selection
        self.coinLabel = QLabel("Coin:", self)
        deviceLayout3.addWidget(self.coinLabel)
        self.coinComboBox = QComboBox()
        self.coinComboBox.addItem("BTC")
        self.coinComboBox.addItem("ETH")
        deviceLayout3.addWidget(self.coinComboBox)

        # Disable Informers (Display) option
        self.displayCheckBox = QCheckBox("Disable Informers (Display):", rotacudaGroupBox)
        self.displayCheckBox.setStyleSheet("color: #E7481F;")
        deviceLayout3.addWidget(self.displayCheckBox)

        self.checkOption = QCheckBox("Check (Check):", rotacudaGroupBox)
        self.checkOption.setStyleSheet("color: #E7481F;")
        deviceLayout3.addWidget(self.checkOption)

        self.uncompCheckBox = QCheckBox("Uncompressed Points (Uncomp):", rotacudaGroupBox)
        self.uncompCheckBox.setStyleSheet("color: #E7481F;")
        deviceLayout3.addWidget(self.uncompCheckBox)

        self.bothCheckBox = QCheckBox("Both Uncompressed & Compressed (Both):", rotacudaGroupBox)
        self.bothCheckBox.setStyleSheet("color: #E7481F;")
        deviceLayout3.addWidget(self.bothCheckBox)

        rotacudaLayout.addLayout(deviceLayout3)

        return rotacudaGroupBox

    # Function to read and display file contents
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

    # Function to check progress
    def check_prog(self):
        self.read_and_display_file('input/progress.txt', "Progress file found.", "Progress")

    # Function to check if found
    def found_prog(self):
        self.read_and_display_file("found/found.txt", "File found. Check for Winners 😀.", "No Winners Yet 😞")

    # Function to browse for an input file
    def browse_input_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Text Files (*.txt);;Binary Files (*.bin);;All Files (*.*)")
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            file_name = os.path.basename(file_path)
            self.inputFileLineEdit.setText(file_name)

    # Function to list GPU information
    def list_info(self):
        # Specify the base path
        base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "RotaCuda", "Rotor-Cuda.exe")

        command = [base_path, '-l']
        self.consoleWindow.append_output(" ".join(command))
        self.run(command)

    # Function to run a command and display its output
    def run(self, command):
        self.process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
        for line in self.process.stdout:
            output = line.strip()
            self.consoleWindow.append_output(output)
        self.process.stdout.close()


    # Function to run ROTA CUDA
    def run_gpu_cuda(self):
        command = self.construct_command("Rotor-Cuda")
        self.execute_command('"' + '" "'.join(command) + '"')

    # Function to construct the RotaCuda command based on user inputs
    def construct_command(self, mode):
        thread_count_n = int(self.threadComboBox_n.currentText())
        # Specify the base path
        base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "RotaCuda", mode)

        command = [base_path]

        if self.gpuCheckBox.isChecked():
            gpu_ids = self.gpuIdLineEdit.text().strip()
            gpu_grid = self.gpugridLineEdit.text().strip()
            command.extend([f" -g --gpu --gpui {gpu_ids} --gpux {gpu_grid} "])

        thread_count = self.threadComboBox_n.currentText()
        if thread_count:
            command.extend([" -t ", thread_count])

        # Add -m (mode) and --coin options
        search_mode = self.modeComboBox.currentText()
        if search_mode:
            command.extend([" -m ", search_mode])

        coin = self.coinComboBox.currentText()
        if coin:
            command.extend([" --coin ", coin])

        range_keyspace = self.keyspaceLineEdit.text().strip()
        if range_keyspace:
            command.extend([" --range ", range_keyspace])

        reload_key = self.reloadKeyLineEdit.text().strip()
        if reload_key:
            command.extend([" --rkey ", reload_key])

        # Output file
        output_file_relative_path = ["found", "found.txt"]
        output_file_path = os.path.join(*output_file_relative_path)
        command.extend([" -o ", output_file_path])

        # Additional Options
        if self.displayCheckBox.isChecked():
            command.extend([" -d 0 "])
        if self.checkOption.isChecked():
            command.extend([" --check "])
        if self.uncompCheckBox.isChecked():
            command.extend([" --uncomp "])
        if self.bothCheckBox.isChecked():
            command.extend([" --both "])

        in_file = self.inputFileLineEdit.text().strip()
        if in_file:
            input_file_relative_path = ["input", in_file]
            input_file_path = os.path.join(*input_file_relative_path)
            command.extend([" -i ", input_file_path])

        return command


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

    # Function to handle command completion
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

    # Function to stop the BitCrack process
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

    # Function to handle application closure
    def closeEvent(self, event):
        self.stop_hunt()
        event.accept()

def main():
    app = QApplication([])
    window = RotacudaFrame()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
