import database as data

db_path = './data/new_repos.db'
db_type = 'sqlite'
db = data.DatabaseInterface(db_path, db_type)
db.debug = True