from datetime import datetime

from flask_restful import Resource


class Index(Resource):
    """The author API to be able to retrieve authors"""

    def get(self):
        return {'time': str(datetime.now())}
