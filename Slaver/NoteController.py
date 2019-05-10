import sys, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append('../')

import multiprocessing
import time
from Slaver.run.run import run
import redis

server = redis.StrictRedis(host='127.0.0.1', port=6379)

def start_note():
    run()

def get_status():
    status = server.get('note_controller:status')

    return bytes.decode(status, encoding='utf-8')

if __name__ == '__main__':
    pid = None
    while True:
        status = get_status()
        if not pid and status == 'runing':
            print('ok')
            p = multiprocessing.Process(target=start_note)
            p.start()
            pid = p.pid
            print(p.pid)

        elif pid and status == 'stop':
            os.system('taskkill -f -pid ' + str(pid))
            pid = None

        time.sleep(1)

    # os.system('python ' + file_path)
