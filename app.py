#!/usr/bin/env python
import dataset
from flask import Flask
from flask import render_template
from flask import make_response
from flask import request
from flask import redirect
from flask import session
from flask import url_for
import os
import urllib.request
import datetime
import pymysql.cursors



app = Flask(__name__, static_folder='static', static_url_path='')
use_debugger=True

con = pymysql.connect(
    host='localhost',
    user='wpuser',
    password='mypassword',
    db='wpdb',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
#print ("connect successful!!")

def check_sql(region):
    cur = con.cursor()
    query = "select districtID from counter_cost;"
    cur.execute(query)
    rows = cur.fetchall()
    #with open('test.txt', 'w') as f:
    #    print(rows, file=f)

    regions = [i["districtID"] for i in rows]
    if region not in regions:
        error = True
        message="Forbidden construct detected: '"+region+"'"
        return error, message
    return False, ''

def get_districtDescription():
    curr = con.cursor()
    query = 'select districtDescription,districtID from counter_cost;'
    rowss = ''
    try:
        curr.execute(query)
        rowss = curr.fetchall()
        message=""
        return (rowss, message)
    except:
        message="Sorry, unexpected server error"
        return (rowss, message)

@app.route('/')
def index():
    districtdescription_id, message = get_districtDescription()
    return render_template('index.html', districtdescription=districtdescription_id, message=message)



@app.route('/check_price', methods=['GET', 'POST'])
def check_price():
    region = request.form['region_name']
    if region =="":
        error = 'True'
        message="An empty argument was sent"
        return render_template('index.html', error=error, message=message)
    error, message = check_sql(region)
    if error:
        return render_template('index.html', error=error, message=message)
    cur = con.cursor()
    query = 'select counter_price from counter_cost where districtID LIKE \'' + region + '\';'
    try:
        cur.execute(query)
        rows = cur.fetchall()
 
        districtdescription_id, message = get_districtDescription()
        return render_template('index.html', counter_price=rows, region=region, districtdescription=districtdescription_id, message=message)
    except:
        error = 'True'
        message="Sorry, unexpected server error"
        return render_template('index.html', error=error, message=message)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081, threaded=True)

