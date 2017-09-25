#!/usr/bin/env python
from datetime import datetime, time

from flask import Flask
from flask_restful import Resource, Api

FLASK_PORT = 5003

app = Flask(__name__)
api = Api(app)


class Index(Resource):
    """The author API to be able to retrieve authors"""

    def get(self):
        return {'time': str(datetime.now())}


# Add our api resource routes

api.add_resource(Index, '/')  # Route_1

# Run the application if running as a script

if __name__ == '__main__':
    # Start the flask webserver
    app.run(port=FLASK_PORT)
