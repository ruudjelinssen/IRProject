#!/usr/bin/env python

import csv


class ReadCSV:
    """
    This class takes the contents of the data set CSV files and outputs them as a python dictionary
    which can then be used as input for e.g. an Indexer.
    """

    @staticmethod
    def get_authors():
        """Get the authors of the NIPS data set"""

        authors = {}

        with open('../dataset/authors.csv', 'r') as csv_file:
            author_reader = csv.reader(csv_file, delimiter=',', quotechar='|')
            skip_head = True

            for row in author_reader:
                if skip_head is True:
                    skip_head = False
                    continue

                authors[row[0]] = row[1]
                print(', '.join(row))

        return authors
