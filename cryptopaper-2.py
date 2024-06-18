#!/usr/bin/env python3
## (c) 2024 Kerry Fraser-Robinson
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import requests
import os, sys, time, string, re
from werkzeug.utils import secure_filename    

from bs4 import BeautifulSoup                   # For BBC News scraping proxy
import socket                                   # For confirming ip address
import base64                                   # For parsing image uploads

PORT = 5000
DEFAULT_LOCATION = 'Toronto'
location = DEFAULT_LOCATION

TITLE, VERSION = 'Cryptopaper', '2.0.1'
LIBDIR = 'lib/'
T_START = int(time.time())
OPTIONS_FILE = 'options.txt'
KEYWORDS_FILE = 'watch-words.txt'

app = Flask(__name__, template_folder=LIBDIR)
CORS(app)                                       # Enable CORS for all routes

def read_location():
    global location
    try:
        with open(os.path.join(LIBDIR, OPTIONS_FILE), 'r') as file:
            location = file.read().lstrip().rstrip()
            print_log(f"Using location: `{location}`")
    except:
        location = DEFAULT_LOCATION
        print_log(f"Using DEFAULT location (`{location}`)")

def print_log(log_string = '',log_to_file=True, noStdOut = False):
    LOG_FILENAME = sys.argv[0].split('.')[0] + '.log'

    timestamp = time.strftime("%m/%d/%y  %H:%M:%S", time.localtime(time.time()))
    if not noStdOut: print(f"[ {timestamp} ] {log_string}")

    if(log_to_file):
        with open(LOG_FILENAME, "a") as file:
            file.write(f"[ {timestamp} ] {log_string}\n")   

def ip_address():
    try:
        ip = ((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(
            ("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["(No IP)"])[0])
    except:
        ip = "(IP Timeout)"
    return ip

    LOG_FILENAME = sys.argv[0].split('.')[0] + '.log'

    timestamp = time.strftime("%d/%b/%Y %H:%M:%S", time.localtime(time.time()))
    newLogLine = f"localhost - - [{timestamp}] {log_string}"

    if not noStdOut: print(newLogLine)

    if(log_to_file):
        with open(LOG_FILENAME, "a") as file:
            file.write(f"{newLogLine}\n")   

def sanitize_watch_words(watch_words: str):
    lines = watch_words.split('\n')
    # Remove non-alphanumeric characters and empty lines
    sanitized_lines = [re.sub(r'\W+', '', line) for line in lines if line.strip() != '']
    return '\n'.join(sorted(sanitized_lines, key=str.lower))

def sanitize_location(location: str):
    return ''.join(ch for ch in location if ch.isprintable())    

@app.route('/', methods=['GET', 'POST'])
def index():
    global location
    if request.method == 'POST' and 'location' in request.form:
        location = sanitize_location(request.form['location'])
        try:
            with open(os.path.join(LIBDIR, OPTIONS_FILE), 'w') as file:
                file.write(location)        
            print_log(f'{OPTIONS_FILE} (location) updated.')
        except:
            print_log('Location not updated.')
    return send_from_directory(LIBDIR, 'index.html')

@app.route('/words', methods=['GET'])
def words():
    watchWords = []
    # Load watch words. Ignore any words containing non-printable characters  
    try: 
        watchWords = [line.strip() for line in open(os.path.join(LIBDIR, KEYWORDS_FILE)) if all(char in string.printable for char in line)]
        print_log("Watch list loaded: '" + ", ".join(watchWords) + "'")
    except:
        # Defaults :
        watchWords = ['breaking', 'shot', 'troop', 'explo', 'nuclear', 'chemical', 'Ukraine', 'killed', 'Putin', 'Moscow'] 

    return jsonify(watchWords)

@app.route('/status', methods=['GET'])
def status():
    statusData = {
        'title': TITLE,
        'version': VERSION,
        'start_time': T_START,
        'ip_addr': ip_address(),
        'location': location
    }
    return jsonify(statusData)

@app.route('/save', methods=['POST'])
def save_canvas():
    img_data = request.form['imgBase64']
    img_data = img_data.replace('data:image/png;base64,', '')
    img_data = base64.b64decode(img_data)

    file_path = os.path.join(LIBDIR, 'canvas_image.png')
    with open(file_path, 'wb') as f:
        f.write(img_data)
    
    return jsonify({'status': 'success', 'file_path': file_path})

@app.route('/options')
def options():
    system_name = os.uname().nodename
    server_time = time.strftime("%m/%d/%y  %H:%M:%S", time.localtime(time.time()))
    return render_template('options.html', status = f'{system_name} :: {server_time}')

@app.route('/save_watch_words', methods=['POST'])
def save_watch_words():
    text = sanitize_watch_words(request.form['text'])
    try:
        with open(os.path.join(LIBDIR, KEYWORDS_FILE), 'w') as file:
            file.write(text)
        return {'message': 'File saved successfully.'}
    except: return {'error': 'An error occurred while saving the watch-words file.'}

@app.route('/<filename>.png')
def serve_png(filename):
    try:
        secure_filename_str = secure_filename(f"{filename}.png")
        return send_from_directory(LIBDIR, secure_filename_str)
    except FileNotFoundError:
        return "File not found", 404

@app.route('/<filename>.js')
def serve_js(filename):
    try:
        secure_filename_str = secure_filename(f"{filename}.js")
        return send_from_directory(LIBDIR, secure_filename_str)
    except FileNotFoundError:
        return "File not found", 404

@app.route('/<filename>.otf')
def serve_font(filename):
    try:
        secure_filename_str = secure_filename(f"{filename}.otf")
        return send_from_directory(LIBDIR, secure_filename_str)
    except FileNotFoundError:
        return "File not found", 404

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(LIBDIR, 'favicon.ico', mimetype='image/x-icon')

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

if __name__ == '__main__':
    print_log(f"v{VERSION}: Initialising...")
    read_location()
    app.run(debug=True, host='0.0.0.0', port=PORT, ssl_context='adhoc')
