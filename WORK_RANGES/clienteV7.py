import os
import sys
import requests
import subprocess
import re
import platform
from datetime import datetime
import time
import pycuda.driver as cuda
import pycuda.autoinit
import hashlib
import argparse
import configparser
import random
import pkgutil
import datetime

print(".########.##........##........######....#####...##....##\n.##.......##....##..##.......##....##..##...##..###...##\n.##.......##....##..##.......##.......##.....##.####..##\n.######...##....##..##.......##.......##.....##.##.##.##\n.##.......#########.##.......##.......##.....##.##..####\n.##.............##..##.......##....##..##...##..##...###\n.##.............##..########..######....#####...##....##")
print("Donate: 1FALCoN194bPQELKGxz2vdZyrPRoSVxGmR" )
print("Version: 7.0 Multi GPU" )
print("Statistics: http://f4lc0n.com:8080/" )

server_url = "http://f4lc0n.com:8080/"
start_time = time.time()

client_version = "7.6"

def generate_initial_request():
    hash_algorithm = hashlib.sha256()

    app_path = sys.argv[0]
    
    with open(app_path, "rb") as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            hash_algorithm.update(data)
    
    initial_request = hash_algorithm.hexdigest()
    return initial_request

initial_request = generate_initial_request()

def request_ranks_f4lc0n():
    initial_request = generate_initial_request()
    nickname = get_nickname()
    response = requests.post(f"{server_url}/request_ranks_f4lc0n", data={"initial_request": initial_request})
    if response.status_code == 200:
        result = response.json()
        if 'error' in result:
            print("registration request fails code: f4lc0n")
        else:
            print("requesting ranges to the server")
    else:
        print("Failed to verify ranges request")
        print("Código de estado HTTP:", response.status_code)
        print("Respuesta del servidor:", response.text)

def send_code_to_server():
    initial_request = generate_initial_request()
    nickname = get_nickname()
    response = requests.post(f"{server_url}/receive_code", data={"initial_request": initial_request, "nickname": nickname})
    if response.status_code == 200:
        result = response.json()
        if 'error' in result:
            print("Error al enviar el código al servidor.")
            print("Respuesta del servidor:", response.text)
        else:
            print("ranges F4LC0N request sent successfully.")
    else:
        print("Failed to send code to the server.")
        print("Código de estado HTTP:", response.status_code)
        print("Respuesta del servidor:", response.text)


def handle_error(exception):
    print("An error occurred:", exception)

def reconnect():
    while True:
        try:
            print("Reconnecting to the server...")
            time.sleep(5)
            break
        except Exception as e:
            handle_error(e)

def show_waiting_message():
    print("Waiting for the server...")

print()
print("Recommended for 16GB of RAM: -b 104 -t 512 -p 2016")
print("Recommended for 8GB of RAM: -b 104 -t 512 -p 1024")
print("Recommended for 4GB of RAM: -b 52 -t 256 -p 256")
print("But you can configure the values recommended for your graphics card")
print()

parser = argparse.ArgumentParser(description='Cliente para realizar cálculos.')

parser.add_argument('-b', type=int, help='Valor para -b')
parser.add_argument('-t', type=int, help='Valor para -t')
parser.add_argument('-p', type=int, help='Valor para -p')

args = parser.parse_args()

config = configparser.ConfigParser()

if os.path.exists("valores.txt"):
    config.read("valores.txt")
    valor_b = config.getint("Valores", "valor_b")
    valor_t = config.getint("Valores", "valor_t")
    valor_p = config.getint("Valores", "valor_p")
else:

    valor_b = 104
    valor_t = 256
    valor_p = 1024

if args.b is not None:
    valor_b = args.b
if args.t is not None:
    valor_t = args.t
if args.p is not None:
    valor_p = args.p

config["Valores"] = {
    "valor_b": str(valor_b),
    "valor_t": str(valor_t),
    "valor_p": str(valor_p)
}
with open("valores.txt", "w") as configfile:
    config.write(configfile)

def get_nickname():
    if not os.path.exists("nickname.txt"):
        with open("nickname.txt", "w") as f:
            nickname = input("(Do not use symbols, emojis or spaces) Enter your nickname: ")
            f.write(nickname)
    else:
        with open("nickname.txt", "r") as f:
            nickname = f.read().strip()

    return nickname

