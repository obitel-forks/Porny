#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Pornhub Search + Scrape
# return video URLs from a search string
# RAWR xD
# TODO discard comments with urls or non english


import requests
from bs4 import BeautifulSoup
import sys
import time
import pymysql
import json


base_url = "https://www.pornhub.com"
urls = list()
limit = 20
CONFIG_FILE = json.loads(open("config.json").read())
db = pymysql.connect(CONFIG_FILE["server"], CONFIG_FILE["username"], CONFIG_FILE["password"], CONFIG_FILE["db"])


def pornhub_search():
    random_url = 'https://www.pornhub.com/random'
    resp = requests.get(random_url)
    soup = BeautifulSoup(resp.text, 'lxml')
    time.sleep(10)
    try:

        if len(soup.select("div.phimage")) > 0:
            for l in soup.select("div.phimage"):
                title = l.find('span', {'class': 'title'})
                url = l.find('a')['href']
                scrape_comments(url)
        else:
            print("failure in loading list of videos")
    except Exception as e:
        print(e)


def scrape_comments(url):
    total = 0
    resp = requests.get(base_url + url)
    soup = BeautifulSoup(resp.text, 'lxml')
    cursor = db.cursor()
    try:
        for comment in soup.select("div.commentMessage"):
            if total < limit:
                s = comment.find('span').string
                if s == "[[commentMessage]]" or s.isdigit():
                    print("Error: Invalid Comment skipping due to comment being a digit: " + resp.url)
                else:
                    print(str(s))
                    sql_insert = "INSERT INTO `comments` (`commentID`, `queryID`, `commentText`, `commentSource`) VALUES (NULL, NULL, %s, %s)"
                    cursor.execute(sql_insert, (str(s), resp.url))
                    db.commit()
                    total += 1
            else:
                pornhub_search()
                print("##### NEW SEARCH #####")
    except Exception as e:
        print(e)

if len(sys.argv) == 1:
    pornhub_search()
   #pornhub_search(input('Genre to Search: '))
else:
    pornhub_search(sys.argv[1])
