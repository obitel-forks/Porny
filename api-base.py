import json
from urllib.request import urlopen

from bs4 import BeautifulSoup
from flask import Flask, request, render_template, jsonify
import pymysql

CONFIG_FILE = json.loads(open("config.json").read())
db = pymysql.connect(CONFIG_FILE["server"], CONFIG_FILE["username"], CONFIG_FILE["password"], CONFIG_FILE["db"])

app = Flask(__name__)
base_url = "https://www.pornhub.com"
urls = list()

@app.route('/api/comment/<data>', methods=['GET'])
def fetch_comment(data):
    try:
        id = int(data)
        cursor = db.cursor()
        cursor.execute("SELECT commentID, commentText, commentSource FROM comments WHERE commentID = %s LIMIT 1", id)
        result = cursor.fetchone()
        number_of_rows = cursor.rowcount
        if number_of_rows > 0:
            # Need to add other outputs, and status codes
            return jsonify(id=result[0],comment=result[1],source=result[2])
        else:
            return jsonify(error="database error")
    except ValueError:
            return jsonify(error="input error, please enter a valid id")

@app.route('/api/random/', methods=['GET'])
def fetch_random():
    cursor = db.cursor()
    cursor.execute("SELECT commentID, commentText, commentSource FROM comments ORDER BY RAND() LIMIT 1",)
    result = cursor.fetchone()
    number_of_rows = cursor.rowcount
    if number_of_rows > 0:
        # Need to add other outputs, and status codes
        return jsonify(id=result[0], comment=result[1], source=result[2])
    else:
        return jsonify("error")

@app.route('/api/search/<search>', methods=['GET'])
def fetch_search(search):
    comment_list = []
    cursor = db.cursor()
    cursor.execute("SELECT commentID, commentText, commentSource FROM comments WHERE commentText LIKE '%{}%'".format(search),)
    results = cursor.fetchall()
    for result in results:
        comment_list.append({'id':result[0],'comment':result[1],'source':result[2]})
    return jsonify(comments=comment_list)




if __name__ == "__main__":
    app.run(host='0.0.0.0')