def get_payment_info():
    if os.path.exists("addresspay.txt") and os.path.exists("tokenuser.txt"):
        with open("addresspay.txt", "r") as f_address, open("tokenuser.txt", "r") as f_token:
            address = f_address.read().strip()
            token = f_token.read().strip()
    else:
        address = input("Enter your Bitcoin payment address: ")
        token = input("Enter your secret password or type a new one if you don't have: ")
        with open("addresspay.txt", "w") as f_address, open("tokenuser.txt", "w") as f_token:
            f_address.write(address)
            f_token.write(token)

    return address, token

def update_payment_info(nickname, address, token, device_name):
    if not os.path.exists("tokenuser.txt"):
        password = get_password()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        with open("tokenuser.txt", "w") as f_token:
            f_token.write(token)

        try:
            response = requests.post(
                f"{server_url}/update_payment_info",
                data={"nickname": nickname, "address": address, "token": token, "device_name": device_name, "password": hashed_password}
            )
            if response.status_code == 200:
                print("Payment information updated successfully.")
            else:
                print("Error updating payment information.")
                print("HTTP status code:", response.status_code)
                print("Server response:", response.text)
        except requests.exceptions.ConnectionError:
            print("Failed to establish a connection to the server. Retrying in 5 seconds...")
            time.sleep(5)
            update_payment_info(nickname, address, token, device_name)
    else:
        with open("tokenuser.txt", "r") as f_token:
            saved_token = f_token.read().strip()
        if saved_token != token:
            print("Error: The token provided does not match the one stored.")
            print("Make sure you enter the correct token.")
        else:
            try:
                response = requests.post(
                    f"{server_url}/update_payment_info",
                    data={"nickname": nickname, "address": address, "token": token, "device_name": device_name}
                )
                if response.status_code == 200:
                    print("Payment information updated successfully.")
                else:
                    print("Error updating payment information.")
                    print("HTTP status code:", response.status_code)
                    print("Server response:", response.text)
            except requests.exceptions.ConnectionError:
                print("Failed to establish a connection to the server. Retrying in 5 seconds...")
                time.sleep(5)
                update_payment_info(nickname, address, token, device_name)
                

def get_password():
    password = input("Enter your password: ")
    confirm_password = input("Confirm your password: ")
    while password != confirm_password:
        print("Passwords do not match. Try again.")
        password = input("Enter your password:")
        confirm_password = input("Confirm your password: ")
    return password

def get_bitcrack_exe():
    try:
        output = subprocess.check_output(["nvidia-smi"])
        if "NVIDIA" in output.decode() or "RTX" in output.decode() or "GTX" in output.decode() or "Quadro" in output.decode():
            return "nvidia.exe"
    except:
        pass

    return "amd.exe"

def detect_device():
    devices = []
    try:
        output = subprocess.check_output(["nvidia-smi"])
        if "NVIDIA" in output.decode() or "RTX" in output.decode() or "GTX" in output.decode() or "Quadro" in output.decode():
            num_devices = cuda.Device.count()

            for device_id in range(num_devices):
                device_name = cuda.Device(device_id).name().strip()
                devices.append(f"NVIDIA ({device_name}) ID {device_id}")

    except:
        pass
    
    try:
        output = subprocess.check_output(["clinfo"])
        if "AMD" in output.decode():

            device_id = 0
            for line in output.decode().split('\n'):
                if 'Device Name:' in line:
                    device_name = line.split('Device Name:')[1].strip()
                    devices.append(f"AMD ({device_name}) ID {device_id}")
                    device_id += 1
    except:
        pass

    return devices

