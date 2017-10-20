import logging
import os

from TopicModeling.server import TopicsServer

if __name__ == '__main__':
    # Config for logging
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    # Start the server
    t = TopicsServer()
    t.init_flask_server(os.environ.get('DEBUG', True))
