import subprocess
import signal
import platform
import os
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import requests
app = Flask(__name__)

def price():
    url = 'https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=GBP,USD,EUR'
    page = requests.get(url)
    data = page.json()
    return f'Bitcoin Price per BTC {data}'


@app.route('/')
def start_page():
    return render_template("index.html", price=price())


@app.route("/list_gpu", methods=["GET"])
def list_gpu():
    command = construct_command("cudaInfo")
    output = execute_command(command)
    return jsonify(output=output)

@app.route("/start_opencl", methods=["GET"])
def start_opencl():
    command = construct_command("clBitcrack")
    return execute_command(command)

@app.route("/start_cuda", methods=["GET"])
def start_cuda():
    command = construct_command("cuBitcrack")
    return execute_command(command)

@app.route("/stop_hunt", methods=["GET"])
def stop_hunt():
    return stop_command()

def run(command):
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,
        )
        output = []
        for line in process.stdout:
            output.append(line.strip())
        process.stdout.close()
        return "\n".join(output)
    except Exception as e:
        return str(e)

def construct_command(mode):
    # Replace with your logic to construct the command
    # You can access form data using request.args.get() or request.form.get()
    # Example: gpu_ids = request.args.get("gpu_ids")
    gpu_ids = "your_gpu_ids_here"
    gpu_blocks = "your_gpu_blocks_here"
    gpu_points = "your_gpu_points_here"
    thread_count_n = "your_thread_count_here"
    # ... (construct the command based on form data)

    command = f"{mode} -d {gpu_ids} -b {gpu_blocks} -p {gpu_points} -t {thread_count_n}"
    # ... (add more command options based on form data)
    return command

def execute_command(command):
    if platform.system() == "Windows":
        subprocess.Popen(command, shell=True)
    else:
        os.system(command)
    return "Command executed."

def stop_command():
    if platform.system() == "Windows":
        subprocess.Popen(["taskkill", "/F", "/T", "/PID", str(os.getpid())])
    else:
        os.killpg(os.getpgid(os.getpid()), signal.SIGTERM)
    return "Hunt stopped."

if __name__ == "__main__":
    app.run(debug=True)

if __name__ == '__main__':
    app.run(use_reloader=True, debug=True, host='0.0.0.0', port=80)