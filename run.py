import json
import subprocess
from time import time
import pygal
import requests
from flask import Flask
from flask import render_template

with open('config.json') as f:
    config = json.loads(f.read())

class MyServer(Flask):
    def __init__(self, *args, **kwargs):
        super(MyServer,self).__init__(*args, **kwargs)
        self.stored_data = {}

        for task in config['tasks']:
            self.stored_data[task["id"]]=[]

app = MyServer(__name__)

def shell_handler(command, **kwargs):
    return_code = subprocess.call(command, shell=True)
    return json.dumps(return_code == 0),0

def http_handler(address, **kwargs):
    s = time()
    try:
        r = requests.get(address, timeout=3.000)
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

    title = "response times"
    chart = pygal.Line(stroke=True,
            width=600,height=300,explicit_size=True,title=title)

    for key, value in app.stored_data.iteritems():
        chart.add(key,[float(i) for i in value])


    box_chart = pygal.Box(box_mode="pstdev",width=600,height=300,explicit_size=True)
    box_chart.title = 'response time range'

    for key, value in app.stored_data.iteritems():
        box_chart.add(key,[float(i) for i in value])

    return render_template('index.html', tasks=config['tasks'],
            title=config['title'],bar_chart=chart,box_chart=box_chart)


@app.route('/<task_id>')
def status(task_id):
    try:
        task = next(task for task in config['tasks'] if task['id'] == task_id)
    except StopIteration:
        return 'This task does not exist', 404

    print("Next task to process is %s of type %s" % (task['id'],task['type']))

    j,t = get_handler[task['type']](**task)

    if float(t) < float(3000):
        app.stored_data[task['id']].append(t)
    else:
        print("Omitting %s response time too high for graphing %s" % (task['id'],t))
    return json.dumps({"status": j, "time": "%sms" % str(t)})

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', threaded=True)
