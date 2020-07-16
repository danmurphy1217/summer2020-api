import flask
from flask import request, jsonify
import sqlite3
import os
import requests 

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.errorhandler(404)
def page_not_found(error):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route('/', methods=['GET'])
def home():
    return "<h1>Dan Murphy Summer 2020</h1><p>This site is a prototype API for accessing the things I've done during the summer of 2020.</p>"

@app.route("/api/v1/summer/all/", methods=['GET'])
def get_all():
    conn = sqlite3.connect("summer2020.db")
    conn.row_factory = dict_factory
    cur = conn.cursor()
    # retrieve data from each table
    return jsonify(
                   cur.execute('''SELECT * FROM books''').fetchall(),
                   cur.execute('''SELECT * FROM textbooks''').fetchall(),
                   cur.execute('''SELECT * FROM work''').fetchall()
                  )

# BOOKS
@app.route("/api/v1/summer/books/", methods=['GET'], defaults={'all' : None})
@app.route("/api/v1/summer/books/<all>/", methods=['GET'])
def get_book(all):

    conn = sqlite3.connect('summer2020.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    if all == "all":
        return jsonify(
            cur.execute(
                "SELECT * FROM books;"
            ).fetchall()
        )

    query_parameters = request.args
    user_id = query_parameters.get('id')
    title = query_parameters.get('title')
    author = query_parameters.get('author')

    query = "SELECT * FROM books WHERE"
    to_filter = []

    if user_id:
        # id info
        max_id = cur.execute('''SELECT count(*) FROM books''').fetchall()[0].get('count(*)')
        selected_id = int(request.args.get('id'))

        # use id info to check for out of range ID
        if (selected_id >= max_id) | (selected_id < 0) :
            return "ID is out of range. Try an ID between 0 and {}".format(max_id - 1)
        
        # otherwise, add id to the query and filter
        query += ' id=? AND'
        to_filter.append(
            user_id
        )
    if title:
        # list of titles
        title_list = [book.get('title') for book in cur.execute('''SELECT title FROM books''')]
        selected_title = str(request.args.get('title'))

        # check if selected title is in the title list
        if selected_title not in title_list:
            return "<h3>I did not read that book (<em>yet!</em>).</h3> Thank you for the recommendation! In the meantime, try one of these books: <br /> {}".format(
                "<br/><br/>".join(title_list)
            )
        
        # otherwise, return the specified title
        query += ' title=? AND'
        to_filter.append(
            title
        )

    if author:

        author_list = [book.get('author(s)') for book in cur.execute('''SELECT `author(s)` FROM books''')]
        selected_author = str(request.args.get('author'))


        if selected_author not in author_list:
            return "<h3>I haven't read a book by that author (<em>yet!</em>).</h3> Thank you for the recommendation! In the meantime, try one of these authors: <br /> {}".format(
                "<br/><br/>".join(author_list)
            )

        query += ' `author(s)`=? AND'
        to_filter.append(
            author
        )
    if not (user_id or title or author):
        return page_not_found(404)

    query = query[:-4] + ';'

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)

