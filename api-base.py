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


@app.route('/fun/<string:search_string>', methods=['GET'])
def pornhub_search(search_string):
    try:
        page = urlopen('https://www.pornhub.com/video/search?search=' + search_string).read()
    except Exception as e:
        page = e.partial
        return jsonify("fail")
    soup = BeautifulSoup(page, "lxml")
    try:
        if len(soup.select("div.phimage")) > 0:
            for l in soup.select("div.phimage"):
                title = l.find('span', {'class': 'title'})
                url = l.find('a')['href']
                comments_page = urlopen(base_url + url).read()
                soup = BeautifulSoup(comments_page, "lxml")
                try:
                    if len(soup.select("div.commentMessage")) > 0:
                        for s in soup.select("div.commentMessage")[0].stripped_strings:
                            if s == "[[commentMessage]]":
                                return("Error: Invalid Comment skipping due to no text: " + url)
                            else:
                                if s.isdigit() == True:
                                    return("Error: Invalid Comment skipping due to comment being a digit: " + url)
                                else:
                                    return (s)
                except Exception as e:
                    return(e)
                return("failure")
    except Exception as e:
        return(e)

@app.route('/api/comment/<data>', methods=['GET'])
def fetch_comment(data):
    try:
        id = int(data)
        cursor = db.cursor()
        cursor.execute("SELECT commentID, commentText FROM comments WHERE commentID = %s LIMIT 1", (id))
        result = cursor.fetchone()
        number_of_rows = cursor.rowcount
        if number_of_rows > 0:
            # Need to add other outputs, and status codes
            return jsonify(id=result[0],comment=result[1])
        else:
            return jsonify(error="database error")
    except ValueError:
            return jsonify(error="input error, please enter a valid id")

@app.route('/api/random/', methods=['GET'])
def fetch_random():
    cursor = db.cursor()
    cursor.execute("SELECT commentID, commentText FROM comments ORDER BY RAND() LIMIT 1",)
    result = cursor.fetchone()
    number_of_rows = cursor.rowcount
    if number_of_rows > 0:
        # Need to add other outputs, and status codes
        return jsonify(id=result[0],comment=result[1])
    else:
        return jsonify("error")


if __name__ == "__main__":
    app.run(host='0.0.0.0')
