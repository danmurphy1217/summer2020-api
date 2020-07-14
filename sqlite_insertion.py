import sqlite3 
import pandas as pd 
import numpy as np
from data import books, textbooks, jobs, side_projects
import json

# establish connection
connection = sqlite3.connect('summer2020.db')
cursor = connection.cursor()

def create_tables():
    cursor.execute(
        "CREATE TABLE books (`id` integer primary key, title text, `author(s)` text)"
    )
    cursor.execute(
        "CREATE TABLE textbooks (`id` integer primary key, title text, `author(s)` text)"
    )
    cursor.execute(
        "CREATE TABLE work (company text, `description` text, `location` text)"
    )
    return "Tables Created."

# insert data
def insert_data(data_for_books, data_for_textbooks, data_for_jobs):
    cursor.executemany(
        "INSERT INTO books VALUES (?, ?, ?)", data_for_books
    )
    connection.commit()
    
    cursor.executemany(
        "INSERT INTO textbooks VALUES (?, ?, ?)", data_for_textbooks 
    )
    connection.commit()

    cursor.executemany(
        "INSERT INTO work VALUES (?, ?, ?)", data_for_jobs
    )
    connection.commit()

    return "Data added."

def insert_row(data_for_books, data_for_textbooks, data_for_jobs):
    pass

# DATA 
books_data = [(books[book]['id'], books[book]['title'], books[book]['author(s)']) for book in range(len(books))]
textbooks_data = [(textbooks[textbook]['id'], textbooks[textbook]['title'], textbooks[textbook]['author(s)']) for textbook in range(len(textbooks))] 
jobs_data = [(jobs[job]['company'], jobs[job]['description'], jobs[job]['location']) for job in range(len(jobs))]

if __name__ == "__main__":
    # create_tables()    
    # print(insert_data(books_data, textbooks_data, jobs_data))

    # for row in cursor.execute(
    #     '''SELECT * FROM books'''
    # ):
    #     print(row)
    # print("\n")
    # for row in cursor.execute(
    #     '''SELECT * FROM textbooks'''
    # ):
    #     print(row)
    # print("\n")
    # for row in cursor.execute(
    #     '''SELECT * FROM work'''
    # ):
    #     print(row)  
    print([row[0] for row in cursor.execute('''SELECT company FROM work''')])

