import sqlite3
import datetime as dt
import numpy as np
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
        
    def db_to_dataframe(self, limit = 100000, offset = 0, where = None, order_by_col = None, order_by_desc = True):
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
        if order_by_col != None:
            query_s += f" ORDER BY {order_by_col} { 'DESC' if order_by_desc else 'ASC' }"
        query_s += " LIMIT (?) OFFSET (?)"

        if(self.debug):
            con.set_trace_callback(print)
        rows = cur.execute(query_s, (limit, offset))
        con.set_trace_callback(None)

        attributes = [description[0] for description in cur.description]
        data = dict()
        for a in attributes:
            data[a] = [] # preallocating would be a better optimization
        

        for r in rows:
            for i, a in enumerate(attributes):
                data[a].append(r[i])

        df = pd.DataFrame(data)

        ### Data cleaning
        # use this macro to convert json string to dict()
        df['owner'] = df['owner'].apply(lambda x : json.loads(x))
        df['languages'] = df['languages'].apply(lambda x : json.loads(x))
        df['license'] = df['license'].apply(lambda x : json.loads(x))
        df['topics'] = df['topics'].apply(lambda x : json.loads(x))
        df['contributors_count'] = df['contributors_count'].apply(lambda x : 1 if np.isnan(x) else x)
        #df['contributors'] = df['contributors'].apply(lambda x : json.loads(x)[0])
        return df


    def construct_where(self, languages, languages_or, min_watchers):
        and_wheres = []
        if(languages == None or len(languages) > 0):
            if languages_or == False:
                and_wheres.append(' AND '.join([f'languages like "%""{l}""%"' for l in languages]))
            else:
                and_wheres.append(' OR '.join([f'languages like "%""{l}""%"' for l in languages]))
        if(min_watchers != None):
            and_wheres.append(f'watchers_count > {min_watchers}')
        and_wheres = [f'({w})' for w in and_wheres]
        sql = ' AND '.join(and_wheres)
        print(sql)
        return sql

def main():
    print("Test db")
    db_path = './data/new_repos.db'
    db_type = 'sqlite'
    db = DatabaseInterface(db_path, db_type)
    db.debug = True
    
    where = db.construct_where(None, min_watchers=10)
    print(where)
    df = db.db_to_dataframe(10, where = where, order_by_col='watchers_count', order_by_desc=False)
    print(df[['full_name', 'watchers_count']])
    #df = db.db_to_dataframe(10)
    #jfiltered = df[df['topics'].apply(lambda x : len(x) > 0)]
    #print(filtered)
    #filtered.to_csv('filtered_topics.csv')


if __name__=='__main__':
    main()