def select_devices(devices):
    devices_selected = []
    print("detected devices")
    for i, device in enumerate(devices):
        print(f"{i}: {device}")

    print("to use another card run again at the same time")
    print("Enter the IDs of the devices you want to use, separated by spaces.")
    device_ids_str = input("For example: 0 or 1 or 2 - just select one optionwrite the ID:\n")
    device_ids = device_ids_str.split()

    for device_id_str in device_ids:
        try:
            device_id = int(device_id_str)
            if device_id >= 0 and device_id < len(devices):
                devices_selected.append(devices[device_id])
            else:
                print(f"Error: invalid ID. It must be between 0 and {len(devices) - 1}")
        except ValueError:
            print("You must enter a whole number")

    # Guardar los dispositivos seleccionados en selected_devices.txt
    with open("selected_devices.txt", "w") as f:
        for device in devices_selected:
            f.write(device + "\n")

    return devices_selected


def execute_cubitcrack(ranges, address, device, device_number, range_type, f4lc0n_rangues_1=None):
    bitcrack_exe = get_bitcrack_exe()
    output = ''
    if not device:
        raise ValueError("No device selected")

    if "NVIDIA" not in device:
        raise ValueError("AMD option is not available. Only NVIDIA is supported.")

    cuda_executable = os.path.join(os.getcwd(), "nvidia.exe")
    if not os.path.exists(cuda_executable):
        raise FileNotFoundError("File 'nvidia' not found in current location.")

    #f4lc0n_rangues_1 = "f4lc0n_rangues_1"

    for r in ranges:
        range_start_time = time.time()
        range_completion_time = None  

        command = f"{cuda_executable} -d {device_number} -c -b {valor_b} -t {valor_t} -p {valor_p} --keyspace {r} {address}"

        start_time = False
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True, shell=True) as process:
            validadorrango1 = None
            validadorrango2 = None
            range_complete = False

            for line in iter(process.stdout.readline, ''):
                line = line.rstrip()
                if "Public key:" in line:
                    start_time = True  
                    continue
                if start_time:
                    start_time = False  
                    continue
                if "Compressed" in line or "Address" in line:
                    continue
    
                if "Private key:" not in line:
                    print(f"Range: {r} | {line}")
                if "Public key:" in line:
                    validadorrango1 = line.replace("Public key:", "").strip()
                elif "Private key:" in line:
                    validadorrango2 = line.replace("Private key:", "").strip()
                elif "Reached end of keyspace" in line:
                    range_completion_time = datetime.datetime.now()
                    range_completion_time_str = range_completion_time.strftime("%Y-%m-%d %H:%M:%S")
                    range_completion_timestamp = time.time()

                    if (range_completion_timestamp - range_start_time) >= 10: 
                        range_complete = True
                    else:
                        print(f"Range {r} not notified to server due to lack of time.")
                

                output += line
                output += line
    
            process.stdout.close()
            process.wait()
    
            if range_complete:
                print(f"\nFULLY COMPLETED RANGE:{r}\n")
                if validadorrango1 is not None:
                    output += f"{r}\n{validadorrango1}\n"
                if validadorrango2 is not None:
                    output += f"{r}\n{validadorrango2}\n"
                
                with open("scanned_ranges.txt", "a") as f:
                    f.write(f"{r} - {range_completion_time_str}\n")
    
                report_task_completion(r, nickname, output, f4lc0n_rangues_1=f4lc0n_rangues_1)

    return output

def report_task_completion(completed_range, nickname, output, range_generator_f4lc0n=False, f4lc0n_rangues_1=None):
    validadorrango2_file_name = f"{nickname}_validadorrango2.txt"
    if os.path.exists(validadorrango2_file_name):
        with open(validadorrango2_file_name, "r") as validadorrango2_file:
            validadorrango2 = validadorrango2_file.read().strip()
    else:
        validadorrango2 = None

    if range_generator_f4lc0n:
        initial_request = "rangue_f4lc0n"
    else:
        initial_request = generate_initial_request()

    data = {"ranges[]": [completed_range], "nickname": nickname, "initial_request": initial_request, "f4lc0n_rangues_1": f4lc0n_rangues_1}

    response = requests.post(f"{server_url}/task_completed", data=data)

    if response.status_code == 200:
        print(f"\nRange {completed_range} completed and reported to server. Unique ID: {f4lc0n_rangues_1}")
    else:
        print(f"\nError reporting range {completed_range} completed to the server.")
        print("HTTP status code:", response.status_code)
        print("Server response:", response.text)

    if validadorrango2 is not None:
        response = requests.post(f"{server_url}/validate_range_1", data={"validadorrango2": validadorrango2, "nickname": nickname})
        if response.status_code == 200:
            print("")
        else:
            print("")

