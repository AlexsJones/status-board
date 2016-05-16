import json
import requests
import subprocess
from time import time

from flask import Flask
from flask import render_template

app = Flask(__name__)
with open('config.json') as f:
    config = json.loads(f.read())


def shell_handler(command, **kwargs):
    return_code = subprocess.call(command, shell=True)
    return json.dumps(return_code == 0)


def http_handler(address, **kwargs):
    s = time()
    try:
        r = requests.get(address)
    except requests.exceptions.RequestException:
        t = format((time() - s) * 1000, ".1f")
        return json.dumps(False), t
    t = format((time() - s) * 1000, ".1f")
    return json.dumps(r.status_code == 200), t


get_handler = {
    'http': http_handler,
    'shell': shell_handler,
}


@app.route('/')
def index():
    data = {
        'tasks': config['tasks'],
        'title': config['title'],
    }
    return render_template('index.html', **data)


@app.route('/<task_id>')
def status(task_id):
    try:
        task = next(task for task in config['tasks'] if task['id'] == task_id)
    except StopIteration:
        return 'This task does not exist', 404
    j, t = get_handler[task['type']](**task)
    return json.dumps({"status": j, "time": "%sms" % str(t)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
