#!/usr/bin/env python

import sqlite3
from sqlite3 import Error
from .paper import Paper


class DataBase:
    """Define the workings of document retrieval from the database"""

    conn = None

    def __init__(self, db_file):
        try:
            self.conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)

    def get_all(self):

        c = self.conn.cursor()
        c.execute(
            """
            SELECT p.id, p.year, p.title, p.event_type, p.pdf_name, p.abstract, p.paper_text, a.id, a.name
            FROM authors AS a, papers AS p, paper_authors AS pa
            WHERE p.id = pa.paper_id AND pa.author_id = a.id
            ORDER BY p.id ASC
            """)
        selection = c.fetchall()
        return self.rows_to_papers(selection)

    def rows_to_papers(self, rows):

        dictionary = {}

        for row in rows:

            paper_id = row[0]
            if paper_id not in dictionary:

                paper = Paper(row[0:7], row[7:9])
                dictionary[paper_id] = paper
            else:
                dictionary[paper_id].add = row[8]

        return dictionary
