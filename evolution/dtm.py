from common.database import DataBase

db = DataBase('../dataset/database.sqlite')
docs = db.get_all()

texts = [d[1]['paper_text'] for d in docs.items()]

