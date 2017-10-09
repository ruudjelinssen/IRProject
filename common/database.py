#!/usr/bin/env python

import sqlite3
from sqlite3 import Error

from common import author, paper


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
        return DataBase.rows_to_papers(selection)

    def get_all_papers(self):
        c = self.conn.cursor()
        c.execute(
            """
            SELECT id, year, title, event_type, pdf_name, abstract, paper_text
            FROM papers
            ORDER BY id
            """
        )
        selection = c.fetchall()
        return DataBase.rows_to_papers(selection)

    def get_all_authors(self):
        c = self.conn.cursor()
        c.execute(
            """
            SELECT id, name FROM authors ORDER BY id ASC
            """
        )
        selection = c.fetchall()
        return self.rows_to_authors(selection)

    @staticmethod
    def rows_to_papers(rows):

        dictionary = {}

        for row in rows:

            paper_id = row[0]
            if paper_id not in dictionary:

                if len(row) > 7:
                    paper_inst = paper.Paper(row[0:7], row[7:9])
                else:
                    paper_inst = paper.Paper(row[0:7], None)
                dictionary[paper_id] = paper_inst
            else:
                if len(row) > 7:
                    dictionary[paper_id].add_author([row[7],row[8]])

        return dictionary

    def rows_to_authors(self, rows):

        dictionary = {}

        for row in rows:
            _id = row[0]
            name = row[1]
            if _id not in dictionary:
                dictionary[_id] = author.Author(_id, name)

        return dictionary
