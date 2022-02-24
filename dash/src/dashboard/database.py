import sqlite3
import pandas as pd
import json
class DatabaseInterface:
    connection_def = None
    connection_type = 'sqlite3'
    debug = False
    def __init__(self, con, con_type = 'sqlite'):
        if(con_type not in ['sqlite']):
            raise Exception('bad db type')
        self.connection_def = con
        self.connection_type = con_type
        
    def db_to_dataframe(self, limit = 100000, offset = 0, where = None):
        con = sqlite3.connect(self.connection_def)
        cur = con.cursor()

        query_s = "SELECT * FROM repos"
        if where != None:
            query_s += f" WHERE {where}"
        query_s += " LIMIT (?) OFFSET (?)"

        if(self.debug):
            print(query_s)
        print(type(offset), type(limit))
        print(offset, limit)
        rows = cur.execute(query_s, (limit, offset))

        attributes = [description[0] for description in cur.description]
        data = dict()
        for a in attributes:
            data[a] = [] # preallocating would be a better optimization

        for r in rows:
            for i, a in enumerate(attributes):
                data[a].append(r[i])

        df = pd.DataFrame(data)
        # use this macro to convert json string to dict()
        df['languages'] = df['languages'].apply(lambda x : json.loads(x)[0])
        df['contributors'] = df['contributors'].apply(lambda x : json.loads(x)[0])
        return df