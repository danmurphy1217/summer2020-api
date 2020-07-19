import requests
import sqlite3

[print(requests.get('http://api.dan-murphy.com:5000/api/v1/summer/books/all/').json()[i].get('title')) for i in range(len(requests.get('http://api.dan-murphy.com:5000/api/v1/summer/books/all/').json()))]
[print(requests.get('http://api.dan-murphy.com:5000/api/v1/summer/textbooks/all/').json()[i].get('title')) for i in range(len(requests.get('http://api.dan-murphy.com:5000/api/v1/summer/textbooks/all/').json()))]
[print(requests.get('http://api.dan-murphy.com:5000/api/v1/summer/work/all/').json()[i].get('company')) for i in range(len(requests.get('http://api.dan-murphy.com:5000/api/v1/summer/work/all/').json()))]


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


conn = sqlite3.connect('summer2020.db')
conn.row_factory = dict_factory
cur = conn.cursor() 

retrieve_title_count = cur.execute("""SELECT count(*) as 'count' FROM textbooks WHERE LOWER(title) == 'hands-on machine learning';""")
count = cur.execute("""SELECT count(*) FROM {};""".format('textbooks')).fetchall()[0].get('count(*)')
title_responses = cur.execute("""SELECT title FROM {} WHERE LOWER(title) == '{}';""".format('textbooks', "hands-on machine learning")).fetchall()
author_responses = cur.execute("""SELECT title, `author(s)` FROM {} WHERE LOWER(`author(s)`) == '{}';""".format("textbooks", "aditya bhargava")).fetchall()
#print(retrieve_title_count.fetchall()[0].get('count'))


[print(val.get('title')) for val in author_responses if val.get('title') == "Hands-on ML V2"]
