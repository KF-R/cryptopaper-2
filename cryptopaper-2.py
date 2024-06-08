from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS  # Import CORS
import json, requests
import time
import os, sys
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
import socket
import base64

import threading # For downloading war DB in background


TITLE = 'Cryptopaper'
VERSION = '2.0.0'
LIBDIR = 'lib/'
T_START = int(time.time())
warData = []

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def updateWarStats():
    global warData
    with open(os.path.join(LIBDIR,'war-db.json'), 'r') as file:
        json_data = json.load(file)

    # military_personnel_values = [day["militaryPersonnel"] for day in json_data["days"]]
    # military_personnel_list = [
    #     military_personnel_values[i] - military_personnel_values[i - 1]
    #     for i in range(1, len(military_personnel_values))
    # ]    

    military_personnel_list = [day["militaryPersonnel"] for day in json_data["days"]]

    print_log(military_personnel_list)
    warData = remove_lower_than_preceding(military_personnel_list)

def remove_lower_than_preceding(numbers):
    if not numbers:
        return []

    max_so_far = numbers[0]
    result = [max_so_far]

    for num in numbers[1:]:
        if num >= max_so_far:
            result.append(num)
            max_so_far = num

    return result    

def download_db():
    url = 'https://raw.githubusercontent.com/andriilive/russia-casualties-ukraine-war-parser/main/db.json'
    local_filename = 'war-db.json'
    response = requests.get(url)
    with open(os.path.join(LIBDIR, local_filename), 'wb') as f:
        f.write(response.content)
    print_log(f"Downloaded {local_filename}")
    updateWarStats()

def schedule_download(interval, func):
    while True:
        func()
        time.sleep(interval)    

@app.route('/wardata', methods=['GET'])
def wardata():
    if len(warData) < 1: updateWarStats()
    return jsonify(warData)

@app.route('/status', methods=['GET'])
def status():
    statusData = {
        'title': TITLE,
        'version': VERSION,
        'start_time': T_START,
        'ip_addr': ip_address(),
        'location': 'Ottawa'
    }
    return jsonify(statusData)


@app.route('/fetch_news', methods=['GET'])
def fetch_bbc_news():
    url = "https://www.bbc.com/news/world"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.text

        soup = BeautifulSoup(data, 'html.parser')
        headlines = soup.find('body').find_all('h2')

        results = []
        for headline in headlines:
            if headline.text.strip() not in results:
                results.append(headline.text.strip())
            if len(results) >= 4:
                break

        return jsonify(results)
    except requests.RequestException as e:
        return jsonify(['', '', 'No headlines found']), 500

@app.route('/')
def index():
    return send_from_directory(LIBDIR, 'index.html')

@app.route('/<filename>.png')
def serve_png(filename):
    try:
        secure_filename_str = secure_filename(f"{filename}.png")
        return send_from_directory(LIBDIR, secure_filename_str)
    except FileNotFoundError:
        # Log an error message or return a custom 404 error
        return "File not found", 404

@app.route('/save', methods=['POST'])
def save_canvas():
    img_data = request.form['imgBase64']
    img_data = img_data.replace('data:image/png;base64,', '')
    img_data = base64.b64decode(img_data)

    file_path = os.path.join(LIBDIR, 'canvas_image.png')
    with open(file_path, 'wb') as f:
        f.write(img_data)
    
    return jsonify({'status': 'success', 'file_path': file_path})

@app.route('/<filename>.js')
def serve_js(filename):
    try:
        secure_filename_str = secure_filename(f"{filename}.js")
        return send_from_directory(LIBDIR, secure_filename_str)
    except FileNotFoundError:
        # Log an error message or return a custom 404 error
        return "File not found", 404

@app.route('/<filename>.otf')
def serve_font(filename):
    try:
        secure_filename_str = secure_filename(f"{filename}.otf")
        return send_from_directory(LIBDIR, secure_filename_str)
    except FileNotFoundError:
        # Log an error message or return a custom 404 error
        return "File not found", 404

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(LIBDIR, 'favicon.ico', mimetype='image/x-icon')

def ip_address():
    try:
        ip = ((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(
            ("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["(No IP)"])[0])
    except:
        ip = "(IP Timeout)"
    return ip

def print_log(log_string = '',log_to_file=True, noStdOut = True):
    LOG_FILENAME = sys.argv[0].split('.')[0] + '.log'

    timestamp = time.strftime("%m/%d/%y  %H:%M:%S", time.localtime(time.time()))
    if not noStdOut: print(f"[ {timestamp} ] {log_string}")

    if(log_to_file):
        with open(LOG_FILENAME, "a") as file:
            file.write(f"[ {timestamp} ] {log_string}\n")   

if __name__ == '__main__':
    print_log(f"v{VERSION}: Initialising...")

    # Start the scheduler in a separate thread
    interval = 24 * 60 * 60  # 24 hours in seconds
    download_thread = threading.Thread(target=schedule_download, args=(interval, download_db))
    download_thread.daemon = True
    download_thread.start()

    app.run(debug=True, host='0.0.0.0', ssl_context='adhoc')
