import sqlite3
import datetime as dt
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
        """
        Example Row:
        name                                     ahoarau/ethercat-drivers
        description     r8169 EtherCAT driver for IgH EtherCAT Master ...
        languages                                          {'C': 1062292}
        forks                                                          21
        topics                                                         []
        contributors    [{'login': 'ahoarau', 'id': 703240, 'node_id':...
        created                                      2014-09-03T13:25:39Z
        updated                                      2021-03-08T12:15:18Z
        pushed                                       2014-10-30T14:41:20Z
        size                                                          472
        branches        [[{"name": "gh-pages", "commit": {"sha": "9ab6...
        license         {"key": "gpl-2.0", "name": "GNU General Public...
        watchers                                                       16
        """
        con = sqlite3.connect(self.connection_def)
        cur = con.cursor()

        query_s = "SELECT * FROM repos"
        if where != None:
            query_s += f" WHERE {where}"
        query_s += " LIMIT (?) OFFSET (?)"

        if(self.debug):
            print(query_s)
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
        df['languages'] = df['languages'].apply(lambda x : json.loads(x))
        #df['contributors'] = df['contributors'].apply(lambda x : json.loads(x)[0])
        return df

def main():
    print("Test db")
    db_path = './data/new_repos.db'
    db_type = 'sqlite'
    db = DatabaseInterface(db_path, db_type)
    
    df = db.db_to_dataframe(100)
    print(df.columns)
    print(df)


if __name__=='__main__':
    main()