def get_range_type():
    range_type_file = "range_type.txt"
    if os.path.exists(range_type_file):
        with open(range_type_file, "r") as f:
            range_type = f.read().strip()
    else:
        range_type_option = input("Select the type of range you want:\n1. Ranges starting with 0x2\n2. Ranges starting with 0x3\n3. Random 0x2 and 0x3 ranges\n4. Custom option\nEnter the option number:")

        if range_type_option == "1":
            range_type = "0x2"
        elif range_type_option == "2":
            range_type = "0x3"
        elif range_type_option == "3":
            range_type = "aleatorio"
        elif range_type_option == "4":
            custom_option = input("Enter the one custom option (e.g., 0x20, 0x21, ... 0x31 , 0x3f): ")
            if custom_option.startswith("0x") and len(custom_option) == 4 and custom_option[2:].isalnum() and int(custom_option, 16) >= 0x20 and int(custom_option, 16) <= 0x3f:
                range_type = custom_option
            else:
                print("Invalid custom option. Random ranges will be used.")
                range_type = "aleatorio"
        else:
            print("Invalid option. Random ranges will be used.")
            range_type = "aleatorio"
        
        with open(range_type_file, "w") as f:
            f.write(range_type)
    
    return range_type


if __name__ == '__main__':
    devices = detect_device()
    nickname = get_nickname()

    if os.path.exists("selected_devices.txt"):
        with open("selected_devices.txt", "r") as f:
            devices_selected = [line.strip() for line in f.readlines()]
    else:
        devices_selected = select_devices(devices)
        with open("selected_devices.txt", "w") as f:
            for device in devices_selected:
                f.write(device + "\n")

    print("Selected devices")
    for device in devices_selected:
        print(device)

    if os.path.exists("nickname.txt"):
        with open("nickname.txt", "r") as f:
            saved_nickname = f.read().strip()
        print()
        print("Welcome back, " + saved_nickname + "!")

    if os.path.exists("addresspay.txt"):
        with open("addresspay.txt", "r") as f:
            saved_address = f.read().strip()
        print(saved_nickname + ", this is your payment address: " + saved_address)
        print()

    range_type = get_range_type()
    address, token = get_payment_info()
    device_name = devices_selected[0]
    update_payment_info(nickname, address, token, device_name)

    print(f"Selected values: -b {valor_b} -t {valor_t} -p {valor_p}")

    initial_request = generate_initial_request()
    request_ranks_f4lc0n()
    send_code_to_server()

    while True:
        try:
            show_waiting_message()
    
            response = requests.post(f"{server_url}/get_range", data={"nickname": nickname, "device": device, "version": client_version, "range_type": range_type, "initial_request": initial_request})
            if response.status_code == 200:
                data = response.json()
                ranges = data["ranges"]
                f4lc0n_rangues_1 = data.get("f4lc0n_rangues_1") 

                device_number = int(device.split()[-1])
                output = execute_cubitcrack(ranges, "13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so", device, device_number, range_type, f4lc0n_rangues_1=f4lc0n_rangues_1)
    
                validadorrango2_regex = re.compile(r"Private key:\s+([0-9a-fA-F]+)")
                match = validadorrango2_regex.search(output)
                if match:
                    validadorrango2 = match.group(1)
                    print(f"")

                    response = requests.post(f"{server_url}/validate_range_1", data={"validadorrango2": validadorrango2, "nickname": nickname})
                    if response.status_code == 200:
                        print("")
                    else:
                        print("")

                validadorrango1_regex = re.compile(r"Public key:\s+([0-9a-fA-F]+)")
                match = validadorrango1_regex.search(output)
                if match:
                    validadorrango1 = match.group(1)
                    response = requests.post(f"{server_url}/validate_range_2", data={"validadorrango1": validadorrango1, "nickname": nickname})
                    if response.status_code == 200:
                        print("")
                    else:
                        print("")
            else:
                print("Error in communication with the server. Check if the server is running.")
        
        except Exception as e:
            handle_error(e)
            reconnect()
            show_waiting_message()

    

