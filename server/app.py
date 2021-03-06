import uuid

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse

import elastic
import json
import sys
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app)
          
def get_plot(time, keywords):
    for (key, value) in keywords.items():
        plt.plot(time, value, label=key)
    size = len(time)
    print("a")
    sizes = [0, int(size/4), int(size/2), int(size*3/4), int(size-1)]
    print("b")
    ticks = [time[sizes[0]], time[sizes[1]], time[sizes[2]], time[sizes[3]], time[sizes[4]]]
    plt.xticks(ticks, [a.split("-")[0] for a in ticks])
    plt.legend(loc='upper left')
    fig = plt.figure()
    return fig

def show_plot(time, keywords):
    get_plot(time, keywords)
    plt.show()

def get_keyword_hist(titles):
    time = []
    keywords = {}
    for key in titles:
        keywords[key] = []

    for aggr in elastic.get_hist(titles):
        if aggr['doc_count'] == 0:
            continue
        time.append(aggr['key_as_string'])
        for (key, value) in aggr['5']['buckets'].items():
            keywords[key].append(value['doc_count'])    

    # plot(time, keywords)
    return {"time": time, "keywords": keywords}

def get_table_data(keywords, start, end):
    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')
    mod_data = []
    for doc in elastic.get_table(keywords, start_str, end_str)['hits']:
        mod = doc['_source']
        mod_data.append(mod)
    return {'data': mod_data}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/table', methods=['POST'])
def table():
    try:

        req_data = json.loads(request.data)
        keywords = req_data["keywords"]
        start = datetime.strptime(req_data['start'], "%Y-%m-%d")
        end = start + relativedelta(months=1)

        return jsonify(get_table_data(keywords, start, end))

    except Exception as e:          
        return e    

@app.route('/hist', methods=['POST'])
def post():
    try:
        keywords = json.loads(request.data)['query']
        data = get_keyword_hist(keywords)
        print(data)

        time = data['time']
        keywords = data['keywords']

        return jsonify(data)
    except Exception as e:          
        return e

if __name__ == '__main__':
    app.run('0.0.0.0')