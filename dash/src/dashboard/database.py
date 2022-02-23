import sqlite3
import pandas as pd
import json
class DatabaseInterface:
    connection_def = None
    connection_type = 'sqlite3'
    def __init__(self, con, con_type = 'sqlite'):
        if(con_type not in ['sqlite']):
            raise Exception('bad db type')
        self.connection_def = con
        self.connection_type = con_type
        
    def db_to_dataframe(self, limit = None):
        con = sqlite3.connect(self.connection_def)
        cur = con.cursor()
        if limit == None:
            rows = cur.execute("SELECT * FROM repos")
        else:
            rows = cur.execute("SELECT * FROM repos LIMIT (?)", (limit,))

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