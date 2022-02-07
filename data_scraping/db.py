import json
import sqlite3
import pprint
pp = pprint.PrettyPrinter(indent = 4)


db_init = '''CREATE TABLE repos 
               (
                id INTEGER PRIMARY KEY, 
                name TEXT NOT NULL,
                description TEXT NULLABLE,
                languages TEXT,
                forks INTEGER,
                topics TEXT NULLABLE,
                contributors TEXT,
                created TEXT,
                updated TEXT,
                pushed TEXT,
                size INTEGER,
                branches TEXT,
                license TEXT,
                watchers INT
                )
                '''

db_drop = ('''DROP TABLE repos''')

def main():
    con = sqlite3.connect('repos.db')
    cur = con.cursor()

    cur.execute(db_drop) 
    cur.execute(db_init) 

    query='''INSERT INTO repos(name, description, languages, forks, topics, contributors, created, updated, pushed, size, branches, license, watchers) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)'''
    count = 0
    with open('bq_results_10000.json', 'r') as f:
        objs = json.load(f)
        for ob in objs:
            #pp.pprint(ob)
            ob['topics'] = json.dumps(ob['topics'])
            cur.execute(query,(ob['name'], ob['description'], ob['languages'], ob['forks'], ob['topics'], ob['contributors'], ob['created'], ob['updated'], ob['pushed'], ob['size'], ob['branches'], ob['license'], ob['watchers']))
            """
            cur.execute(f'''
                        INSERT INTO repos(name, description, languages, forks, topics, 
                        contributors, created, updated, pushed, size,
                        branches, license, watchers) 
                        VALUES ('{ob['name']}', '{ob['description']}', '{ob['languages']}', '{ob['forks']}', '{ob['topics']}',
                        '{ob['contributors']}', '{ob['created']}', '{ob['updated']}', '{ob['pushed']}', '{ob['size']}',
                        '{ob['branches']}', '{ob['license']}', '{ob['watchers']}')
                        ''')
                        """
    con.commit()
    con.close()

if __name__ == "__main__":
    main()