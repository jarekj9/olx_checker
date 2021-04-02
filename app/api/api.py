from flask import Flask
from flask import request
import threading
import random
import time
import sys

sys.path.append('/opt/app/flask-react/app/api')
from olxjj import OLXJJ

app = Flask(__name__, static_folder='../build', static_url_path='/') # so can server static from react folder
olx_threads = {}



class OlxThread(threading.Thread):
    def __init__(self, url, ignore_list):
        self.progress = 0
        self._return = None
        self.olx = OLXJJ(url)
        self.ignore_list = ignore_list
        super().__init__()

    def run(self):
        self._return =  self.olx.get_all_prices(self.ignore_list)

    def join(self):
        threading.Thread.join(self)
        return self._return


@app.route('/api/time')
def get_current_time():
    return {'time': f'{int(time.time())}'}

@app.route('/api/olxresult/', methods = ['POST'])
def olx():
    global olx_threads
    thread_id = request.json.get('id')
    olxjj_result_dict = olx_threads[thread_id].join()
    olx_threads.pop(thread_id, None)
    return olxjj_result_dict

@app.route('/api/olx_get_id/', methods = ['POST'])
def olx_id():
    global olx_threads
    url = request.json.get('url')
    ignore_list = request.json.get('ignore_list').split()
    thread_id = random.randint(1, 100)
    while(olx_threads.get(thread_id)):
        thread_id = random.randint(1, 100)
    olx_threads[thread_id] = OlxThread(url, ignore_list)
    olx_threads[thread_id].start()
    return {'id': thread_id}

@app.route('/api/progress/<int:thread_id>', methods = ['GET'])
def progress(thread_id):
    global olx_threads
    if not thread_id:
        return {'progress': 0}
    olx_thread_obj = olx_threads.get(thread_id)
    progress = str(olx_thread_obj.olx.percent_progress) if olx_thread_obj else '100'  # 100 if thread was already removed
    return {'progress': progress}


@app.route('/')
def index():
    return app.send_static_file('index.html') # served rrom react
