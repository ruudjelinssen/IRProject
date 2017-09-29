import os
from TopicModeling.server import TopicsServer

t = TopicsServer()

if __name__ == '__main__':
    t.init_flask_server(os.environ.get('DEBUG', False))