@app.route('/api/v1/books/', methods=['GET', 'POST'])
def add_book():
    conn = sqlite3.connect('summer2020.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    req = request.args.to_dict()


    if list(req.keys())[0] == 'title' and list(req.keys())[1] == 'author':
        author = req.get('author')
        title = req.get('title')
        user_id = int(cur.execute('SELECT `id` FROM books WHERE `id` = (SELECT MAX(`id`)  FROM books);').fetchall()[0].get('id'))+1

        duplicate_titles = "SELECT title FROM books WHERE lower(title) == '{}';".format(title.lower())
        if (len(cur.execute(duplicate_titles).fetchall())) != 0:
            return "Duplicate entry. Try a different book title!"
        query = "INSERT INTO books(`id`, `title`, `author(s)`) VALUES (?, ?, ?)"
        cur.execute(query, [user_id, title, author])
        conn.commit()
        return f"Your POST request was successful. Title: {title}, and Author: {author} were inserted into the table."

    return "<h3>Please include these three arguments in this order in your post request: <br/> <h3 style = 'background-color:lightgray; width: 200'> title, and author.</h3></h3>"




# TEXTBOOKS
@app.route('/api/v1/summer/textbooks/', methods=['GET'], defaults={'all' : None})
@app.route('/api/v1/summer/textbooks/<all>/', methods=['GET'])
def get_textbook(all):
    conn = sqlite3.connect('summer2020.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    if all == "all":
        return jsonify(
            cur.execute(
                "SELECT * FROM textbooks;"
            ).fetchall()
        )

    query_parameters = request.args
    user_id = query_parameters.get('id')
    title = query_parameters.get('title')
    author = query_parameters.get('author')

    query = "SELECT * FROM textbooks WHERE"
    to_filter = []

    if user_id:
        # id info
        max_id = cur.execute('''SELECT count(*) FROM textbooks''').fetchall()[0].get('count(*)')
        selected_id = int(request.args.get('id'))

        # use id info to check for out of range ID
        if (selected_id > max_id) | (selected_id < 0) :
            return "ID is out of range. Try an ID between 0 and {}".format(max_id - 1)
        
        # otherwise, add id to the query and filter
        query += ' id=? AND'
        to_filter.append(
            user_id
        )
    if title:
        # list of titles
        title_list = [textbook.get('title') for textbook in cur.execute('''SELECT title FROM textbooks''')]
        selected_title = str(request.args.get('title'))

        # check if selected title is in the title list
        if selected_title not in title_list:
            return "<h3>I did not read that textbook (<em>yet!</em>).</h3> Thank you for the recommendation! In the meantime, try one of these books: <br /> {}".format(
                "<br/><br/>".join(title_list)
            )
        
        # otherwise, return the specified title
        query += ' title=? AND'
        to_filter.append(
            title
        )

    if author:

        author_list = [textbook.get('author(s)') for textbook in cur.execute('''SELECT `author(s)` FROM textbooks''')]
        selected_author = str(request.args.get('author'))


        if selected_author not in author_list:
            return "<h3>I haven't read a book by that author (<em>yet!</em>).</h3> Thank you for the recommendation! In the meantime, try one of these authors: <br/> {}".format(
                
                "<br/><br/>".join(author_list)
            )

        query += ' `author(s)`=? AND'
        to_filter.append(
            author
        )
    if not (user_id or title or author):
        return page_not_found(404)

    query = query[:-4] + ';'

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)


# WORK
@app.route("/api/v1/summer/work/", methods=['GET'], defaults = {'all' : None})
@app.route("/api/v1/summer/work/<all>/", methods=['GET'])
def get_work(all):
    conn = sqlite3.connect('summer2020.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    if all == "all":
        return jsonify(
            cur.execute(
                "SELECT * FROM work;"
            ).fetchall()
        )
    
    query_parameters = request.args
    company = query_parameters.get('company')
    description = query_parameters.get('description')
    location = query_parameters.get('location')

    query = "SELECT * FROM work WHERE"
    to_filter = []

    if company:
        # company info
        company_list = [company.get('company') for company in cur.execute('''SELECT `company` FROM work''')]
        selected_company = str(request.args.get('company'))

        # use id info to check for out of range ID
        if selected_company not in company_list :
            return "ID is out of range. TO DO" 
        
        # otherwise, add id to the query and filter
        query += ' company=? AND'
        to_filter.append(
            company
        )
    


    if location:

        location_list = [book.get('location') for book in cur.execute('''SELECT `location` FROM work''')]
        selected_location = str(request.args.get('location'))


        if selected_location not in location_list:
            return "<h3>I haven't worked with a company located in {}.</h3> Try one of these:<br/> {}".format(
                selected_location, "<br/><br/>".join(list(set(location_list)))
            )

        query += ' `location`=? AND'
        to_filter.append(
            location
        )
    if not (company or location):
        return page_not_found(404)

    query = query[:-4] + ';'

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)


# SIDE PROJECTS
"""
To Do
"""

if __name__ == "__main__":
    app.run()

