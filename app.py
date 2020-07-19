import flask
from flask import request, jsonify, make_response, render_template, redirect
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
@app.route('/<name>', methods=['GET'])
def homepage(name = "Dan Murphy"):
    return render_template('welcome.html', name = name)

@app.route('/', methods=['POST', 'GET'])
def login():
    conn = sqlite3.connect("summer2020.db")
    conn.row_factory = dict_factory
    cur = conn.cursor()


    book = request.form['book_title']
    textbook = request.form['textbook_title']
    work = request.form['work_title']

    if work and not (textbook or book):
        results = cur.execute("""SELECT * FROM work WHERE `company` == '{}'""".format(work)).fetchall()
        return jsonify(results)
    if textbook and not (work or book):
        results = cur.execute("""SELECT * FROM textbooks WHERE `title` == '{}'""".format(textbook)).fetchall()
        return jsonify(results)
    if book and not (textbook or work):
        results = cur.execute("""SELECT * FROM books WHERE `title` == '{}'""".format(book)).fetchall()
        return jsonify(results)
    else:
        return make_response(jsonify({'error': 'invalid input'}), 405)
    

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
def bookAndTextbookGetRequest(all, table):
    conn = sqlite3.connect('summer2020.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    if all == "all":
        return jsonify(
            cur.execute(
                "SELECT * FROM {};".format(table)
            ).fetchall()
        )

    query_parameters = request.args
    user_id = query_parameters.get('id')
    title = query_parameters.get('title')
    author = query_parameters.get('author')

    query = "SELECT * FROM {} WHERE".format(table)
    to_filter = []

    if user_id:
        # id info
        max_id = cur.execute('''SELECT count(*) FROM {}'''.format(table)).fetchall()[0].get('count(*)')
        selected_id = int(request.args.get('id'))
        if table == 'books':
            # use id info to check for out of range ID
            if (selected_id >= max_id) | (selected_id < 0) :
                return "ID is out of range. Try an ID between 0 and {}".format(max_id - 1)
            
            # otherwise, add id to the query and filter
            query += ' id=? AND'
            to_filter.append(
                user_id
            )
        else:
            # use id info to check for out of range ID
            if (selected_id > max_id) | (selected_id <= 0) :
                return "ID is out of range. Try an ID between 1 and {}".format(max_id)
            
            # otherwise, add id to the query and filter
            query += ' id=? AND'
            to_filter.append(
                user_id
            )
    if title:
        # list of titles
        title_list = [book.get('title') for book in cur.execute('''SELECT title FROM {}'''.format(table))]
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

        author_list = [book.get('author(s)') for book in cur.execute('''SELECT `author(s)` FROM {}'''.format(table))]
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

def bookAndTextbookPostRequest(table):
    conn = sqlite3.connect('summer2020.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    req = request.args.to_dict()
    if len(req.keys()) < 2:
        return make_response(jsonify({'error': 'Incorrect arguments. Please include title and author arguments.'}), 400)
    elif list(req.keys())[0] == 'title' and list(req.keys())[1] == 'author':
        author = req.get('author')
        title = req.get('title')
        id_num = int(cur.execute(f"SELECT `id` FROM {table} WHERE `id` = (SELECT MAX(`id`)  FROM {table});").fetchall()[0].get('id'))+1

        duplicate_titles = "SELECT title FROM {} WHERE lower(title) == '{}';".format(table, title.lower())
        if (len(cur.execute(duplicate_titles).fetchall())) != 0:
            return make_response(jsonify({'error': 'Duplicate entry. Specify a different title'}), 400)

        query = "INSERT INTO {}(`id`, `title`, `author(s)`) VALUES (?, ?, ?)".format(table)
        cur.execute(query, [id_num, title, author])
        conn.commit()
        return f"Your POST request was successful. Title: {title}, and Author: {author} were inserted into the {table} table."
    else:
        return make_response(jsonify({'error': 'Incorrect arguments. Please specify the title and author of the book.'}), 400)

def bookAndTextbookDeleteRequest(table):
    conn = sqlite3.connect('summer2020.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    query_parameters = request.args
    user_id = query_parameters.get('id')
    title = query_parameters.get('title')
    author = query_parameters.get('author')

    query = "DELETE FROM {} WHERE".format(table)
    to_filter = []

    if user_id:
        # id info
        max_id = cur.execute('''SELECT count(*) FROM {}'''.format(table)).fetchall()[0].get('count(*)')
        selected_id = int(request.args.get('id'))
        if table == 'books':
            # use id info to check for out of range ID
            if (selected_id >= max_id) | (selected_id < 0) :
                return "ID is out of range. Try an ID between 0 and {}".format(max_id - 1)
            
            # otherwise, add id to the query and filter
            query += ' id=? AND'
            to_filter.append(
                user_id
            )
        else: # if  table == textbooks
            # use id info to check for out of range ID
            if (selected_id > max_id) | (selected_id <= 0) :
                return "ID is out of range. Try an ID between 1 and {}".format(max_id)
            
            # otherwise, add id to the query and filter
            query += ' id=? AND'
            to_filter.append(
                user_id
            )
    if title:
        # list of titles
        title_list = [book.get('title') for book in cur.execute('''SELECT title FROM {}'''.format(table))]
        selected_title = str(request.args.get('title'))

        # check if selected title is in the title list
        if selected_title not in title_list:
            return "<h3>I did not read that book (<em>yet!</em>).</h3> Try to delete one of these books: <br /> {}".format(
                "<br/><br/>".join(title_list)
            )
        
        # otherwise, add the specified title
        query += ' title=? AND'
        to_filter.append(
            title
        )

    if author:

        author_list = [book.get('author(s)') for book in cur.execute('''SELECT `author(s)` FROM {}'''.format(table))]
        selected_author = str(request.args.get('author'))


        if selected_author not in author_list:
            return "<h3>I haven't read a book by that author (<em>yet!</em>).</h3> Try to delete one of these authors: <br /> {}".format(
                "<br/><br/>".join(set(author_list))
            )

        query += ' `author(s)`=? AND'
        to_filter.append(
            author
        )
    if not (user_id or title or author):
        return make_response(jsonify({'error':'Please specify an ID, Title, or Author parameter'}), 404)

    query = query[:-4] + ';'

    results = cur.execute(query, to_filter).fetchall()
    conn.commit()

    return make_response(jsonify({'Success': '{} was deleted from the database.'.format(list(query_parameters.to_dict().values())[0])}))

def bookAndTextbookPutRequest(table):
    conn = sqlite3.connect('summer2020.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    query_parameters = request.args
    title = query_parameters.get('title')
    author = query_parameters.get('author')
    
    title_responses = cur.execute("""SELECT title FROM {} WHERE LOWER(title) == '{}';""".format(table, title.lower())).fetchall()
    author_responses = cur.execute("""SELECT `author(s)` FROM {} WHERE LOWER(`author(s)`) == '{}';""".format(table, author.lower())).fetchall()

    if len(title_responses) == 0:
        id_num = int(cur.execute(f"SELECT `id` FROM {table} WHERE `id` = (SELECT MAX(`id`)  FROM {table});").fetchall()[0].get('id'))+1
        query = "INSERT INTO {}(`id`, `title`, `author(s)`) VALUES (?, ?, ?)".format(table)
        cur.execute(query, [id_num, title, author])
        conn.commit()
        return f"Your PUT request was successful. Title: {title}, and Author: {author} were inserted into the {table} table."
    elif title_responses != 0:
        id_query = cur.execute("""SELECT id from {} WHERE LOWER(title) = '{}'""".format(table, title.lower())).fetchall()[0].get('id')
        update_value = cur.execute("""UPDATE {} SET `title` = '{}', `author(s)` = '{}' WHERE `id` == {};""".format(
                table, title, author, int(id_query)
            ))
        conn.commit()
        return make_response(jsonify({'success': 'The data was correctly updated'}))
    else:
        return make_response(jsonify({
            'error':'check the documentation and ensure your requests are of the specified format.'
        }))



    # if title and author:
    #     retrieve_title_count = cur.execute("""SELECT count(*) FROM {} WHERE LOWER(title) == '{}';""".format(table, title.lower()))
    #     retrieve_author_count = cur.execute("""SELECT count(*) FROM {} WHERE LOWER(`authors(s)`) == '{}';""".format(table, author.lower()))
    #     if (retrieve_title_count and retrieve_author_count) == 1:
    #         if retrieve_author_count == author:
    #             return make_response(jsonify({'error': 'No changes were made to the specified resource'}), 405)

    #         current_id = cur.execute("""SELECT id FROM {} WHERE LOWER(title) == '{}';""".format(table, title.lower()))
    #         update_value = cur.execute("""UPDATE {} SET id = '{}', title = '{}', `author(s)` = '{}' WHERE LOWER(title) == '{}';""".format(
    #             table, int(current_id.fetchone().get('id')), title, author, title.lower()
    #         ))
    #         conn.commit()
    #         return make_response(jsonify({'success': 'The data was correctly updated'}))
    #     elif (len(retrieve_title_count) or len(retrieve_author_count)) == 0:
    #         return bookAndTextbookPostRequest(table)
    #     elif (len(retrieve_author_count) and len(retrieve_title_count)) > 1:
    #         pass
    #     else:
    #         return make_response(jsonify({'error' : 'Please format your PUT request as api/v1/{}?title=<>?author=<>'.format(table)}), 400)
    # else:
    #         return make_response(jsonify({'error' : 'Please format your PUT request as api/v1/{}?title=<>?author=<>'.format(table)}), 400)




@app.route("/api/v1/summer/books/", methods=['GET'], defaults={'all' : None})
@app.route("/api/v1/summer/books/<all>/", methods=['GET'])
def get_book(all):
    return bookAndTextbookGetRequest(all, 'books')

@app.route('/api/v1/books/', methods=['GET', 'POST', 'DELETE', 'PUT'])
def crud_book():
    if request.method == 'POST':
        return bookAndTextbookPostRequest('books')
    elif request.method == 'DELETE':
        return bookAndTextbookDeleteRequest('books')
    elif request.method == 'GET':
        return make_response(jsonify({'error':'GET method not supported for this endpoint. Try /api/v1/summer/books/all.'}), 405)
    elif request.method == 'PUT':
        return bookAndTextbookPutRequest('books')

# TEXTBOOKS
@app.route('/api/v1/summer/textbooks/', methods=['GET'], defaults={'all' : None})
@app.route('/api/v1/summer/textbooks/<all>/', methods=['GET'])
def get_textbook(all):
       return bookAndTextbookGetRequest(all, 'textbooks')

@app.route('/api/v1/textbooks/', methods=['GET', 'POST', 'DELETE', 'PUT'])
def crud_textbook():
    if request.method == 'POST':
        return bookAndTextbookPostRequest('textbooks')
    elif request.method == 'DELETE':
        return bookAndTextbookDeleteRequest('textbooks')
    elif request.method == 'GET':
        return make_response(jsonify({'error':'GET method not supported for this endpoint. Try /api/v1/summer/textbooks/all to retrieve all data.'}), 405) 
    elif request.method == 'PUT':
        return bookAndTextbookPutRequest('textbooks')

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


if __name__ == "__main__":
    app.run()
