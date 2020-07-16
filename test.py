import sqlite3
id = '11'
title="Mamas Last Hug"
author="Bradley Hope"

conn = sqlite3.connect('summer2020.db')
cur = conn.cursor()


check_for_duplicates = "SELECT id FROM books WHERE id == '{}';".format(int(id))

print(cur.execute(check_for_duplicates).fetchall())
