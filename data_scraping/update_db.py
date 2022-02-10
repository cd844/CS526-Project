import csv
import requests
import pprint
import json
import time
import sqlite3
import repo_lookup as rl

import load_bq_titles as lb
from requests.auth import HTTPBasicAuth


#token = put your pa token here

pp = pprint.PrettyPrinter(indent = 4)

insert_query='''INSERT INTO repos(name, description, languages, forks, topics, contributors, created, updated, pushed, size, branches, license, watchers) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

def get_unretrieved(master, db_list, file404='404.txt'):
    unretrieved_set = set(master) - set(db_list)
    unretrieved = [repo for repo in unretrieved_set]
    return unretrieved


def main():
    tokens = json.load(open('tokens.json'))
    lookup = rl.RepoLookup()
    dbfile = 'repos.db'
    for tok in tokens:
        lookup.tokens.append(tok)
    with open("bq-results-20220203-212826-iq0do5yddqd.csv") as csvfile:
        next(csvfile)
        master = set([line.strip() for line in csvfile])
    
    print(len(master))
    con = sqlite3.connect(dbfile)
    cur = con.cursor()

    i = 0
    count = 0
    max = 10000
    rows = cur.execute("SELECT NAME FROM repos")
    retrieved = set([row[0] for row in rows])
    unretrieved = get_unretrieved(master, retrieved)

    with open("bq-results-20220203-212826-iq0do5yddqd.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        rows = []
        next(reader)
        #traverse list until find name not in row
        skipped_repos = open("missing_repos","a")

        while count < max:
            #print(name)
            #rows = cur.execute("SELECT COUNT(*) FROM repos WHERE name=?", (name,))
            #present = next(rows)[0] > 0
            name = unretrieved[i]
            code, row = lookup.get_attributes(name)
            print(f'{i}: {name} res={code}')
            if code == 0: # no valid tokens, wait
                time.sleep(600)
            elif(row != None):
                #pp.pprint(row)
                cur.execute(insert_query,(row['name'], row['description'], row['languages'], 
                    row['forks'], row['topics'], row['contributors'], row['created'], row['updated'], row['pushed'], row['size'], row['branches'], row['license'], row['watchers']))
                con.commit()
                count += 1
                i+=1
            elif code == 403: #api limit, wait ten minutes
                time.sleep(600)
            else:
                print(f"code:{code}, skipping") 
                skipped_repos.write(f"{name}\n")
                name = next(reader)[0]
                i+=1
                    
            if count > max:
                break
        print(count)
    return
    """
    with open("bq-results-20220203-212826-iq0do5yddqd.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        rows = []
        next(reader)
        #traverse list until find name not in row

        while count < max:
            #print(name)
            rows = cur.execute("SELECT COUNT(*) FROM repos WHERE name=?", (name,))
            present = next(rows)[0] > 0
            if(not present):
                code, row = lookup.get_attributes(name)
                print(f'{i}: {name} res={code}')
                if code == 0: # no valid tokens, wait
                    time.sleep(600)
                elif(row != None):
                    #pp.pprint(row)
                    cur.execute(insert_query,(row['name'], row['description'], row['languages'], 
                        row['forks'], row['topics'], row['contributors'], row['created'], row['updated'], row['pushed'], row['size'], row['branches'], row['license'], row['watchers']))
                    con.commit()
                    count += 1
                    name = next(reader)[0]
                    i+=1
                elif code == 403: #api limit, wait ten minutes
                    time.sleep(600)
                else:
                    print(f"code:{code}, skipping") 
                    name = next(reader)[0]
                    i+=1
            else:
                name = next(reader)[0]
                    
            if count > max:
                break
        print(count)
    """

if __name__=="__main__":
    main()
    