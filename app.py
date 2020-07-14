import flask
from flask import request, jsonify
import sqlite3

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.errorhandler(404)
def page_not_found(error):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@app.route('/', methods=['GET'])
def home():
    return "<h1>Dan Murphy Summer 2020</h1><p>This site is a prototype API for accessing the things I've done during the summer of 2020.</p>"

@app.route("/api/v1/summer/all/", methods=['GET'])
def get_all():
    conn = sqlite3.connect("summer2020.db")
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
def get_book_ids(all):
    conn = sqlite3.connect("summer2020.db")
    cur = conn.cursor()
    if request.args.get('id'):
        max_id = [val[0] for val in cur.execute('''SELECT count(*) FROM books''').fetchall()]
        selected_id = int(request.args.get('id'))

        # check for out of range ID
        if (selected_id >= max_id[0]) | (selected_id < 0) :
            return "ID is out of range. Try an ID between 0 and {}".format(max_id[0] - 1)

    elif all == "all":
        # return all books
        return jsonify(
            cur.execute('''SELECT * FROM books''').fetchall()
            )
    # otherwise filter by the provided ID
    return jsonify(
        cur.execute('''SELECT * FROM books WHERE id == {}'''.format(request.args.get('id'))).fetchall()
        )


# TEXTBOOKS
@app.route('/api/v1/summer/textbooks/', methods=['GET'], defaults={'all' : None})
@app.route('/api/v1/summer/textbooks/<all>/', methods=['GET'])
def get_textbook_ids(all):
    conn = sqlite3.connect("summer2020.db")
    cur = conn.cursor()
    if request.args.get('id'):
        max_id = [val[0] for val in cur.execute('''SELECT count(*) FROM textbooks''').fetchall()]
        selected_id = int(request.args.get('id'))

        # check for out of range ID
        if (selected_id > max_id[0]) | (selected_id < 0) :
            return "ID is out of range. Try an ID between 1 and {}".format(max_id[0])

    elif all == "all":
        # return all textbooks
        return jsonify(
            cur.execute('''SELECT * FROM textbooks''').fetchall()
            )
    
    # otherwise filter by the provided ID
    return jsonify(
        cur.execute('''SELECT * FROM textbooks WHERE id == {}'''.format(request.args.get('id'))).fetchall()
        )


# WORK
@app.route("/api/v1/summer/work/", methods=['GET'], defaults = {'all' : None})
@app.route("/api/v1/summer/work/<all>/", methods=['GET'])
def get_work_co(all):
    conn = sqlite3.connect("summer2020.db")
    cur = conn.cursor()
    if request.args.get('company'):        
        company_list = [company[0] for company in cur.execute('''SELECT company FROM work''')]
        selected_company = str(request.args.get('company'))
        
        # check for non-existent company
        if (selected_company not in company_list) :
            return "Dan did not work for '{}' in the summer of 2020. Please try one of these companys: {}.".format(selected_company,", ".join(company_list))
    elif all == "all":
        # return all companies
        return jsonify(
            cur.execute('''SELECT * FROM work''').fetchall()
            )
    
    # otherwise, filter by the provided company
    return jsonify(
        cur.execute('''SELECT * FROM work WHERE company == "{}"'''.format(request.args.get('company'))).fetchall()
        )

# SIDE PROJECTS
"""
To Do
"""

if __name__ == "__main__":
    app.run()

