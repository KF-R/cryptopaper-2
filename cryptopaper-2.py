from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS  # Import CORS
import json, requests
import os, sys, time, string
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
import socket
import base64

# import tkinter as tk
# from PIL import Image, ImageTk
# from threading import Thread

PORT = 5000
LOCATION = 'Toronto'

TITLE = 'Cryptopaper'
VERSION = '2.0.0'
LIBDIR = 'lib/'
T_START = int(time.time())
warData = []

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/words', methods=['GET'])
def words():
    watchWords = []
    # Load watch words. Ignore any words containing non-printable characters  
    try: 
        watchWords = [line.strip() for line in open(os.path.join(LIBDIR, 'watch-words.txt')) if all(char in string.printable for char in line)]
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
        'location': LOCATION
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

    LOG_FILENAME = sys.argv[0].split('.')[0] + '.log'

    timestamp = time.strftime("%d/%b/%Y %H:%M:%S", time.localtime(time.time()))
    newLogLine = f"localhost - - [{timestamp}] {log_string}"

    if not noStdOut: print(newLogLine)

    if(log_to_file):
        with open(LOG_FILENAME, "a") as file:
            file.write(f"{newLogLine}\n")   

class ImageDisplay:
    def __init__(self, root):
        self.root = root
        self.root.title(TITLE)
        self.root.attributes("-fullscreen", True)
        self.root.geometry("+0+0")
        self.root.overrideredirect(True)
        self.label = tk.Label(root)
        self.label.pack()
        self.update_image()

    def update_image(self):
        try:
            image = Image.open('lib/canvas_image.png')
            photo = ImageTk.PhotoImage(image)
            self.label.config(image=photo)
            self.label.image = photo
        except Exception as e:
            print(f"Error loading image: {e}")
        self.root.after(1000, self.update_image)  # Update every second

def start_image_display():
    root = tk.Tk()
    display = ImageDisplay(root)
    root.mainloop()

def print_log(log_string = '',log_to_file=True, noStdOut = True):
    LOG_FILENAME = sys.argv[0].split('.')[0] + '.log'

    timestamp = time.strftime("%m/%d/%y  %H:%M:%S", time.localtime(time.time()))
    if not noStdOut: print(f"[ {timestamp} ] {log_string}")

    if(log_to_file):
        with open(LOG_FILENAME, "a") as file:
            file.write(f"[ {timestamp} ] {log_string}\n")   

if __name__ == '__main__':
    print_log(f"v{VERSION}: Initialising...")

    # display_thread = Thread(target=start_image_display, daemon=True)
    # display_thread.start()
    app.run(debug=True, host='0.0.0.0', port=PORT, ssl_context='adhoc')
